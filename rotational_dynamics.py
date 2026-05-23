"""
rotational_dynamics.py - Rotational kinematics and dynamics for rigid bodies.

Covers every formula in the specification:

    Kinematics
    ----------
    w  = dtheta/dt          angular velocity (array form)
    alpha = dw/dt           angular acceleration (array form)
    v  = r * w              tangential velocity
    at = r * alpha          tangential acceleration
    ac = v² / r             centripetal acceleration
    fc = m * v² / r         centripetal force

    Constant-alpha analogues of linear kinematics (Big-3 + 2 more)
    ---------------------------------------------------------------
    w  = w0 + alpha*t       (analogue of v = v0 + a*t)
    theta = w0*t + ½*alpha*t²   (analogue of x = v0*t + ½*a*t²)
    w² = w0² + 2*alpha*theta    (analogue of v² = v0² + 2*a*x)
    theta = ½*(w0 + w)*t        (analogue of x = ½*(v0+v)*t)
    theta = w*t - ½*alpha*t²    (analogue of x = v*t - ½*a*t²)

    Torque & Moment of Inertia
    --------------------------
    tau = r * F * sin(theta)    torque (cross-product magnitude)
    I   = m * r²                point-mass moment of inertia
    I   = integral r² dm        continuous-body MOI (numerical)
    I   = I_cm + M * d²         parallel-axis theorem
    Iz  = Ix + Iy               perpendicular-axis theorem

    Angular Momentum & Newton's 2nd Law (rotation)
    -----------------------------------------------
    L   = r * p * sin(theta)    = m*v*r*sin(theta)
    L   = I * w
    tau = dL/dt                 (scalar, finite-difference & array forms)

Project: Project Formulon-Physics
License: MIT License ~ Open Source Project
"""

import math
import numpy as np
from validators import (
    validate, chain, Rule, RULES,
    validate_array_lengths, validate_strictly_increasing,
)

# ── Constants ──────────────────────────────────────────────────────────────────
TWO_PI = 2.0 * math.pi   # Full rotation in radians


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Angular Kinematics (array / instantaneous forms)
# ══════════════════════════════════════════════════════════════════════════════

def angular_velocity(theta, t):
    """
    Compute average angular velocity over each time interval: w = dtheta/dt.

    Discrete analogue of the derivative definition w = dθ/dt, applied
    element-wise over an array of angular positions and timestamps.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    theta : array-like
        Angular positions (radians). Any real values; multi-revolution
        accumulation (theta > 2π) is valid.
    t : array-like
        Corresponding timestamps (seconds). Must be strictly increasing
        and contain at least two elements.

    Returns
    -------
    numpy.ndarray
        Average angular velocity (rad/s) for each consecutive interval.

    Raises
    ------
    TypeError
        If theta or t are not array-like of real numbers.
    ValueError
        If lengths differ or t is not strictly increasing.
    """
    try:
        theta = np.asarray(theta, dtype=float)
        t     = np.asarray(t,     dtype=float)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"'theta' and 't' must be array-like of numbers. Detail: {exc}") from exc

    validate_array_lengths(theta, t, "theta", "t")
    validate_strictly_increasing(t, "t")

    # dtheta / dt for each consecutive pair
    return np.diff(theta) / np.diff(t)


def angular_acceleration(w, t):
    """
    Compute average angular acceleration over each interval: alpha = dw/dt.

    Discrete analogue of alpha = dω/dt.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    w : array-like
        Angular velocity values (rad/s).
    t : array-like
        Corresponding timestamps (seconds, strictly increasing).

    Returns
    -------
    numpy.ndarray
        Average angular acceleration (rad/s²) per interval.

    Raises
    ------
    TypeError
        If w or t are not array-like of real numbers.
    ValueError
        If lengths differ or t is not strictly increasing.
    """
    try:
        w = np.asarray(w, dtype=float)
        t = np.asarray(t, dtype=float)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"'w' and 't' must be array-like of numbers. Detail: {exc}") from exc

    validate_array_lengths(w, t, "w", "t")
    validate_strictly_increasing(t, "t")

    # dw / dt for each consecutive pair
    return np.diff(w) / np.diff(t)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Tangential & Centripetal quantities
# ══════════════════════════════════════════════════════════════════════════════

@validate(r=RULES.RADIUS, w=RULES.ANGULAR_VEL)
def tangential_velocity(r: float, w: float) -> float:
    """
    Tangential speed of a point on a rotating body: v = r * w.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    r : float
        Radius from the axis of rotation (metres, > 0).
    w : float
        Angular velocity (rad/s). Signed; sign encodes direction.

    Returns
    -------
    float
        Tangential speed (m/s). Sign matches w.
    """
    return r * w


@validate(r=RULES.RADIUS, alpha=RULES.ANGULAR_ACC)
def tangential_acceleration(r: float, alpha: float) -> float:
    """
    Tangential acceleration of a point on a rotating body: at = r * alpha.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    r : float
        Radius from the axis of rotation (metres, > 0).
    alpha : float
        Angular acceleration (rad/s²). Signed.

    Returns
    -------
    float
        Tangential acceleration (m/s²). Sign matches alpha.
    """
    return r * alpha


@validate(v=RULES.REAL, r=RULES.RADIUS)
def centripetal_acceleration(v: float, r: float) -> float:
    """
    Centripetal (radial) acceleration directed toward the rotation axis: ac = v² / r.

    Always non-negative; direction (inward) is implicit.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    v : float
        Tangential speed (m/s). Squared, so sign is irrelevant.
    r : float
        Radius from the axis of rotation (metres, > 0).

    Returns
    -------
    float
        Centripetal acceleration (m/s², non-negative).
    """
    return v ** 2 / r


@validate(m=RULES.POSITIVE, v=RULES.REAL, r=RULES.RADIUS)
def centripetal_force(m: float, v: float, r: float) -> float:
    """
    Net centripetal force required to maintain circular motion: Fc = m * v² / r.

    This is the magnitude of the inward force; it is always non-negative.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    m : float
        Mass of the object (kg, > 0).
    v : float
        Tangential speed (m/s).
    r : float
        Radius of circular path (metres, > 0).

    Returns
    -------
    float
        Centripetal force (Newtons, non-negative).
    """
    return m * v ** 2 / r


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Constant-alpha rotational kinematics (Big-5 equations)
# ══════════════════════════════════════════════════════════════════════════════
# These are the direct rotational analogues of the linear kinematic equations.
# Replace: x→theta, v→w, a→alpha.

@validate(w0=RULES.ANGULAR_VEL, alpha=RULES.ANGULAR_ACC, t=RULES.NON_NEG_TIME)
def angular_velocity_at_time(w0: float, alpha: float, t: float) -> float:
    """
    Angular velocity after time t under constant alpha: w = w0 + alpha*t.

    Rotational analogue of v = v0 + a*t.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    w0 : float
        Initial angular velocity (rad/s).
    alpha : float
        Constant angular acceleration (rad/s²).
    t : float
        Elapsed time (seconds, >= 0).

    Returns
    -------
    float
        Angular velocity at time t (rad/s).
    """
    return w0 + alpha * t


@validate(w0=RULES.ANGULAR_VEL, alpha=RULES.ANGULAR_ACC, t=RULES.NON_NEG_TIME)
def angular_displacement_time(w0: float, alpha: float, t: float) -> float:
    """
    Angular displacement under constant alpha: theta = w0*t + ½*alpha*t².

    Rotational analogue of x = v0*t + ½*a*t².

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    w0 : float
        Initial angular velocity (rad/s).
    alpha : float
        Constant angular acceleration (rad/s²).
    t : float
        Elapsed time (seconds, >= 0).

    Returns
    -------
    float
        Angular displacement (radians).
    """
    return w0 * t + 0.5 * alpha * t ** 2


@validate(w0=RULES.ANGULAR_VEL, alpha=RULES.ANGULAR_ACC, theta=RULES.ANGLE_RAD)
def angular_velocity_from_displacement(w0: float, alpha: float, theta: float) -> float:
    """
    Angular velocity from displacement: w² = w0² + 2*alpha*theta  →  w.

    Rotational analogue of v² = v0² + 2*a*x.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    w0 : float
        Initial angular velocity (rad/s).
    alpha : float
        Constant angular acceleration (rad/s²). Must be non-zero unless
        theta = 0 (handled gracefully).
    theta : float
        Angular displacement (radians).

    Returns
    -------
    float
        Angular speed at displacement theta (rad/s).

    Raises
    ------
    ValueError
        If w0² + 2*alpha*theta < 0 (unphysical combination).
    """
    w_sq = w0 ** 2 + 2 * alpha * theta

    # Guard against taking sqrt of a negative number
    if w_sq < 0:
        raise ValueError(
            f"w² = {w_sq:.4g} < 0: the combination of w0={w0}, "
            f"alpha={alpha}, theta={theta} is physically unattainable."
        )

    return math.sqrt(w_sq)


@validate(w0=RULES.ANGULAR_VEL, w=RULES.ANGULAR_VEL, t=RULES.NON_NEG_TIME)
def angular_displacement_avg_velocity(w0: float, w: float, t: float) -> float:
    """
    Angular displacement from average angular velocity: theta = ½*(w0 + w)*t.

    Rotational analogue of x = ½*(v0 + v)*t.
    Valid only under constant angular acceleration.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    w0 : float
        Initial angular velocity (rad/s).
    w : float
        Final angular velocity (rad/s).
    t : float
        Elapsed time (seconds, >= 0).

    Returns
    -------
    float
        Angular displacement (radians).
    """
    return 0.5 * (w0 + w) * t


@validate(w=RULES.ANGULAR_VEL, alpha=RULES.ANGULAR_ACC, t=RULES.NON_NEG_TIME)
def angular_displacement_final_velocity(w: float, alpha: float, t: float) -> float:
    """
    Angular displacement from final velocity: theta = w*t - ½*alpha*t².

    Rotational analogue of x = v*t - ½*a*t².
    Useful when initial angular velocity is unknown.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    w : float
        Final angular velocity (rad/s).
    alpha : float
        Constant angular acceleration (rad/s²).
    t : float
        Elapsed time (seconds, >= 0).

    Returns
    -------
    float
        Angular displacement (radians).
    """
    return w * t - 0.5 * alpha * t ** 2


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Torque
# ══════════════════════════════════════════════════════════════════════════════

@validate(r=RULES.RADIUS, F=RULES.REAL, theta=RULES.CROSS_ANGLE_DEG)
def torque(r: float, F: float, theta: float) -> float:
    """
    Magnitude of torque (cross-product form): tau = r * F * sin(theta).

    Torque is the rotational equivalent of force. The angle theta is
    between the position vector r and the force vector F.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    r : float
        Moment arm — distance from the axis of rotation to the point of
        force application (metres, > 0).
    F : float
        Magnitude of the applied force (Newtons). May be negative to
        indicate opposing direction.
    theta : float
        Angle between r and F vectors (degrees, [0, 180]).
        theta = 90° gives maximum torque; theta = 0° or 180° gives zero.

    Returns
    -------
    float
        Torque magnitude (N·m). Sign matches F.
    """
    theta_rad = math.radians(theta)
    return r * F * math.sin(theta_rad)


@validate(r=RULES.RADIUS, F=RULES.REAL)
def torque_perpendicular(r: float, F: float) -> float:
    """
    Torque when force is perpendicular to moment arm (theta = 90°): tau = r * F.

    Convenience wrapper for the common case where sin(theta) = 1.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    r : float
        Moment arm (metres, > 0).
    F : float
        Applied force magnitude (Newtons).

    Returns
    -------
    float
        Torque (N·m).
    """
    # sin(90°) = 1, so tau = r * F * 1
    return r * F


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Moment of Inertia
# ══════════════════════════════════════════════════════════════════════════════

@validate(m=RULES.POSITIVE, r=RULES.RADIUS)
def moment_of_inertia_point_mass(m: float, r: float) -> float:
    """
    Moment of inertia for a point mass: I = m * r².

    This is the simplest case — a single particle at distance r from the axis.
    For a rigid body, integrate this over all mass elements (see
    moment_of_inertia_continuous below).

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    m : float
        Mass of the point particle (kg, > 0).
    r : float
        Perpendicular distance from the rotation axis (metres, > 0).

    Returns
    -------
    float
        Moment of inertia (kg·m²).
    """
    return m * r ** 2


def moment_of_inertia_continuous(r_values, dm_values):
    """
    Numerical approximation of I = integral(r² dm) for a continuous body.

    Approximates the integral by treating each element as a point mass:
        I ≈ sum(r_i² * dm_i)

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    r_values : array-like
        Perpendicular distances of each mass element from the rotation axis
        (metres). All values must be non-negative.
    dm_values : array-like
        Mass of each corresponding element (kg). All values must be positive.

    Returns
    -------
    float
        Approximate moment of inertia (kg·m²).

    Raises
    ------
    TypeError
        If r_values or dm_values are not array-like of real numbers.
    ValueError
        If lengths differ, any r < 0, or any dm <= 0.
    """
    try:
        r  = np.asarray(r_values,  dtype=float)
        dm = np.asarray(dm_values, dtype=float)
    except (TypeError, ValueError) as exc:
        raise TypeError(
            f"'r_values' and 'dm_values' must be array-like of numbers. Detail: {exc}"
        ) from exc

    validate_array_lengths(r, dm, "r_values", "dm_values")

    if np.any(r < 0):
        raise ValueError("All values in 'r_values' must be non-negative (distances from axis).")
    if np.any(dm <= 0):
        raise ValueError("All values in 'dm_values' must be strictly positive (mass elements).")

    # Numerical integration: I = sum(r_i^2 * dm_i)
    return float(np.sum(r ** 2 * dm))


@validate(I_cm=RULES.MOMENT_OF_INERTIA, M=RULES.POSITIVE, d=RULES.PARALLEL_AXIS_D)
def moment_of_inertia_parallel_axis(I_cm: float, M: float, d: float) -> float:
    """
    Moment of inertia via the parallel-axis theorem: I = I_cm + M*d².

    Shifts the rotation axis from the centre of mass to any parallel axis
    at distance d. This always increases the moment of inertia.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    I_cm : float
        Moment of inertia about the centre-of-mass axis (kg·m², > 0).
    M : float
        Total mass of the body (kg, > 0).
    d : float
        Perpendicular distance between the two parallel axes (metres, >= 0).
        d = 0 returns I_cm unchanged.

    Returns
    -------
    float
        Moment of inertia about the new parallel axis (kg·m²).
    """
    return I_cm + M * d ** 2


@validate(I_x=RULES.MOMENT_OF_INERTIA, I_y=RULES.MOMENT_OF_INERTIA)
def moment_of_inertia_perpendicular_axis(I_x: float, I_y: float) -> float:
    """
    Moment of inertia via the perpendicular-axis theorem: Iz = Ix + Iy.

    Valid for a flat (2-D) laminar body lying in the x-y plane.
    Iz is the MOI about the z-axis perpendicular to the plane.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    I_x : float
        Moment of inertia about the x-axis (kg·m², > 0).
    I_y : float
        Moment of inertia about the y-axis (kg·m², > 0).

    Returns
    -------
    float
        Moment of inertia about the z-axis (kg·m²).

    Notes
    -----
    This theorem applies ONLY to flat laminar (planar) bodies.
    It does NOT generalise to 3-D objects.
    """
    return I_x + I_y


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — Angular Momentum
# ══════════════════════════════════════════════════════════════════════════════

@validate(r=RULES.RADIUS, m=RULES.POSITIVE, v=RULES.REAL, theta=RULES.CROSS_ANGLE_DEG)
def angular_momentum_particle(r: float, m: float, v: float, theta: float) -> float:
    """
    Angular momentum of a particle: L = r * p * sin(theta) = m*v*r*sin(theta).

    This is the cross-product magnitude |r × p| where p = m*v is the
    linear momentum and theta is the angle between r and p.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    r : float
        Distance from the rotation axis to the particle (metres, > 0).
    m : float
        Mass of the particle (kg, > 0).
    v : float
        Speed of the particle (m/s). Sign encodes direction.
    theta : float
        Angle between position vector r and momentum vector p
        (degrees, [0, 180]).

    Returns
    -------
    float
        Angular momentum magnitude (kg·m²/s). Sign matches v.
    """
    theta_rad = math.radians(theta)
    return m * v * r * math.sin(theta_rad)


@validate(I=RULES.MOMENT_OF_INERTIA, w=RULES.ANGULAR_VEL)
def angular_momentum_rigid_body(I: float, w: float) -> float:
    """
    Angular momentum of a rigid body rotating about a fixed axis: L = I * w.

    This is the rotational analogue of linear momentum p = m*v.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    I : float
        Moment of inertia about the rotation axis (kg·m², > 0).
    w : float
        Angular velocity (rad/s). Signed; encodes direction of rotation.

    Returns
    -------
    float
        Angular momentum (kg·m²/s). Sign matches w.
    """
    return I * w


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — Newton's Second Law for rotation  tau = dL/dt
# ══════════════════════════════════════════════════════════════════════════════

@validate(L_initial=RULES.ANGULAR_MOMENTUM, L_final=RULES.ANGULAR_MOMENTUM,
          delta_t=RULES.POSITIVE_TIME)
def torque_from_angular_momentum_change(
    L_initial: float, L_final: float, delta_t: float
) -> float:
    """
    Net torque from rate of change of angular momentum: tau = dL/dt.

    Finite-difference approximation of the rotational form of Newton's
    second law (tau = dL/dt). For a body with constant I, this reduces
    to tau = I * alpha.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    L_initial : float
        Angular momentum at the start of the interval (kg·m²/s).
    L_final : float
        Angular momentum at the end of the interval (kg·m²/s).
    delta_t : float
        Time interval (seconds, > 0, within [T_MIN, T_MAX]).

    Returns
    -------
    float
        Average net torque over the interval (N·m).
    """
    delta_L = L_final - L_initial   # Change in angular momentum
    return delta_L / delta_t


def torque_from_angular_momentum_arrays(L, t):
    """
    Net torque at each time step via tau = dL/dt (array form).

    Useful when angular momentum has been recorded at discrete timestamps
    and you want the torque at each interval.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    L : array-like
        Angular momentum values (kg·m²/s) at each time step.
    t : array-like
        Corresponding timestamps (seconds, strictly increasing).

    Returns
    -------
    numpy.ndarray
        Average net torque (N·m) over each consecutive time interval.

    Raises
    ------
    TypeError
        If L or t are not array-like of real numbers.
    ValueError
        If lengths differ or t is not strictly increasing.
    """
    try:
        L = np.asarray(L, dtype=float)
        t = np.asarray(t, dtype=float)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"'L' and 't' must be array-like of numbers. Detail: {exc}") from exc

    validate_array_lengths(L, t, "L", "t")
    validate_strictly_increasing(t, "t")

    # dL / dt for each consecutive pair
    return np.diff(L) / np.diff(t)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — Convenience: Newton's 2nd Law (rotation) via alpha
# ══════════════════════════════════════════════════════════════════════════════

@validate(I=RULES.MOMENT_OF_INERTIA, alpha=RULES.ANGULAR_ACC)
def torque_from_inertia_alpha(I: float, alpha: float) -> float:
    """
    Net torque from moment of inertia and angular acceleration: tau = I * alpha.

    Rotational analogue of F = m*a. Valid when I is constant (fixed axis,
    rigid body with no redistribution of mass).

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    I : float
        Moment of inertia (kg·m², > 0).
    alpha : float
        Angular acceleration (rad/s²). Signed.

    Returns
    -------
    float
        Net torque (N·m). Sign matches alpha.
    """
    return I * alpha


@validate(tau=RULES.REAL, I=RULES.MOMENT_OF_INERTIA)
def alpha_from_torque(tau: float, I: float) -> float:
    """
    Angular acceleration from torque: alpha = tau / I.

    Rearrangement of tau = I * alpha.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    tau : float
        Net torque applied to the body (N·m). Signed.
    I : float
        Moment of inertia (kg·m², > 0).

    Returns
    -------
    float
        Angular acceleration (rad/s²). Sign matches tau.
    """
    return tau / I
