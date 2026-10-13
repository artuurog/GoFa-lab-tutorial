# ABB GoFa Guided Tutorial

A brief introduction to ABB GoFa programming with RobotStudio, RAPID, Python TCP communication, and EGM.

## Learning outcomes

By the end of this tutorial, students will be able to:

1. Run a GoFa virtual controller in RobotStudio and recognize the main motion references.
2. Program and verify simple `MoveJ` and `MoveL` motion in RAPID.
3. Exchange discrete commands and state messages between Python and RAPID over TCP.
4. Run a bounded EGM trajectory in simulation, then repeat the validated procedure on a real robot under instructor supervision.

## Intended use

- Audience: programmers new to ABB robotics.
- Duration: 4–6 hours.
- Language: technical English.
- Teaching format: a linear tutorial. There are no separate exercises.
- Target: ABB GoFa with OmniCore, RobotWare 7.x, and a recent RobotStudio release.

## Tutorial path

| Step | Topic | Estimated time | Result |
| --- | --- | ---: | --- |
| 00 | Setup and safety | 30 min | A virtual controller is ready. |
| 01 | RAPID motion | 60 min | A safe point-to-point sequence runs in simulation. |
| 02 | TCP commands and states | 75 min | Python exchanges newline-delimited messages with RAPID. |
| 03 | EGM guided motion | 90 min | A small bounded trajectory is validated in simulation. |
| 04 | Integrated demonstration | 30 min | TCP selects the demonstration and EGM supplies motion setpoints. |

Read the lessons in order. Do not use the real-robot path until the corresponding simulation path has been completed and signed off by the instructor.

## Repository map

```text
lessons/       Guided student-facing steps
rapid/         RAPID modules, organized by lesson
python/        Small Python scripts and configuration template
robotstudio/   Station setup and instructor-only configuration notes
assets/        Diagrams and screenshots used by the lessons
```

## Safety boundary

This repository is an educational starting point, not a production robot application. Real-robot use requires the checklist in [SAFETY.md](SAFETY.md), validated targets, reduced speed, and instructor supervision.

## Start here

1. Read [Compatibility](COMPATIBILITY.md).
2. Read [Safety](SAFETY.md).
3. Follow [Lesson 00](lessons/00_setup.md).

## Additional resources

1. ABB RAPID manual [PDF](https://library.e.abb.com/public/b227fcd260204c4dbeb8a58f8002fe64/Rapid_instructions.pdf)
1. ABB EGM manual [PDF](https://library.e.abb.com/public/e7938c068b3742a7aead2dc6cbf64cd7/3HAC073318%20AM%20Externally%20Guided%20Motion%20OmniCore-en.pdf?x-sign=RTIyDIT44nlpAGKgL46AN1cKX7GScwgevIho0H2oGCTViphMVDm%2FAPfWDWrpxLoP)