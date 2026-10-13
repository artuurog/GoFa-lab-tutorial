"""Stream validated teaching poses to Lesson02TcpServer over TCP.

Start the RAPID module first. For a RobotStudio virtual controller on the
same PC, the default endpoint is 127.0.0.1:5000. Use --host and --port only

For real robot controllers, the default endpoint is
    IP address: 192.168.125.1
    port 1025

with instructor-approved real-robot values.
"""

from __future__ import annotations

import argparse
import socket
from collections.abc import Iterable


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5000
RESPONSE_LIMIT = 256

# x, y, z [mm], Rx, Ry, Rz [degrees]
TEACHING_POSES = (
    (-400, 60, 400, 0, 0, 0),
    (-400, 250, 400, 0, 0, 0),
    (-400, 200, 700, 0, 0, 0),
    (-400, 60, 700, 0, 0, 0),
    (-400, 60, 400, 0, 0, 0),
)


def format_pose(pose: Iterable[float]) -> bytes:
    """Encode one RAPID pose request as x,y,z,rx,ry,rz."""
    values = tuple(pose)
    if len(values) != 6:
        raise ValueError("A pose must contain x, y, z, rz, ry, and rx")
    return ",".join(format(value, "g") for value in values).encode("ascii")


def receive_response(connection: socket.socket) -> str:
    """Receive the one response paired with the current request."""
    data = connection.recv(RESPONSE_LIMIT)
    if not data:
        raise ConnectionError("The RAPID server closed the TCP connection")
    return data.decode("ascii").strip()


def send_request(connection: socket.socket, request: bytes) -> str:
    """Send one request and return its paired RAPID response."""
    connection.sendall(request)
    response = receive_response(connection)
    if response.startswith("ERROR"):
        raise RuntimeError(f"RAPID rejected the request: {response}")
    return response


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", default=DEFAULT_PORT, type=int)
    parser.add_argument("--timeout", default=10.0, type=float)
    args = parser.parse_args()

    with socket.create_connection((args.host, args.port), timeout=args.timeout) as connection:
        print(f"Connected to Lesson02TcpServer at {args.host}:{args.port}")
        print(send_request(connection, b"GET_STATE"))

        for index, pose in enumerate(TEACHING_POSES, start=1):
            response = send_request(connection, format_pose(pose))
            print(f"Pose {index}: {response}")

        print(send_request(connection, b"GET_STATE"))


if __name__ == "__main__":
    main()
