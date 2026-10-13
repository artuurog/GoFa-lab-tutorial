"""Minimal newline-delimited TCP protocol helpers for Lesson 02."""

from __future__ import annotations


def encode_command(command: str) -> bytes:
    """Return one protocol line, rejecting embedded line breaks."""
    clean = command.strip()
    if not clean or "\n" in clean or "\r" in clean:
        raise ValueError("A command must be one non-empty line")
    return f"{clean}\n".encode("ascii")


def decode_response(payload: bytes) -> str:
    """Decode one ASCII response line from the robot."""
    text = payload.decode("ascii").strip()
    if not text:
        raise ValueError("The robot returned an empty response")
    return text

