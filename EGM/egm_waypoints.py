"""
Minimal EGM example for ABB GoFa (OmniCore): the robot follows a list of waypoints.

Setup:
  1. protoc --python_out=. egm.proto      -> egm_pb2.py (already in this folder)
  2. pip install protobuf
  3. Run this script FIRST, then start the RAPID module EGM_Waypoints on the controller.

The robot (UdpUc client) sends an EgmRobot message every ~4 ms to this script (UDP server).
For every message the script replies with one EgmSensor message containing the target pose.

Edit WAYPOINTS and SEGMENT_TIME below, nothing else is needed.
"""

import socket
import time

import egm_pb2

# ---------------------------------------------------------------- Configuration
UDP_IP = "0.0.0.0"          # listen on all interfaces
UDP_PORT = 6510             # must match the UdpUc device "Local Port" in the controller
RX_TIMEOUT = 5.0            # [s] stop if the robot stops sending
RX_BUFFER = 4096            # [bytes]

# Waypoints: XYZ OFFSETS [mm] from the pose the robot has when EGM starts (orientation kept),
# expressed in wobj0. The path starts at the current pose and visits them in order.
WAYPOINTS = [
    (-200.0, 0.0, 0.0),
    (100.0, 100.0, 0.0),
    (0.0, 100.0, 0.0),
    (0.0, 0.0, 0.0),
]
SEGMENT_TIME = 3.0          # [s] duration of each segment (previous point -> next waypoint)
FINAL_HOLD_TIME = 1.0       # [s] keep sending the last waypoint so the robot converges

PATH = [(0.0, 0.0, 0.0)] + WAYPOINTS
DURATION = len(WAYPOINTS) * SEGMENT_TIME + FINAL_HOLD_TIME


# ---------------------------------------------------------------- Trajectory
def min_jerk(s):
    """Smooth 0->1 profile (zero velocity and acceleration at both ends)."""
    return 10 * s**3 - 15 * s**4 + 6 * s**5


def target_at(start_xyz, t):
    """Target XYZ [mm] at time t [s]; stays on the last waypoint once the path is done."""
    k = min(int(t // SEGMENT_TIME), len(WAYPOINTS) - 1)
    s = min_jerk(min((t - k * SEGMENT_TIME) / SEGMENT_TIME, 1.0))
    p0, p1 = PATH[k], PATH[k + 1]
    return tuple(start_xyz[i] + p0[i] + s * (p1[i] - p0[i]) for i in range(3))


# ---------------------------------------------------------------- EGM messages
def read_pose(data):
    """Parse an EgmRobot message -> (xyz [mm], quaternion (u0,u1,u2,u3))."""
    robot = egm_pb2.EgmRobot()
    robot.ParseFromString(data)
    pose = robot.feedBack.cartesian
    return ((pose.pos.x, pose.pos.y, pose.pos.z),
            (pose.orient.u0, pose.orient.u1, pose.orient.u2, pose.orient.u3))


def build_target_msg(seq, xyz, quat):
    """Build a serialized EgmSensor message with the target pose."""
    msg = egm_pb2.EgmSensor()
    msg.header.seqno = seq
    msg.header.tm = int(time.time() * 1000) & 0xFFFFFFFF
    msg.header.mtype = egm_pb2.EgmHeader.MSGTYPE_CORRECTION

    pose = msg.planned.cartesian
    pose.pos.x, pose.pos.y, pose.pos.z = xyz
    pose.orient.u0, pose.orient.u1, pose.orient.u2, pose.orient.u3 = quat
    return msg.SerializeToString()


# ---------------------------------------------------------------- Main
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.settimeout(RX_TIMEOUT)
    print(f"Waiting for the robot on UDP port {UDP_PORT} ...")

    start_xyz, start_quat, t0 = None, None, None
    seq = 0

    try:
        while True:
            data, robot_addr = sock.recvfrom(RX_BUFFER)
            xyz, quat = read_pose(data)

            # First message: the path is relative to the pose the robot has now
            if start_xyz is None:
                start_xyz, start_quat, t0 = xyz, quat, time.monotonic()
                print(f"Robot connected: {robot_addr}, start pose {start_xyz}")

            t = time.monotonic() - t0
            if t >= DURATION:
                print("Trajectory finished")
                break

            seq += 1
            sock.sendto(build_target_msg(seq, target_at(start_xyz, t), start_quat), robot_addr)

    except socket.timeout:
        print("No data from the robot - exiting")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
