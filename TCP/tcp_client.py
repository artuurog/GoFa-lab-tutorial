"""
Minimal TCP example for ABB GoFa (OmniCore): send waypoints, the robot reaches each with MoveJ.

Setup:
  1. Start the RAPID module TCP_Waypoints on the controller (it waits for a client).
  2. Run this script. It needs only the Python standard library.

For every waypoint the script sends "dx,dy,dz" and waits for the reply "OK" before sending the
next one, so the robot is at the waypoint when the reply arrives.

Edit WAYPOINTS below, nothing else is needed. For a RobotStudio virtual controller run:
    python tcp_client.py --host 127.0.0.1 --port 5000
"""

import argparse
import socket

# ---------------------------------------------------------------- Configuration
ROBOT_HOST = "192.168.125.1"    # must match SERVER_IP in TCP_Waypoints.modx
ROBOT_PORT = 1025               # must match SERVER_PORT in TCP_Waypoints.modx
CONNECT_TIMEOUT = 5.0           # [s] max wait for the connection
REPLY_TIMEOUT = 60.0            # [s] max wait for one move to finish
RX_BUFFER = 1024                # [bytes]

# Waypoints: XYZ OFFSETS [mm] from the home pose of the RAPID module (orientation kept),
# expressed in wobj0. RAPID rejects any offset larger than MAX_OFFSET (300 mm).
WAYPOINTS = [
    (100.0, 0.0, 0.0),
    (100.0, 100.0, 0.0),
    (0.0, 100.0, 0.0),
    (0.0, 0.0, 0.0),
]


# ---------------------------------------------------------------- Communication
def send_waypoint(connection, waypoint):
    """Send one waypoint and block until the robot has reached it."""
    request = ",".join(f"{value:.1f}" for value in waypoint)
    connection.sendall(request.encode("ascii"))

    data = connection.recv(RX_BUFFER)
    if not data:
        raise ConnectionError("Robot closed the TCP connection")
    reply = data.decode("ascii").strip()
    if reply != "OK":
        raise RuntimeError(f"Robot rejected '{request}': {reply}")


def main():
    parser = argparse.ArgumentParser(description="Send waypoints to the RAPID TCP server.")
    parser.add_argument("--host", default=ROBOT_HOST)
    parser.add_argument("--port", default=ROBOT_PORT, type=int)
    args = parser.parse_args()

    with socket.create_connection((args.host, args.port), timeout=CONNECT_TIMEOUT) as connection:
        connection.settimeout(REPLY_TIMEOUT)
        print(f"Connected to {args.host}:{args.port}")

        for index, waypoint in enumerate(WAYPOINTS, start=1):
            print(f"Waypoint {index}/{len(WAYPOINTS)}: {waypoint}")
            send_waypoint(connection, waypoint)

    print("Done.")


if __name__ == "__main__":
    main()
