# ABB GoFa Tutorial

A brief introduction to ABB GoFa programming with RobotStudio, RAPID, Python TCP communication, and EGM.

## Learning outcomes

By the end of this tutorial, students will be able to:

1. Run a GoFa virtual controller in RobotStudio and recognize the main motion references.
2. Program and verify simple `MoveJ` and `MoveL` motion in RAPID.
3. Exchange discrete commands and state messages between Python and RAPID over TCP.
4. Run a bounded EGM trajectory in simulation, then repeat the validated procedure on a real robot under instructor supervision.

## Tutorial path

| Lesson | Topic | Result |
| --- | --- | --- |
| [00](lessons/00_setup.md) | Setup and safety | A virtual controller is ready. |
| [01](lessons/01_rapid_motion.md) | RAPID motion | A safe point-to-point sequence runs in simulation. |
| [02](lessons/02_tcp_protocol.md) | TCP commands and states | Python exchanges newline-delimited messages with RAPID. |
| [03](lessons/03_egm_motion.md) | EGM guided motion | A small bounded trajectory is validated in simulation. |
| [04](lessons/04_integrated_demo.md) | Integrated demonstration | TCP selects the demonstration and EGM supplies motion setpoints. |

## Repository map

```text
SAFETY.md                    Safety rules and real-robot checklist
lessons/
  00_setup.md                Setup and safety
  01_rapid_motion.md         MoveJ / MoveL motion
  02_tcp_protocol.md         TCP message protocol
  03_egm_motion.md           EGM guided motion
  04_integrated_demo.md      TCP + EGM demonstration
rapid/
  lesson_01_motion.mod       RAPID module: named-position MoveJ/MoveL sequence
  lesson_02_tcp_server.mod   RAPID module: TCP socket server
  lesson_02_python_client.py Python client that streams poses to the TCP server
  lesson_03_egm.mod          RAPID module: EGM motion setup
python/
  protocol.py                Newline-delimited TCP protocol helpers
  tcp_client.py              Sends one command to the RAPID TCP service
  egm_trajectory.py          Bounded Cartesian EGM trajectory (Lesson 03)
  settings.py                Host, port and EGM configuration (instructor-provided values)
  requirements.txt           Python dependencies (EGM client)
```

## Safety boundary

Real-robot use requires the checklist in [SAFETY.md](SAFETY.md), validated targets, reduced speed, and instructor supervision.

## Start here

1. Read [Safety](SAFETY.md).
1. Follow [Lesson 00](lessons/00_setup.md).

## RobotStudio stations

A simple RobotStudio environment station can be found [here](https://github.com/artuurog/ABB_GoFa_socket/tree/main/envs)

## Additional resources

1. ABB RAPID manual [PDF](https://library.e.abb.com/public/b227fcd260204c4dbeb8a58f8002fe64/Rapid_instructions.pdf)
1. ABB EGM manual [PDF](https://library.e.abb.com/public/e7938c068b3742a7aead2dc6cbf64cd7/3HAC073318%20AM%20Externally%20Guided%20Motion%20OmniCore-en.pdf?x-sign=RTIyDIT44nlpAGKgL46AN1cKX7GScwgevIho0H2oGCTViphMVDm%2FAPfWDWrpxLoP)