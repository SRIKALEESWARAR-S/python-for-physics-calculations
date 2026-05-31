"""
dynamics_v2.py - dynamics.py rewritten using the universal @validate decorator.

Compare with dynamics.py to see how much boilerplate disappears.

Project: Project Formulon-Physics
License: MIT License ~ Open Source Project
"""

import math
import numpy as np
from validators import validate, chain, Rule, RULES
from validators import validate_array_lengths, validate_strictly_increasing

G_STANDARD = 9.80665   # Standard gravitational acceleration (m/s²)


# ── Newton's Second Law  F = m·a ───────────────────────────────────────────────

@validate(m=RULES.POSITIVE, a=RULES.REAL)
def net_force(m: float, a: float) -> float:
    """
    Net force on an object: F = m·a.

    Project: Project Formulon-Physics
    """
    return m * a


@validate(f=RULES.REAL, m=RULES.POSITIVE)
def acceleration_from_force(f: float, m: float) -> float:
    """
    Acceleration from net force: a = F / m.

    Project: Project Formulon-Physics
    """
    return f / m


# ── Weight  W = m·g ───────────────────────────────────────────────────────────

@validate(m=RULES.POSITIVE, g=RULES.GRAVITY)
def weight(m: float, g: float = G_STANDARD) -> float:
    """
    Gravitational weight: W = m·g.

    Project: Project Formulon-Physics
    """
    return m * g


@validate(w=RULES.NON_NEGATIVE, g=RULES.GRAVITY)
def mass_from_weight(w: float, g: float = G_STANDARD) -> float:
    """
    Mass from weight: m = W / g.

    Project: Project Formulon-Physics
    """
    return w / g


# ── Momentum  p = m·v ─────────────────────────────────────────────────────────

@validate(m=RULES.POSITIVE, v=RULES.REAL)
def momentum(m: float, v: float) -> float:
    """
    Linear momentum: p = m·v.

    Project: Project Formulon-Physics
    """
    return m * v


@validate(p=RULES.REAL, m=RULES.POSITIVE)
def velocity_from_momentum(p: float, m: float) -> float:
    """
    Velocity from momentum: v = p / m.

    Project: Project Formulon-Physics
    """
    return p / m


# ── Force from momentum change  F = dp/dt ─────────────────────────────────────

@validate(p_initial=RULES.REAL, p_final=RULES.REAL, delta_t=RULES.POSITIVE_TIME)
def force_from_momentum_change(p_initial: float, p_final: float, delta_t: float) -> float:
    """
    Average force from momentum change: F = delta_p / delta_t.

    Project: Project Formulon-Physics
    """
    return (p_final - p_initial) / delta_t


def force_from_momentum_arrays(p, t):
    """
    Average force at each time step via F = dp/dt (array form).

    Project: Project Formulon-Physics
    """
    # Arrays need length/shape checks — handled by standalone helpers
    p = np.asarray(p, dtype=float)
    t = np.asarray(t, dtype=float)
    validate_array_lengths(p, t, "p", "t")
    validate_strictly_increasing(t, "t")

    return np.diff(p) / np.diff(t)


# ── Impulse  J = F·Δt ─────────────────────────────────────────────────────────

@validate(f=RULES.REAL, delta_t=RULES.POSITIVE_TIME)
def impulse(f: float, delta_t: float) -> float:
    """
    Impulse from constant force: J = F·delta_t.

    Project: Project Formulon-Physics
    """
    return f * delta_t


@validate(j=RULES.REAL, delta_t=RULES.POSITIVE_TIME)
def force_from_impulse(j: float, delta_t: float) -> float:
    """
    Average force from impulse: F = J / delta_t.

    Project: Project Formulon-Physics
    """
    return j / delta_t


# ── Friction ──────────────────────────────────────────────────────────────────

@validate(mu_s=RULES.NON_NEGATIVE, normal_force=RULES.NON_NEGATIVE)
def static_friction_max(mu_s: float, normal_force: float) -> float:
    """
    Maximum static friction: f_s = mu_s * N.

    Project: Project Formulon-Physics
    """
    return mu_s * normal_force


@validate(mu_k=RULES.NON_NEGATIVE, normal_force=RULES.NON_NEGATIVE)
def kinetic_friction(mu_k: float, normal_force: float) -> float:
    """
    Kinetic friction force: f_k = mu_k * N.

    Project: Project Formulon-Physics
    """
    return mu_k * normal_force


# ── Hooke's Law  F = -k·x ─────────────────────────────────────────────────────

@validate(k=RULES.SPRING_CONST, x=RULES.REAL)
def spring_force(k: float, x: float) -> float:
    """
    Spring restoring force: F = -k * x  (Hooke's Law).

    Project: Project Formulon-Physics
    """
    return -k * x


@validate(f=RULES.REAL, k=RULES.SPRING_CONST)
def spring_displacement(f: float, k: float) -> float:
    """
    Spring displacement from force: x = -F / k.

    Project: Project Formulon-Physics
    """
    return -f / k


# ── Apparent Weight ───────────────────────────────────────────────────────────

@validate(m=RULES.POSITIVE, g=RULES.GRAVITY, a=RULES.NON_NEGATIVE)
def apparent_weight_upward(m: float, g: float = G_STANDARD, a: float = 0.0) -> float:
    """
    Apparent weight during upward acceleration: W_app = m*(g + a).

    Project: Project Formulon-Physics
    """
    return m * (g + a)


# Custom rule: downward acceleration cannot exceed g (would mean leaving surface)
_a_le_g = Rule(
    lambda v, _: True,   # placeholder — real check needs g, done below
    ""
)

@validate(m=RULES.POSITIVE, g=RULES.GRAVITY, a=RULES.NON_NEGATIVE)
def apparent_weight_downward(m: float, g: float = G_STANDARD, a: float = 0.0) -> float:
    """
    Apparent weight during downward acceleration: W_app = m*(g - a).

    At a = g the object is in free fall (apparent weight = 0).

    Project: Project Formulon-Physics
    """
    # Cross-parameter check (a vs g) — needs both values, can't be a simple Rule
    if a > g:
        raise ValueError(
            f"Downward acceleration 'a' ({a}) cannot exceed 'g' ({g}); "
            "apparent weight would be negative (object leaves the surface)."
        )
    return m * (g - a)
