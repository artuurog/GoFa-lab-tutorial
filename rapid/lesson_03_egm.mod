MODULE lesson_03_egm
    ! EGM pose guidance for python/egm_trajectory.py (manual 3HAC073319, 5.4.2).
    ! Start the Python script FIRST, then run this program.
    !
    ! Controller prerequisites (instructor):
    !  - RobotWare option "Externally Guided Motion".
    !  - Communication > Transmission Protocol: Name "EGMsensor", Type UDPUC,
    !    Remote Address = PC running the script, Remote Port = --port (6510).
    !  - Motion > External Motion Interface Data: "default" (Level 1).

    VAR egmident egmID1;
    VAR egmstate egmSt1;

    ! Convergence windows (tighter than the EGM default so that the move does
    ! not "converge" while the TCP lags the reference during motion).
    CONST egm_minmax egm_lin:=[-0.2,0.2];   ! mm
    CONST egm_minmax egm_rot:=[-0.5,0.5];   ! degrees

    ! Start fine point. It must lie INSIDE the workspace
    ! X -400..-200, Y 20..300, Z 40..300 (mm). TEACH IT on the real station:
    ! the configuration and orientation below are placeholders.
    PERS robtarget pStart:=[[-340,60,80],[0,0,1,0],[0,0,0,0],
                            [9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! Correction frame and sensor frame: identity, both in the WORLD frame,
    ! so the setpoints sent by Python are absolute world coordinates (mm).
    CONST pose frameId:=[[0,0,0],[1,0,0,0]];

    PROC main()
        ! EGM must start from a fine point (manual 1.1, limitations).
        MoveJ pStart,v100,fine,tool0\WObj:=wobj0;

        EGMReset egmID1;
        EGMGetId egmID1;
        egmSt1:=EGMGetState(egmID1);
        IF egmSt1<=EGM_STATE_CONNECTED THEN
            EGMSetupUC ROB_1,egmID1,"default","EGMsensor"\Pose;
        ENDIF

        EGMActPose egmID1\Tool:=tool0\WObj:=wobj0,frameId,EGM_FRAME_WORLD,
            frameId,EGM_FRAME_WORLD
            \x:=egm_lin\y:=egm_lin\z:=egm_lin
            \rx:=egm_rot\ry:=egm_rot\rz:=egm_rot
            \LpFilter:=20\SampleRate:=4\MaxPosDeviation:=1000;

        ! Returns when the target has been inside the windows for 2 s, i.e.
        ! after Python has driven the whole path and holds the last point.
        EGMRunPose egmID1,EGM_STOP_HOLD\x\y\z\rx\ry\rz
            \CondTime:=2\RampInTime:=0.05;

        EGMReset egmID1;
    ENDPROC
ENDMODULE
