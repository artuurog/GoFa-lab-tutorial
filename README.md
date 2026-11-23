# ABB GoFa Tutorial

A brief introduction to ABB GoFa programming with RobotStudio, RAPID, Python TCP communication, and EGM.

## Learning outcomes

By the end of this tutorial, students will be able to:

1. Run a GoFa virtual controller in RobotStudio and recognize the main motion references.
2. Program and verify simple `MoveJ` and `MoveL` motion in RAPID.
3. Exchange commands and replies between Python and RAPID over TCP.
4. Run a bounded EGM waypoint trajectory in simulation, then repeat the validated procedure on a real robot under instructor supervision.

## Repository map

```text
SAFETY.md                      Safety rules and real-robot checklist
RAPID/                         Minimal RAPID motion example
  motion.mod                   RAPID module: MoveJ/MoveL sequence between pre-programmed targets
TCP/                           Minimal TCP waypoint example
  TCP_Waypoints.modx           RAPID module: receives "dx,dy,dz" offsets and reaches each with MoveJ
  tcp_client.py                Python client (standard library only) that sends the waypoints
EGM/                           Minimal EGM waypoint example
  EGM_Waypoints.modx           RAPID module: EGM position guidance
  egm_waypoints.py             Python UDP server that streams the waypoints to the robot
  egm.proto                    EGM protobuf definition
  egm_pb2.py                   Python bindings generated from egm.proto
```

## Safety boundary

Real-robot use requires the checklist in [SAFETY.md](SAFETY.md), validated targets, reduced speed, and instructor supervision.

## Start here

1. Read [Safety](SAFETY.md).
1. Start with [RAPID/motion.mod](RAPID/motion.mod) in a RobotStudio virtual controller.
1. Continue with the TCP example ([TCP/](TCP/)) and then the EGM example ([EGM/](EGM/)).

## Running the examples

The robtargets and the `gripper` tooldata in the RAPID modules are placeholders: teach or validate them for your cell before use. In the TCP and EGM examples all waypoints are offsets from the robot pose at start.

### RAPID motion

1. Load `RAPID/motion.mod` on the controller (virtual controller first).
1. Run `main`. The robot goes `home` → `approach` (`MoveJ`), `point_a` → `point_b` (`MoveL`), then back to `approach` and `home`, stopping exactly at each target (`fine` zone).

### TCP

1. Load and start `TCP/TCP_Waypoints.modx` on the controller. It waits for a client.
1. Run `python TCP/tcp_client.py`. For a RobotStudio virtual controller use `python TCP/tcp_client.py --host 127.0.0.1 --port 5000`.

The real controller defaults are `192.168.125.1:1025`.

### EGM

Requires the EGM option and a UdpUc device on the controller (remote port 6510).

1. `pip install protobuf`
1. Run `python EGM/egm_waypoints.py` first.
1. Then start `EGM/EGM_Waypoints.modx` on the controller.

## RobotStudio stations

A simple RobotStudio environment station can be found [here](https://github.com/artuurog/ABB_GoFa_socket/tree/main/envs)

## Additional resources

1. ABB RAPID manual [PDF](https://library.e.abb.com/public/b227fcd260204c4dbeb8a58f8002fe64/Rapid_instructions.pdf)
1. ABB EGM manual [PDF](https://library.e.abb.com/public/e7938c068b3742a7aead2dc6cbf64cd7/3HAC073318%20AM%20Externally%20Guided%20Motion%20OmniCore-en.pdf?x-sign=RTIyDIT44nlpAGKgL46AN1cKX7GScwgevIho0H2oGCTViphMVDm%2FAPfWDWrpxLoP)
