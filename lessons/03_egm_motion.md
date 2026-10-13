# Lesson 03 — EGM guided motion

## Goal

Run a small instructor-configured EGM trajectory in simulation.

## Separation of responsibilities

- TCP selects or stops the demonstration and reports state.
- EGM provides bounded motion setpoints only.
- The instructor configures EGM and validates the reference pose before students run the Python script.

## Procedure

1. Read the [instructor EGM configuration guide](../robotstudio/instructor/egm-configuration.md).
2. Verify the reference pose and motion limits in RobotStudio.
3. Copy the validated EGM settings into `python/settings.py`.
4. Read `python/egm_trajectory.py` before running it.
5. Run the trajectory in the virtual controller.
6. Repeat on the real robot only through the instructor’s commissioning procedure.

## Checkpoint

The virtual robot follows the bounded trajectory around the approved reference pose and stops through the approved procedure.

