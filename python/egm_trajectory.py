"""Run the bounded Lesson 03 Cartesian EGM trajectory.

The RAPID program must already be running EGM pose guidance. The controller
starts the UDP exchange, so this client waits for its first EGM feedback packet
before sending any setpoint.
"""

from __future__ import annotations

import argparse
import math
import time
from typing import Optional, Sequence

import numpy as np
from ABBRobotEGM import EGM

try:
    from settings import (
        EGM_CIRCLE_FREQUENCY_HZ,
        EGM_CIRCLE_RADIUS_MM,
        EGM_DURATION_S,
        EGM_PORT,
        EGM_REFERENCE_ORIENTATION_WXYZ,
        EGM_REFERENCE_POSITION_MM,
    )
except ImportError as error:
    raise SystemExit(
        "Create python/settings.py from python/settings.example.py and enter "
        "the instructor-validated EGM pose-guidance values."
    ) from error


MAX_RADIUS_MM = 5.0
MAX_CONSECUTIVE_MISSES = 3


def vector_from_settings(
    name: str, values: Optional[Sequence[float]], size: int
) -> np.ndarray:
    """Return a finite numeric vector with exactly *size* elements."""
    if values is None:
        raise ValueError(f"{name} is not configured")
    vector = np.asarray(values, dtype=float)
    if vector.shape != (size,) or not np.isfinite(vector).all():
        raise ValueError(f"{name} must contain {size} finite numeric values")
    return vector


def validate_configuration(
    reference_position: np.ndarray,
    orientation: np.ndarray,
    radius_mm: float,
    frequency_hz: float,
    duration_s: float,
) -> None:
    """Reject incomplete or unsafe teaching parameters before opening EGM."""
    quaternion_norm = float(np.linalg.norm(orientation))
    if not math.isclose(quaternion_norm, 1.0, rel_tol=0.0, abs_tol=1e-3):
        raise ValueError("EGM_REFERENCE_ORIENTATION_WXYZ must be a unit quaternion")
    if not 0.0 < radius_mm <= MAX_RADIUS_MM:
        raise ValueError(f"radius must be greater than 0 and at most {MAX_RADIUS_MM} mm")
    if not 0.0 < frequency_hz <= 0.2:
        raise ValueError("frequency must be greater than 0 and at most 0.2 Hz")
    if not 0.0 < duration_s <= 30.0:
        raise ValueError("duration must be greater than 0 and at most 30 seconds")
    if not np.isfinite(reference_position).all():
        raise ValueError("EGM reference position contains an invalid value")


def circle_setpoint(
    reference_position: np.ndarray,
    radius_mm: float,
    frequency_hz: float,
    elapsed_s: float,
) -> np.ndarray:
    """Return a small circle in the YZ plane around the approved reference pose."""
    angle = 2.0 * math.pi * frequency_hz * elapsed_s
    return reference_position + np.array(
        [0.0, radius_mm * math.cos(angle), radius_mm * math.sin(angle)]
    )


def wait_for_first_feedback(egm: EGM, timeout_s: float) -> None:
    """Wait until the configured controller begins EGM pose guidance."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        received, _ = egm.receive_from_robot(timeout=0.25)
        if received:
            return
    raise TimeoutError(
        "No EGM feedback received. Verify that the RAPID EGM pose-guidance "
        "program is running and that the configured UDP port is reachable."
    )


def run_trajectory(
    egm: EGM,
    reference_position: np.ndarray,
    orientation: np.ndarray,
    radius_mm: float,
    frequency_hz: float,
    duration_s: float,
) -> None:
    """Send the bounded setpoints; stop if EGM feedback is lost repeatedly."""
    start_time = time.monotonic()
    missed_feedback = 0

    while time.monotonic() - start_time < duration_s:
        received, _ = egm.receive_from_robot(timeout=0.25)
        if not received:
            missed_feedback += 1
            if missed_feedback >= MAX_CONSECUTIVE_MISSES:
                raise ConnectionError("EGM feedback was lost")
            continue

        missed_feedback = 0
        elapsed_s = time.monotonic() - start_time
        target_position = circle_setpoint(
            reference_position, radius_mm, frequency_hz, elapsed_s
        )
        if not egm.send_to_robot_cart(target_position, orientation):
            raise ConnectionError("Unable to send the EGM Cartesian setpoint")

    # Leave the EGM target at the approved reference pose before closing UDP.
    egm.send_to_robot_cart(reference_position, orientation)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=EGM_PORT)
    parser.add_argument("--radius-mm", type=float, default=EGM_CIRCLE_RADIUS_MM)
    parser.add_argument("--frequency-hz", type=float, default=EGM_CIRCLE_FREQUENCY_HZ)
    parser.add_argument("--duration-s", type=float, default=EGM_DURATION_S)
    parser.add_argument("--wait-timeout-s", type=float, default=10.0)
    args = parser.parse_args()

    reference_position = vector_from_settings(
        "EGM_REFERENCE_POSITION_MM", EGM_REFERENCE_POSITION_MM, 3
    )
    orientation = vector_from_settings(
        "EGM_REFERENCE_ORIENTATION_WXYZ", EGM_REFERENCE_ORIENTATION_WXYZ, 4
    )
    validate_configuration(
        reference_position,
        orientation,
        args.radius_mm,
        args.frequency_hz,
        args.duration_s,
    )

    print(f"Waiting for EGM feedback on UDP port {args.port}...")
    with EGM(port=args.port) as egm:
        wait_for_first_feedback(egm, args.wait_timeout_s)
        print("EGM feedback received; streaming the bounded trajectory.")
        run_trajectory(
            egm,
            reference_position,
            orientation,
            args.radius_mm,
            args.frequency_hz,
            args.duration_s,
        )
    print("Trajectory complete; reference pose sent before UDP close.")


if __name__ == "__main__":
    main()
