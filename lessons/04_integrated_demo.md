# Lesson 04 — Integrated demonstration

## Goal

Use TCP for control flow and EGM for the motion segment.

## Demonstration sequence

1. Python requests `GET_STATE`.
2. Python requests `SELECT_DEMO EGM_PATH`.
3. RAPID acknowledges the request and enters the ready state.
4. Python starts the bounded EGM trajectory.
5. Python sends `STOP` and confirms the final state.

## Checkpoint

The protocol log shows a clear state transition for each step, and the motion remains inside the instructor-approved envelope.

