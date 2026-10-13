"""Send one guided Lesson 02 command to the approved TCP endpoint."""

from __future__ import annotations

import argparse
import socket

from protocol import decode_response, encode_command
from settings import ROBOT_HOST, TCP_PORT


def receive_line(connection: socket.socket) -> bytes:
    """Read until one newline-delimited protocol response is complete."""
    received = bytearray()
    while not received.endswith(b"\n"):
        chunk = connection.recv(1024)
        if not chunk:
            raise ConnectionError("Robot closed the TCP connection")
        received.extend(chunk)
    return bytes(received)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["GET_STATE", "RUN_SEQUENCE", "STOP"])
    args = parser.parse_args()

    with socket.create_connection((ROBOT_HOST, TCP_PORT), timeout=5) as connection:
        connection.sendall(encode_command(args.command))
        print(decode_response(receive_line(connection)))


if __name__ == "__main__":
    main()

