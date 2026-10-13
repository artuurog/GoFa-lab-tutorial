MODULE Lesson01Motion

    ! Lesson 01: moving between predefined targets with MoveJ and MoveL.
    !
    ! MoveJ: joint motion. Fast, the TCP path is not a straight line.
    !        Use it for large free-space moves.
    ! MoveL: linear motion. The TCP follows a straight line.
    !        Use it when the path matters (approaching or working on a part).
    !
    ! WARNING: the target values below are PLACEHOLDERS. Teach or validate
    ! them in RobotStudio / on the real robot before running, and check that
    ! they are reachable and collision free in your station.

    ! robtarget = [ [x,y,z] (mm), [q1,q2,q3,q4] orientation, [cf1,cf4,cf6,cfx] configuration, external axes ]
    LOCAL CONST robtarget home     := [[-300, 150, 300], [0, 0, 1, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    LOCAL CONST robtarget approach := [[-400, 300, 150], [0, 0, 1, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    LOCAL CONST robtarget point_a  := [[-400, 300, 40],  [0, 0, 1, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    LOCAL CONST robtarget point_b  := [[-200, 10,  40],  [0, 0,_target point_b := [[-2００,
    ! Pause (s) in each reached pose before the next motion.
    LOCAL CONST num pause_time := 1;

    LOCAL PROC main()
        ! Start at home, slowly: first move of a program.
        MoveJ home, v100, fine, tool0;
        WaitTime pause_time;

        ! Large free-space move: MoveJ at high speed.
        ! Every target uses the zone "fine" so the robot stops exactly there
        ! (a zone like z50 would round the corner and skip the stop).
        MoveJ approach, v1000, fine, tool0;
        WaitTime pause_time;

        ! Straight-line descent to the work point at low speed, stop exactly (fine).
        MoveL point_a, v50, fine, tool0;
        WaitTime pause_time;

        ! Straight-line move between the two work points at medium speed.
        MoveL point_b, v200, fine, tool0;
        WaitTime pause_time;

        ! Joint move back up to approach at medium speed.
        MoveJ approach, v500, fine, tool0;
        WaitTime pause_time;

        ! Return home at maximum speed with a straight line.
        MoveL home, vmax, fine, tool0;
        WaitTime pause_time;

        TPWrite "Lesson 01: sequence finished.";
    ENDPROC

ENDMODULE
