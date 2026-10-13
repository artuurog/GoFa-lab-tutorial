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
6. The robot is operated only in the approved mode for the lab.

## EGM boundary

EGM setpoints are motion commands. The EGM lesson uses a bounded trajectory around an instructor-validated reference pose. Never substitute unbounded user input, arbitrary coordinates, or production motion logic into the tutorial example.

