# Lesson 01 — Simple RAPID motion

## Goal

Run an instructor-validated sequence of named positions in RobotStudio.

## Concept

`MoveJ` is used to reach broad approach positions. `MoveL` is used when the tool path between positions must remain linear. In this tutorial, positions are named to make the sequence readable: `home`, `approach`, `point_a`, and `point_b`.

## Procedure

1. Open [`rapid/lesson_01_motion.mod`](../rapid/lesson_01_motion.mod).
2. Read the comments before loading the module.
3. Import it into the approved virtual controller.
4. Run `main` in simulation.
5. Compare the observed sequence with the source code.
6. For a real robot, complete the [real-robot checklist](../robotstudio/instructor/real-robot-commissioning.md) with the instructor.

## Checkpoint

The robot reaches the instructor-validated points in the expected order and returns to `home`.

