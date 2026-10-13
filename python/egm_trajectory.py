"""Guide the robot along a pre-defined Cartesian path with ABB EGM position guidance.

The path (a few waypoints inside the allowed workspace) is created here and
interpolated here at the EGM sample time (4 ms) with a trapezoidal speed profile
on every segment. The controller runs EGM pose guidance (see
rapid/lesson_03_egm.mod); no MoveL/MoveJ is used for the trajectory itself.

Protocol facts used (ABB application manual "Externally Guided Motion",
3HAC073319-001, chapters 2.3 and 3):
  * UDP + Google Protocol Buffers. This script is the *sensor*, i.e. the UDP
    server: it cannot send anything before the robot's first message.
  * The robot sends an EgmRobot message every 4 ms (default SampleRate); we
    answer each one with exactly one EgmSensor message (phase-locked, as
    recommended in 2.3, so the setpoint stream stays smooth).
  * Pose mode: planned.cartesian = position in mm + quaternion [w,x,y,z],
    expressed in the frame configured by EGMActPose (WORLD here).
  * EGM bypasses path planning: the reference stream must be smooth, because
    "the robot will react quickly to all position references, also faulty ones".

Start this script first, then start the RAPID program: the script waits for
the controller's first packet. No external packages are required; the few
protobuf messages needed are encoded by hand (field numbers from egm.proto,
shipped in RobotWare ...\\utility\\Template\\EGM\\egm.proto).
"""

from __future__ import annotations

import argparse
import math
import socket
import struct
import time
from dataclasses import dataclass
from typing import Iterator, List, Optional, Sequence, Tuple

Vec3 = Tuple[float, float, float]

# --------------------------------------------------------------------------
# Workspace (mm, EGM correction frame = world/base) and the pre-defined path
# --------------------------------------------------------------------------
X_RANGE = (-400.0, -200.0)
Y_RANGE = (20.0, 300.0)
Z_RANGE = (40.0, 300.0)

# Waypoints of the path. Every point lies >= 20 mm inside the workspace box.
WAYPOINTS: List[Vec3] = [
    (-340.0, 60.0, 80.0),
    (-260.0, 60.0, 80.0),
    (-260.0, 260.0, 80.0),
    (-340.0, 260.0, 160.0),
    (-340.0, 260.0, 260.0),
    (-260.0, 60.0, 260.0),
    (-340.0, 60.0, 260.0),
    (-340.0, 60.0, 80.0),
]

SAMPLE_TIME_S = 0.004          # EGM default SampleRate (manual 3.1.1: 4 ms)
MAX_SPEED_LIMIT_MM_S = 100.0   # hard cap on --speed
MAX_STEP_MM = MAX_SPEED_LIMIT_MM_S * SAMPLE_TIME_S * 1.01
MAX_TRACKING_ERROR_MM = 30.0   # |measured - commanded| above this -> abort
MAX_CONSECUTIVE_MISSES = 3     # receive timeouts tolerated
MAX_OVERLOAD_PACKETS = 50      # utilizationRate > 100 % tolerated this long


# --------------------------------------------------------------------------
# Minimal protobuf codec (proto2 wire format) for EgmRobot / EgmSensor
# --------------------------------------------------------------------------
def _varint(value: int) -> bytes:
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def _field_varint(number: int, value: int) -> bytes:
    return _varint(number << 3) + _varint(value)


def _field_double(number: int, value: float) -> bytes:
    return _varint((number << 3) | 1) + struct.pack("<d", value)


def _field_message(number: int, payload: bytes) -> bytes:
    return _varint((number << 3) | 2) + _varint(len(payload)) + payload


def _read_varint(buf: bytes, pos: int) -> Tuple[int, int]:
    result = shift = 0
    while True:
        byte = buf[pos]
        pos += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return result, pos
        shift += 7


def _fields(buf: bytes) -> Iterator[Tuple[int, int, object]]:
    """Yield (field number, wire type, value); unknown fields are skipped by callers."""
    pos = 0
    while pos < len(buf):
        key, pos = _read_varint(buf, pos)
        number, wire = key >> 3, key & 7
        if wire == 0:
            value, pos = _read_varint(buf, pos)
        elif wire == 1:
            value, pos = buf[pos:pos + 8], pos + 8
        elif wire == 2:
            length, pos = _read_varint(buf, pos)
            value, pos = buf[pos:pos + length], pos + length
        elif wire == 5:
            value, pos = buf[pos:pos + 4], pos + 4
        else:
            raise ValueError(f"unsupported protobuf wire type {wire}")
        yield number, wire, value


def _first(buf: bytes, number: int) -> Optional[object]:
    for field, _, value in _fields(buf):
        if field == number:
            return value
    return None


def encode_sensor_message(
    seqno: int, time_ms: int, position: Vec3, quaternion: Sequence[float]
) -> bytes:
    """EgmSensor{header{seqno,tm,mtype=CORRECTION}, planned{cartesian{pos,orient}}}."""
    header = (
        _field_varint(1, seqno)
        + _field_varint(2, time_ms & 0xFFFFFFFF)
        + _field_varint(3, 3)  # MSGTYPE_CORRECTION, required from the sensor
    )
    pos = b"".join(_field_double(i + 1, v) for i, v in enumerate(position))
    orient = b"".join(_field_double(i + 1, v) for i, v in enumerate(quaternion))
    cartesian = _field_message(1, pos) + _field_message(2, orient)
    planned = _field_message(2, cartesian)
    return _field_message(1, header) + _field_message(2, planned)


@dataclass
class RobotState:
    position: Vec3
    quaternion: Tuple[float, float, float, float]  # w, x, y, z
    motors_on: Optional[bool]
    rapid_running: Optional[bool]
    convergence_met: Optional[bool]
    utilization: Optional[float]


def decode_robot_message(data: bytes) -> RobotState:
    """Decode EgmRobot. Optional/unknown fields are tolerated (manual 3.1.3)."""
    feedback = _first(data, 2)
    cartesian = _first(feedback, 2) if feedback is not None else None
    if cartesian is None:
        raise ValueError("EgmRobot message has no feedBack.cartesian")
    pos_raw, orient_raw = _first(cartesian, 1), _first(cartesian, 2)
    if pos_raw is None or orient_raw is None:
        raise ValueError("feedBack.cartesian lacks position or quaternion")
    position = tuple(
        struct.unpack("<d", v)[0]
        for n in (1, 2, 3)
        for v in [_first(pos_raw, n)]
    )
    quaternion = tuple(
        struct.unpack("<d", v)[0]
        for n in (1, 2, 3, 4)
        for v in [_first(orient_raw, n)]
    )

    motor = _first(data, 4)
    rapid = _first(data, 8)
    convergence = _first(data, 6)
    utilization = _first(data, 10)
    motor_state = _first(motor, 1) if motor is not None else None
    rapid_state = _first(rapid, 1) if rapid is not None else None
    return RobotState(
        position=position,  # type: ignore[arg-type]
        quaternion=quaternion,  # type: ignore[arg-type]
        motors_on=None if motor_state is None else motor_state == 1,
        rapid_running=None if rapid_state is None else rapid_state == 2,
        convergence_met=None if convergence is None else bool(convergence),
        utilization=None if utilization is None
        else struct.unpack("<d", utilization)[0],
    )


# --------------------------------------------------------------------------
# Trajectory generation and interpolation
# --------------------------------------------------------------------------
def in_workspace(p: Vec3) -> bool:
    return (
        X_RANGE[0] <= p[0] <= X_RANGE[1]
        and Y_RANGE[0] <= p[1] <= Y_RANGE[1]
        and Z_RANGE[0] <= p[2] <= Z_RANGE[1]
    )


def _distance(a: Vec3, b: Vec3) -> float:
    return math.dist(a, b)


def _trapezoid_distance(t: float, length: float, v_max: float, accel: float) -> float:
    """Distance travelled after t seconds, starting and ending at rest."""
    if length <= 0.0:
        return 0.0
    v_peak = min(v_max, math.sqrt(accel * length))
    t_acc = v_peak / accel
    d_acc = 0.5 * accel * t_acc ** 2
    t_cruise = (length - 2.0 * d_acc) / v_peak
    t_total = 2.0 * t_acc + t_cruise
    if t >= t_total:
        return length
    if t < t_acc:
        return 0.5 * accel * t * t
    if t < t_acc + t_cruise:
        return d_acc + v_peak * (t - t_acc)
    td = t_total - t
    return length - 0.5 * accel * td * td


def interpolate_segment(
    start: Vec3, end: Vec3, v_max: float, accel: float
) -> List[Vec3]:
    """Linear segment sampled every SAMPLE_TIME_S with a trapezoidal speed profile."""
    length = _distance(start, end)
    if length < 1e-9:
        return []
    v_peak = min(v_max, math.sqrt(accel * length))
    t_total = 2.0 * v_peak / accel + (length - v_peak ** 2 / accel) / v_peak
    steps = math.ceil(t_total / SAMPLE_TIME_S)
    unit = tuple((e - s) / length for s, e in zip(start, end))
    points: List[Vec3] = []
    for k in range(1, steps + 1):
        d = _trapezoid_distance(k * SAMPLE_TIME_S, length, v_max, accel)
        points.append(tuple(s + u * d for s, u in zip(start, unit)))  # type: ignore[arg-type]
    points[-1] = end  # land exactly on the waypoint
    return points


def build_trajectory(
    start: Vec3, waypoints: Sequence[Vec3], v_max: float, accel: float
) -> List[Vec3]:
    """Approach move from the robot's current position, then the waypoint path."""
    trajectory: List[Vec3] = []
    previous = start
    for waypoint in waypoints:
        trajectory.extend(interpolate_segment(previous, waypoint, v_max, accel))
        previous = waypoint
    return trajectory


def validate_trajectory(trajectory: Sequence[Vec3]) -> None:
    """Refuse to start if any setpoint leaves the workspace or jumps too far."""
    previous = trajectory[0]
    for index, point in enumerate(trajectory):
        if not in_workspace(point):
            raise ValueError(f"setpoint {index} {point} is outside the workspace")
        if _distance(previous, point) > MAX_STEP_MM:
            raise ValueError(f"setpoint {index} jumps more than {MAX_STEP_MM:.2f} mm")
        previous = point


# --------------------------------------------------------------------------
# EGM sensor (UDP server)
# --------------------------------------------------------------------------
class EgmSensor:
    def __init__(self, port: int) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(("0.0.0.0", port))
        self._robot: Optional[Tuple[str, int]] = None
        self._seqno = 0
        self._t0 = time.monotonic()

    def __enter__(self) -> "EgmSensor":
        return self

    def __exit__(self, *exc: object) -> None:
        self._sock.close()

    def receive(self, timeout_s: float) -> Optional[RobotState]:
        self._sock.settimeout(timeout_s)
        try:
            data, address = self._sock.recvfrom(4096)
        except (socket.timeout, ConnectionResetError):  # Windows ICMP reset
            return None
        self._robot = address  # reply to whoever the controller is
        return decode_robot_message(data)

    def send(self, position: Vec3, quaternion: Sequence[float]) -> None:
        if self._robot is None:
            raise RuntimeError("cannot send before the robot's first message")
        if not in_workspace(position):
            raise ValueError(f"refusing to send {position}: outside the workspace")
        self._seqno += 1
        elapsed_ms = int((time.monotonic() - self._t0) * 1000)
        self._sock.sendto(
            encode_sensor_message(self._seqno, elapsed_ms, position, quaternion),
            self._robot,
        )


def wait_for_first_feedback(sensor: EgmSensor, timeout_s: float) -> RobotState:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        state = sensor.receive(0.25)
        if state is not None:
            return state
    raise TimeoutError(
        "No EGM message received. Start the RAPID EGM program and check the "
        "UdpUc device (Remote Address = this PC, Remote Port = --port)."
    )


def check_state(state: RobotState, commanded: Vec3) -> None:
    if state.motors_on is False:
        raise RuntimeError("Motors are off; stopping")
    if state.rapid_running is False:
        raise RuntimeError("RAPID is not running; stopping")
    error = _distance(state.position, commanded)
    if error > MAX_TRACKING_ERROR_MM:
        raise RuntimeError(f"Tracking error {error:.1f} mm exceeds limit; stopping")


def run(
    sensor: EgmSensor, first: RobotState, waypoints: Sequence[Vec3],
    speed: float, accel: float, hold_timeout_s: float,
) -> None:
    start = first.position
    if not in_workspace(start):
        raise ValueError(
            f"Robot start position {tuple(round(v, 1) for v in start)} is outside the "
            "workspace; jog/MoveJ the robot into the box before running EGM"
        )
    orientation = first.quaternion  # held constant for the whole path
    trajectory = build_trajectory(start, waypoints, speed, accel)
    validate_trajectory(trajectory)
    duration = len(trajectory) * SAMPLE_TIME_S
    print(f"{len(trajectory)} setpoints, about {duration:.1f} s. Streaming...")

    commanded: Vec3 = start
    state: Optional[RobotState] = first
    index = 0
    misses = overload = 0
    # Answer the packet we already hold, then one setpoint per received packet.
    while index < len(trajectory):
        if state is None:
            misses += 1
            if misses >= MAX_CONSECUTIVE_MISSES:
                raise ConnectionError("EGM feedback was lost")
            state = sensor.receive(0.25)
            continue
        misses = 0
        check_state(state, commanded)
        if state.utilization is not None and state.utilization > 100.0:
            overload += 1
            if overload >= MAX_OVERLOAD_PACKETS:
                raise RuntimeError("Robot cannot follow the reference (utilization > 100 %)")
        else:
            overload = 0
        commanded = trajectory[index]
        sensor.send(commanded, orientation)
        index += 1
        state = sensor.receive(0.25)

    # Keep sending the last point until the controller reports convergence
    # (EGMRunPose waits for it) or ends the EGM movement and stops streaming.
    print("Path finished; holding final point until EGM converges.")
    deadline = time.monotonic() + hold_timeout_s
    while time.monotonic() < deadline:
        sensor.send(commanded, orientation)
        state = sensor.receive(0.25)
        if state is None:
            print("Controller stopped streaming (EGM movement ended).")
            return
        if state.convergence_met:
            print("Convergence criteria met.")
            return
    raise TimeoutError("Final point did not converge in time")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--port", type=int, default=6510,
                        help="UDP port = RemotePort of the UdpUc device")
    parser.add_argument("--speed", type=float, default=40.0,
                        help="TCP cruise speed in mm/s (max %(default)s default)")
    parser.add_argument("--accel", type=float, default=80.0, help="mm/s^2")
    parser.add_argument("--wait-timeout-s", type=float, default=60.0)
    parser.add_argument("--hold-timeout-s", type=float, default=10.0)
    args = parser.parse_args()

    if not 0.0 < args.speed <= MAX_SPEED_LIMIT_MM_S:
        raise SystemExit(f"--speed must be in (0, {MAX_SPEED_LIMIT_MM_S}] mm/s")
    if not 0.0 < args.accel <= 500.0:
        raise SystemExit("--accel must be in (0, 500] mm/s^2")
    bad = [w for w in WAYPOINTS if not in_workspace(w)]
    if bad:
        raise SystemExit(f"Waypoints outside the workspace: {bad}")

    print(f"Waiting for the controller on UDP port {args.port}...")
    with EgmSensor(args.port) as sensor:
        first = wait_for_first_feedback(sensor, args.wait_timeout_s)
        print("First EGM message received; start =",
              tuple(round(v, 1) for v in first.position))
        run(sensor, first, WAYPOINTS, args.speed, args.accel, args.hold_timeout_s)
    print("Done.")


if __name__ == "__main__":
    main()
