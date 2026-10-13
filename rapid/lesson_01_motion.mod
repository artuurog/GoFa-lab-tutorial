MODULE Lesson01Motion

    ! This is a teaching template. The instructor must replace all targets
    ! with positions validated for the specific virtual or real station.

    LOCAL PROC main()
        ! Example sequence to explain in RobotStudio:
        MoveJ home, v100, z50, tool0;
        WaitTime \InPos 1;
        MoveJ approach, v100, z50, tool0;
        WaitTime \InPos 1;
        MoveL point_a, v50, fine, tool0;
        WaitTime \InPos 1;
        MoveL point_b, v50, fine, tool0;
        WaitTime \InPos 1;
        MoveJ home, v100, z50, tool0;
        TPWrite "Lesson 01: targets must be configured by the instructor.";
    ENDPROC

ENDMODULE

