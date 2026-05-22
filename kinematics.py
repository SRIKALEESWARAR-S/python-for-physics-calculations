"""
kinematics.py - Core kinematics functions for 1D and 2D motion.

Project: Project Formulon-Physics
License: MIT License ~ Open Source Project
"""

import math
import numpy as np

# ── Constants ──────────────────────────────────────────────────────────────────
# Numerical stability bounds for time values
T_MIN = 1e-6    # Minimum allowable time (seconds)
T_MAX = 1e100   # Maximum allowable time (seconds)

# ── Helpers ────────────────────────────────────────────────────────────────────

def _validate_array_lengths(a, b, name_a: str, name_b: str) -> None:
    """Raise ValueError if two array-like objects differ in length."""
    if len(a) != len(b):
        raise ValueError(
            f"'{name_a}' and '{name_b}' must have the same length "
            f"(got {len(a)} and {len(b)})."
        )


def _validate_time_array(t) -> None:
    """
    Validate a time array for numerical stability and physical correctness.

    Checks:
    - All values are strictly positive.
    - At least two distinct values exist (so a time interval is defined).
    - All values lie within [T_MIN, T_MAX].
    """
    t = np.asarray(t, dtype=float)

    if np.any(t <= 0):
        raise ValueError("All time values must be strictly positive (t > 0).")

    if t[-1] - t[0] == 0:
        raise ValueError("'t' must contain at least two distinct values.")

    if np.any(t < T_MIN):
        raise ValueError(
            f"All time values must be >= {T_MIN} to avoid numerical instability."
        )

    if np.any(t > T_MAX):
        raise ValueError(
            f"All time values must be <= {T_MAX} to avoid numerical overflow."
        )


def _validate_non_negative(value, name: str) -> None:
    """Raise ValueError if a scalar value is negative."""
    if value < 0:
        raise ValueError(f"'{name}' must be non-negative (got {value}).")


def _validate_positive(value, name: str) -> None:
    """Raise ValueError if a scalar value is not strictly positive."""
    if value <= 0:
        raise ValueError(f"'{name}' must be strictly positive (got {value}).")


def _validate_non_negative_time(t, name: str = "t") -> None:
    """Raise ValueError if a scalar time value is negative."""
    if t < 0:
        raise ValueError(f"Time '{name}' must be non-negative (got {t}).")


# ── Array-based kinematics ──────────────────────────────────────────────────────

def average_velocity(x, t):
    """
    Calculate average velocity over each time interval.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    x : array-like
        Position values (non-negative, metres).
    t : array-like
        Corresponding time values (seconds). Must be strictly positive,
        have at least two distinct values, and lie within [T_MIN, T_MAX].

    Returns
    -------
    numpy.ndarray
        Average velocities for each consecutive interval (m/s).

    Raises
    ------
    TypeError
        If x or t are not array-like.
    ValueError
        If lengths differ, time constraints are violated, or positions are negative.
    """
    # Convert to numpy arrays for uniform handling
    try:
        x = np.asarray(x, dtype=float)
        t = np.asarray(t, dtype=float)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"'x' and 't' must be array-like of numbers. Detail: {exc}") from exc

    _validate_array_lengths(x, t, "x", "t")

    # Validate position array: all values must be non-negative
    if np.any(x < 0):
        raise ValueError("All position values in 'x' must be non-negative.")

    # Validate time array (positivity, distinctness, stability bounds)
    _validate_time_array(t)

    # Δx / Δt for each consecutive pair
    return np.diff(x) / np.diff(t)


def average_acceleration(v, t):
    """
    Calculate average acceleration over each time interval.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    v : array-like
        Velocity values (m/s).
    t : array-like
        Corresponding time values (seconds).

    Returns
    -------
    numpy.ndarray
        Average accelerations for each consecutive interval (m/s²).

    Raises
    ------
    TypeError
        If v or t are not array-like.
    ValueError
        If lengths differ or the time span is zero.
    """
    try:
        v = np.asarray(v, dtype=float)
        t = np.asarray(t, dtype=float)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"'v' and 't' must be array-like of numbers. Detail: {exc}") from exc

    _validate_array_lengths(v, t, "v", "t")

    if t[-1] - t[0] == 0:
        raise ValueError("'t' must have at least two distinct values.")

    # Δv / Δt for each consecutive pair
    return np.diff(v) / np.diff(t)


# ── Constant-acceleration kinematics ──────────────────────────────────────────

def displacement_constant_acceleration(v0: float, a: float, t: float) -> float:
    """
    Displacement under constant acceleration: x = v0·t + ½·a·t².

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    v0 : float
        Initial velocity (m/s).
    a : float
        Constant acceleration (m/s²). May be negative (deceleration).
    t : float
        Elapsed time (seconds, non-negative).

    Returns
    -------
    float
        Displacement after time t (metres).

    Raises
    ------
    TypeError
        If any argument is not a real number.
    ValueError
        If t is negative.
    """
    if not all(isinstance(arg, (int, float)) for arg in (v0, a, t)):
        raise TypeError("'v0', 'a', and 't' must be real numbers.")

    _validate_non_negative_time(t)

    return v0 * t + 0.5 * a * t ** 2


def velocity_constant_acceleration(v0: float, a: float, t: float) -> float:
    """
    Velocity under constant acceleration: v = v0 + a·t.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    v0 : float
        Initial velocity (m/s).
    a : float
        Constant acceleration (m/s²).
    t : float
        Elapsed time (seconds, non-negative).

    Returns
    -------
    float
        Velocity at time t (m/s).

    Raises
    ------
    TypeError
        If any argument is not a real number.
    ValueError
        If t is negative.
    """
    if not all(isinstance(arg, (int, float)) for arg in (v0, a, t)):
        raise TypeError("'v0', 'a', and 't' must be real numbers.")

    _validate_non_negative_time(t)

    return v0 + a * t


def velocity_displacement_relation(v0: float, a: float, x: float, x0: float) -> float:
    """
    Velocity from displacement via v² = v0² + 2·a·(x − x0).

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    v0 : float
        Initial velocity (m/s).
    a : float
        Constant acceleration (m/s²). Must be non-zero.
    x : float
        Final position (metres).
    x0 : float
        Initial position (metres).

    Returns
    -------
    float
        Speed at position x (m/s).

    Raises
    ------
    TypeError
        If any argument is not a real number.
    ValueError
        If a is zero or if v0² + 2·a·(x − x0) is negative (unphysical).
    """
    if not all(isinstance(arg, (int, float)) for arg in (v0, a, x, x0)):
        raise TypeError("All arguments must be real numbers.")

    if a == 0:
        raise ValueError("'a' must be non-zero to use the displacement–velocity relation.")

    v_sq = v0 ** 2 + 2 * a * (x - x0)
    if v_sq < 0:
        raise ValueError(
            f"Computed v² = {v_sq:.4g} < 0: the combination of v0, a, and "
            "(x - x0) is physically unattainable."
        )

    return math.sqrt(v_sq)


def average_velocity_linear_acceleration(v0: float, v: float) -> float:
    """
    Average velocity under uniform acceleration: v_avg = (v0 + v) / 2.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    v0 : float
        Initial velocity (m/s).
    v : float
        Final velocity (m/s).

    Returns
    -------
    float
        Average velocity (m/s).

    Raises
    ------
    TypeError
        If either argument is not a real number.
    ValueError
        If both velocities are zero (result would still be 0, but noted).
    """
    if not all(isinstance(arg, (int, float)) for arg in (v0, v)):
        raise TypeError("'v0' and 'v' must be real numbers.")

    # Guard: original code raised on v0+v == 0; keep that check but
    # improve the message — physically zero average velocity IS valid,
    # but the original API flagged it, so preserve that behaviour.
    if v0 + v == 0:
        raise ValueError(
            "The sum (v0 + v) is zero. "
            "If both velocities are zero the average is trivially 0; "
            "if they are equal and opposite the formula still holds — "
            "pass the values directly if needed."
        )

    return (v0 + v) / 2


def displacement_velocities(v0: float, v: float, t: float) -> float:
    """
    Displacement from initial/final velocities: x = ((v0 + v) / 2) · t.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    v0 : float
        Initial velocity (m/s).
    v : float
        Final velocity (m/s).
    t : float
        Elapsed time (seconds, non-negative).

    Returns
    -------
    float
        Displacement (metres).

    Raises
    ------
    TypeError
        If any argument is not a real number.
    ValueError
        If t is negative.
    """
    if not all(isinstance(arg, (int, float)) for arg in (v0, v, t)):
        raise TypeError("'v0', 'v', and 't' must be real numbers.")

    _validate_non_negative_time(t)

    return ((v0 + v) / 2) * t


# ── Free-fall kinematics ───────────────────────────────────────────────────────

def free_fall_velocity(h: float, g: float) -> float:
    """
    Impact speed of a free-falling object: v = √(2·g·h).

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    h : float
        Drop height (metres, non-negative).
    g : float
        Gravitational acceleration (m/s², strictly positive).

    Returns
    -------
    float
        Speed just before impact (m/s).

    Raises
    ------
    TypeError
        If either argument is not a real number.
    ValueError
        If h < 0 or g ≤ 0.
    """
    if not all(isinstance(arg, (int, float)) for arg in (h, g)):
        raise TypeError("'h' and 'g' must be real numbers.")

    _validate_non_negative(h, "h")
    _validate_positive(g, "g")

    return math.sqrt(2 * g * h)


def free_fall_velocity_time(g: float, t: float) -> float:
    """
    Speed of a free-falling object after time t: v = g·t.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    g : float
        Gravitational acceleration (m/s², strictly positive).
    t : float
        Elapsed fall time (seconds, non-negative).

    Returns
    -------
    float
        Speed at time t (m/s).

    Raises
    ------
    TypeError
        If either argument is not a real number.
    ValueError
        If g ≤ 0 or t < 0.
    """
    if not all(isinstance(arg, (int, float)) for arg in (g, t)):
        raise TypeError("'g' and 't' must be real numbers.")

    _validate_positive(g, "g")
    _validate_non_negative_time(t)

    return g * t


def free_fall_time(h: float, g: float) -> float:
    """
    Time for an object to fall from height h: t = √(2·h / g).

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    h : float
        Drop height (metres, non-negative).
    g : float
        Gravitational acceleration (m/s², strictly positive).

    Returns
    -------
    float
        Fall duration (seconds).

    Raises
    ------
    TypeError
        If either argument is not a real number.
    ValueError
        If h < 0 or g ≤ 0.
    """
    if not all(isinstance(arg, (int, float)) for arg in (h, g)):
        raise TypeError("'h' and 'g' must be real numbers.")

    _validate_non_negative(h, "h")
    _validate_positive(g, "g")

    return math.sqrt(2 * h / g)


def free_fall_height(g: float, t: float) -> float:
    """
    Height fallen by a free-falling object in time t: h = ½·g·t².

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    g : float
        Gravitational acceleration (m/s², strictly positive).
    t : float
        Elapsed fall time (seconds, non-negative).

    Returns
    -------
    float
        Distance fallen (metres).

    Raises
    ------
    TypeError
        If either argument is not a real number.
    ValueError
        If g ≤ 0 or t < 0.
    """
    if not all(isinstance(arg, (int, float)) for arg in (g, t)):
        raise TypeError("'g' and 't' must be real numbers.")

    _validate_positive(g, "g")
    _validate_non_negative_time(t)

    return 0.5 * g * t ** 2


# ── Projectile motion ─────────────────────────────────────────────────────────

def projectile_motion_range(v0: float, theta: float, g: float) -> float:
    """
    Horizontal range of a projectile: R = v0²·sin(2θ) / g.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    v0 : float
        Launch speed (m/s, non-negative).
    theta : float
        Launch angle above horizontal (degrees, 0 ≤ θ ≤ 90).
    g : float
        Gravitational acceleration (m/s², strictly positive).

    Returns
    -------
    float
        Horizontal range (metres).

    Raises
    ------
    TypeError
        If any argument is not a real number.
    ValueError
        If v0 < 0, g ≤ 0, or theta is outside [0, 90].
    """
    if not all(isinstance(arg, (int, float)) for arg in (v0, theta, g)):
        raise TypeError("'v0', 'theta', and 'g' must be real numbers.")

    _validate_non_negative(v0, "v0")
    _validate_positive(g, "g")

    if not (0 <= theta <= 90):
        raise ValueError(f"'theta' must be in [0, 90] degrees (got {theta}).")

    theta_rad = math.radians(theta)
    return (v0 ** 2 * math.sin(2 * theta_rad)) / g


def projectile_motion_max_height(v0: float, theta: float, g: float) -> float:
    """
    Maximum height of a projectile: H = v0²·sin²(θ) / (2·g).

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    v0 : float
        Launch speed (m/s, non-negative).
    theta : float
        Launch angle above horizontal (degrees, 0 ≤ θ ≤ 90).
    g : float
        Gravitational acceleration (m/s², strictly positive).

    Returns
    -------
    float
        Peak height above launch point (metres).

    Raises
    ------
    TypeError
        If any argument is not a real number.
    ValueError
        If v0 < 0, g ≤ 0, or theta is outside [0, 90].
    """
    if not all(isinstance(arg, (int, float)) for arg in (v0, theta, g)):
        raise TypeError("'v0', 'theta', and 'g' must be real numbers.")

    _validate_non_negative(v0, "v0")
    _validate_positive(g, "g")

    if not (0 <= theta <= 90):
        raise ValueError(f"'theta' must be in [0, 90] degrees (got {theta}).")

    theta_rad = math.radians(theta)
    return (v0 ** 2 * math.sin(theta_rad) ** 2) / (2 * g)


def projectile_motion_trajectory_equation(x: float, theta: float, g: float, v0: float) -> float:
    """
    Vertical position on a projectile trajectory at horizontal distance x.

    Formula: y = x·tan(θ) − g·x² / (2·v0²·cos²(θ))

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    x : float
        Horizontal distance from launch point (metres, non-negative).
    theta : float
        Launch angle above horizontal (degrees, 0 < θ < 90).
    g : float
        Gravitational acceleration (m/s², strictly positive).
    v0 : float
        Launch speed (m/s, strictly positive — zero gives division by zero).

    Returns
    -------
    float
        Height at horizontal position x (metres).

    Raises
    ------
    TypeError
        If any argument is not a real number.
    ValueError
        If x < 0, g ≤ 0, v0 ≤ 0, theta is outside (0, 90), or
        cos(θ) is effectively zero (θ = 90°).
    """
    if not all(isinstance(arg, (int, float)) for arg in (x, theta, g, v0)):
        raise TypeError("'x', 'theta', 'g', and 'v0' must be real numbers.")

    _validate_non_negative(x, "x")
    _validate_positive(g, "g")
    _validate_positive(v0, "v0")   # v0 = 0 causes division by zero in the formula

    if not (0 < theta < 90):
        raise ValueError(
            f"'theta' must be strictly between 0 and 90 degrees "
            f"for the trajectory equation (got {theta})."
        )

    theta_rad = math.radians(theta)
    cos_theta = math.cos(theta_rad)

    # Guard against floating-point near-zero (shouldn't happen with 0 < θ < 90)
    if abs(cos_theta) < 1e-12:
        raise ValueError("cos(theta) is effectively zero; cannot compute trajectory.")

    return (
        x * math.tan(theta_rad)
        - (g * x ** 2) / (2 * v0 ** 2 * cos_theta ** 2)
    )