MODULE Lesson01Motion

    ! Lesson 01: minimal example, moving between pre-programmed targets.
    !
    ! MoveJ: joint motion. The TCP path is not a straight line.
    !        Use it for free-space moves.
    ! MoveL: linear motion. The TCP follows a straight line.
    !        Use it when approaching or working on a part.
    !
    ! WARNING: the target values below are PLACEHOLDERS. Teach or validate
    ! them in RobotStudio / on the real robot before running, and check that
    ! they are reachable and collision free in your station.

    ! robtarget = [ [x,y,z] (mm), [q1,q2,q3,q4] orientation, [cf1,cf4,cf6,cfx] configuration, external axes ]
    LOCAL CONST robtargethome     := [[-300, 150, 300], [0, 0, 1, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    LOCAL CONST robtargetapproach := [[-400, 300, 190], [0, 0, 1, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    LOCAL CONST robtargetpoint_a  := [[-400, 300, 140],  [0, 0, 1, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    LOCAL CONST robtargetpoint_b  := [[-200, 10,  140],  [0, 0, 1, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    LOCAL PERS tooldata gripper:=[TRUE,[[0,0,117.85],[0.966,0,0,0.259]],[0.59,[0.15,0.01,57.98],[1,0,0,0],0,0,0]];


    LOCAL PROC main()
        ! Every move uses the zone "fine": the robot stops exactly at each
        ! target (a zone like z50 would round the corner instead).

        ! Joint moves in free space.
        MoveJ home, v100, fine, gripper;
        MoveJ approach, v500, fine, gripper;

        ! Straight-line moves at the work height, slowly.
        MoveL point_a, v50, fine, gripper;
        MoveL point_b, v100, fine, gripper;

        ! Back up and home.
        MoveL approach, v100, fine, gripper;
        MoveJ home, v500, fine, gripper;

        TPWrite "Lesson 01: sequence finished.";
    ENDPROC

ENDMODULE
