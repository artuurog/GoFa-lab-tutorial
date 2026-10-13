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
4. Load `rapid/lesson_03_egm.mod`, teach `pStart` inside the workspace, and configure the UdpUc device (Remote Port = script `--port`).
5. Run `python python/egm_trajectory.py` (it waits for the controller).
6. Start the RAPID program in simulation.
7. Confirm that the script prints `First EGM message received` and then streams the path.
8. Repeat on the real robot only through the instructor’s commissioning procedure.

## Python trajectory

`egm_trajectory.py` is the EGM sensor (UDP server, no external packages). Start
it first; it waits for the controller's first packet, then answers every 4 ms
packet with one setpoint. It interpolates a pre-defined waypoint path linearly
with a trapezoidal speed profile (default 40 mm/s, 80 mm/s²) and holds the
orientation reported by the robot. All setpoints must stay inside
X −400…−200, Y 20…300, Z 40…300 mm (world frame); the robot's start position
must also be inside this box (`rapid/lesson_03_egm.mod`, `pStart`, must be
taught on the station).

The script aborts on lost feedback (3 timeouts), motors off, RAPID stopped,
tracking error above 30 mm, or sustained `utilizationRate` above 100 %. It
does not configure EGM: that is done by `rapid/lesson_03_egm.mod` and the
instructor's RobotStudio configuration. Run: `python python/egm_trajectory.py --port 6510`.

## Checkpoint

The virtual robot follows the bounded trajectory around the approved reference pose and stops through the approved procedure.

