MODULE Lesson02TcpServer

    ! Protocol: PC -> robot: GET_STATE | STOP | x,y,z,rx,ry,rz
    !           robot -> PC: STATE <value> | OK | ERROR <reason>
    ! Send one request and wait for one response before sending the next one.
    ! STOP is read only between completed MoveL instructions. It is not an
    ! emergency-stop mechanism and must never replace the approved safety stop.

    ! For virtual controller
    CONST string SERVER_IP := "127.0.0.1";
    CONST num SERVER_PORT := 5000;

    ! For real Omnicore controller
    CONST string SERVER_IP := "192.168.125.1";
    CONST num SERVER_PORT := 1025;

    ! The supplied Python demonstration uses this bounded teaching envelope.
    ! The instructor must validate it for the actual tool, workobject, and cell.
    CONST num X_MIN := -500;
    CONST num X_MAX := -300;
    CONST num Y_MIN := 0;
    CONST num Y_MAX := 300;
    CONST num Z_MIN := 350;
    CONST num Z_MAX := 750;

    PERS string tcp_state := "IDLE";

    PROC main()
        VAR socketdev server_socket;
        VAR socketdev client_socket;
        VAR string client_ip;

        TPWrite "Lesson 02: creating TCP server.";
        SocketCreate server_socket;
        SocketBind server_socket,SERVER_IP,SERVER_PORT;
        SocketListen server_socket;
        TPWrite "TCP server ready.";

        WHILE TRUE DO
            TPWrite "Waiting for a Python client.";
            SocketAccept server_socket,client_socket\ClientAddress:=client_ip;
            TPWrite "Client connected: "+client_ip;
            ServeClient client_socket;
            TPWrite "Client disconnected.";
        ENDWHILE
    ENDPROC

    PROC ServeClient(VAR socketdev client_socket)
        VAR string request;

        tcp_state := "IDLE";
        WHILE TRUE DO
            SocketReceive client_socket\Str:=request\Time:=WAIT_MAX;
            HandleRequest client_socket,request;
        ENDWHILE
    ERROR
        IF ERRNO=ERR_SOCK_CLOSED THEN
            tcp_state := "IDLE";
            RETURN;
        ELSE
            tcp_state := "ERROR";
            RETURN;
        ENDIF
    ENDPROC

    PROC HandleRequest(VAR socketdev client_socket, string request)
        VAR robtarget target;

        IF request="GET_STATE" THEN
            SocketSend client_socket\Str:="STATE "+tcp_state;
        ELSEIF request="STOP" THEN
            StopMove;
            tcp_state := "IDLE";
            SocketSend client_socket\Str:="OK";
        ELSEIF ParsePose(request,target) THEN
            IF IsInsideTeachingEnvelope(target) THEN
                tcp_state := "MOVING";
                MoveL target,v50,fine,tool0\WObj:=wobj0;
                tcp_state := "IDLE";
                SocketSend client_socket\Str:="OK";
            ELSE
                SocketSend client_socket\Str:="ERROR OUT_OF_RANGE";
            ENDIF
        ELSE
            SocketSend client_socket\Str:="ERROR INVALID_REQUEST";
        ENDIF
    ERROR
        tcp_state := "ERROR";
        SocketSend client_socket\Str:="ERROR RAPID";
    ENDPROC

    FUNC bool ParsePose(string request, VAR robtarget target)
        VAR string token;
        VAR num start_pos;
        VAR num comma_pos;
        VAR num x;
        VAR num y;
        VAR num z;
        VAR num rx;
        VAR num ry;
        VAR num rz;

        start_pos := 1;
        IF NOT ReadNextNumber(request,start_pos,x) THEN
            RETURN FALSE;
        ENDIF
        IF NOT ReadNextNumber(request,start_pos,y) THEN
            RETURN FALSE;
        ENDIF
        IF NOT ReadNextNumber(request,start_pos,z) THEN
            RETURN FALSE;
        ENDIF
        IF NOT ReadNextNumber(request,start_pos,rx) THEN
            RETURN FALSE;
        ENDIF
        IF NOT ReadNextNumber(request,start_pos,ry) THEN
            RETURN FALSE;
        ENDIF

        token := StrPart(request,start_pos,StrLen(request)-start_pos+1);
        comma_pos := StrFind(token,1,",");
        IF comma_pos<>0 THEN
            RETURN FALSE;
        ENDIF
        IF NOT StrToVal(token,rz) THEN
            RETURN FALSE;
        ENDIF

        target := CRobT(\Tool:=tool0\WObj:=wobj0);
        target.trans := [x,y,z];
        target.rot := OrientZYX(rz,ry,rx);
        RETURN TRUE;
    ENDFUNC

    FUNC bool ReadNextNumber(string request, VAR num start_pos, VAR num value)
        VAR num comma_pos;
        VAR string token;

        comma_pos := StrFind(request,start_pos,",");
        IF comma_pos=0 THEN
            RETURN FALSE;
        ENDIF
        token := StrPart(request,start_pos,comma_pos-start_pos);
        IF NOT StrToVal(token,value) THEN
            RETURN FALSE;
        ENDIF
        start_pos := comma_pos+1;
        RETURN TRUE;
    ENDFUNC

    FUNC bool IsInsideTeachingEnvelope(robtarget target)
        IF target.trans.x<X_MIN OR target.trans.x>X_MAX THEN
            RETURN FALSE;
        ENDIF
        IF target.trans.y<Y_MIN OR target.trans.y>Y_MAX THEN
            RETURN FALSE;
        ENDIF
        IF target.trans.z<Z_MIN OR target.trans.z>Z_MAX THEN
            RETURN FALSE;
        ENDIF
        RETURN TRUE;
    ENDFUNC

ENDMODULE

