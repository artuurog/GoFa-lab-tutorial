# Lesson 02 — TCP commands and states

## Goal

Exchange a small set of discrete messages between Python and RAPID.

## Message format

Each TCP message is one ASCII line terminated by `\n`.

| Direction | Example | Meaning |
| --- | --- | --- |
| PC → robot | `GET_STATE` | Request the current state. |
| Robot → PC | `STATE IDLE` | Report the state. |
| PC → robot | `RUN_SEQUENCE` | Request the validated RAPID sequence. |
| PC → robot | `STOP` | Request the approved stop path. |
| Robot → PC | `OK` or `ERROR <reason>` | Acknowledge the last command. |

## Procedure

1. Copy `python/settings.example.py` to `python/settings.py` and enter only the instructor-provided simulation values.
2. Read `python/protocol.py` and `python/tcp_client.py`.
3. Import `rapid/lesson_02_tcp_server.mod` after its controller-specific socket settings have been reviewed.
4. Run `python tcp_client.py GET_STATE` against the virtual controller.
5. Confirm the state response before trying `RUN_SEQUENCE`.

## Checkpoint

Python sends `GET_STATE` and prints one valid `STATE ...` line from the RAPID service.

