# Safety and real-robot boundary

## Scope

Every motion example is first verified in RobotStudio. A simulation result is not by itself authorization to run on a physical robot.

## Student rules

Students may change RAPID and Python examples only after careful validation in simulation. They must not change safety settings, network policy, EGM configuration, calibrated tool data, or workobject data without approval.

## Required check before a real-robot run

1. The instructor has approved the station and current configuration.
2. The correct tool and workobject are selected and verified.
3. The programmed targets are known, reachable, and clear of people and obstacles.
4. Speed and motion limits are set for supervised teaching.
5. The same code has completed the simulation path successfully.
6. Be ready to press the red button to stop robot execution.

## EGM boundary

EGM setpoints are motion commands. The robot controller does not validate EGM setpoints before execution, so be sure that the EGM points you are streaming are safe and in the robot range.
