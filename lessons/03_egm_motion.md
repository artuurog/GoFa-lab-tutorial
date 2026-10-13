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
3. Install the Python dependency: `python -m pip install -r python/requirements.txt`.
4. Copy `python/settings.example.py` to `python/settings.py` and enter the validated EGM port, reference position, and quaternion.
5. Start the instructor-approved RAPID program in EGM pose-guidance mode.
6. Run `python python/egm_trajectory.py`.
7. Confirm that the script prints `EGM feedback received` before it sends the bounded circle.
8. Repeat on the real robot only through the instructor’s commissioning procedure.

## Python trajectory

`egm_trajectory.py` waits for the controller’s first UDP packet, then sends a
circle in the YZ plane around `EGM_REFERENCE_POSITION_MM`. The circle has a
maximum radius of 5 mm, fixed orientation, a maximum frequency of 0.2 Hz, and
a maximum duration of 30 seconds. The configured quaternion is `[w,x,y,z]`.

The script aborts when feedback is missing for three consecutive receive
periods and sends the configured reference position once before a normal exit.
It does not start, stop, or configure EGM on the controller: those actions
remain in the instructor-approved RAPID program and RobotStudio configuration.

## Checkpoint

The virtual robot follows the bounded trajectory around the approved reference pose and stops through the approved procedure.

