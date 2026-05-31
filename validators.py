"""
validators.py - Universal validation module for Project Formulon-Physics.

Provides:
  - Standalone validator functions  (_validate_* helpers)
  - A composable @validate() decorator for annotating function signatures
  - Pre-built rule sets (RULES) for physics-domain types

Project: Project Formulon-Physics
License: MIT License ~ Open Source Project

Usage
-----
    from validators import validate, RULES

    # --- as a decorator ---
    @validate(m=RULES.POSITIVE, v=RULES.REAL, t=RULES.NON_NEG_TIME)
    def momentum(m, v, t):
        return m * v

    # --- composing custom rules ---
    from validators import Rule, chain
    angle = chain(RULES.REAL, Rule(lambda x, _: 0 <= x <= 90,
                                   "must be in [0, 90] degrees"))

    @validate(theta=angle)
    def projectile_range(v0, theta, g):
        ...
"""

import math
import functools
import inspect
import numpy as np
from typing import Callable, Any

# ── Stability bounds (shared across all physics modules) ───────────────────────
T_MIN = 1e-6    # Minimum allowable time (seconds)
T_MAX = 1e100   # Maximum allowable time (seconds)


# ══════════════════════════════════════════════════════════════════════════════
# 1.  Rule  — the atomic unit of validation
# ══════════════════════════════════════════════════════════════════════════════

class Rule:
    """
    A single validation rule: a predicate paired with an error message.

    Parameters
    ----------
    predicate : Callable[[Any, str], bool]
        A function (value, param_name) -> bool.
        Return True  = passes validation.
        Return False = raise ValueError.
    message : str
        Human-readable description of what went wrong.
        Use '{name}' and '{value}' as placeholders.
    error_type : type, optional
        Exception class to raise (default: ValueError).

    Example
    -------
        positive = Rule(lambda v, _: v > 0, "'{name}' must be > 0 (got {value}).")
    """

    def __init__(
        self,
        predicate: Callable[[Any, str], bool],
        message: str,
        error_type: type = ValueError,
    ):
        self.predicate  = predicate
        self.message    = message
        self.error_type = error_type

    def check(self, value: Any, name: str) -> None:
        """Run the predicate; raise self.error_type on failure."""
        if not self.predicate(value, name):
            raise self.error_type(self.message.format(name=name, value=value))


# ══════════════════════════════════════════════════════════════════════════════
# 2.  chain()  — compose multiple Rules into one
# ══════════════════════════════════════════════════════════════════════════════

def chain(*rules: Rule) -> Rule:
    """
    Combine multiple Rules into a single Rule that runs them in order.

    The first failing rule raises immediately; later rules are skipped.

    Project: Project Formulon-Physics

    Parameters
    ----------
    *rules : Rule
        Any number of Rule instances to chain together.

    Returns
    -------
    Rule
        A composite Rule whose check() runs every sub-rule in sequence.

    Example
    -------
        angle_rule = chain(RULES.REAL, RULES.NON_NEGATIVE,
                           Rule(lambda v, _: v <= 90, "'{name}' must be <= 90°."))
    """
    # Sentinel predicate — the real work happens inside check()
    composite = Rule(lambda v, n: True, "")

    def _check(value: Any, name: str) -> None:
        for rule in rules:
            rule.check(value, name)   # each rule raises on its own if needed

    # Override check() on the composite object directly
    composite.check = _check
    return composite


# ══════════════════════════════════════════════════════════════════════════════
# 3.  Pre-built Rule instances  (RULES namespace)
# ══════════════════════════════════════════════════════════════════════════════

class _Rules:
    """
    Namespace of ready-to-use Rule instances for physics-domain values.

    Access via the module-level singleton:  RULES.POSITIVE, RULES.REAL, …

    Project: Project Formulon-Physics
    """

    # ── Type rules ─────────────────────────────────────────────────────────────
    REAL = Rule(
        lambda v, _: isinstance(v, (int, float)) and not isinstance(v, bool),
        "'{name}' must be a real number (int or float), got {value!r}.",
        TypeError,
    )

    ARRAY_LIKE = Rule(
        lambda v, _: hasattr(v, "__len__") or hasattr(v, "__iter__"),
        "'{name}' must be array-like (list, tuple, or numpy array), got {value!r}.",
        TypeError,
    )

    # ── Scalar magnitude rules ─────────────────────────────────────────────────
    POSITIVE = chain(
        Rule(lambda v, _: isinstance(v, (int, float)) and not isinstance(v, bool),
             "'{name}' must be a real number, got {value!r}.", TypeError),
        Rule(lambda v, _: v > 0,
             "'{name}' must be strictly positive (> 0), got {value}."),
    )

    NON_NEGATIVE = chain(
        Rule(lambda v, _: isinstance(v, (int, float)) and not isinstance(v, bool),
             "'{name}' must be a real number, got {value!r}.", TypeError),
        Rule(lambda v, _: v >= 0,
             "'{name}' must be non-negative (>= 0), got {value}."),
    )

    NON_ZERO = chain(
        Rule(lambda v, _: isinstance(v, (int, float)) and not isinstance(v, bool),
             "'{name}' must be a real number, got {value!r}.", TypeError),
        Rule(lambda v, _: v != 0,
             "'{name}' must be non-zero, got {value}."),
    )

    # ── Time-specific rules ────────────────────────────────────────────────────
    NON_NEG_TIME = chain(
        Rule(lambda v, _: isinstance(v, (int, float)) and not isinstance(v, bool),
             "'{name}' must be a real number, got {value!r}.", TypeError),
        Rule(lambda v, _: v >= 0,
             "Time '{name}' must be non-negative (>= 0), got {value}."),
    )

    POSITIVE_TIME = chain(
        Rule(lambda v, _: isinstance(v, (int, float)) and not isinstance(v, bool),
             "'{name}' must be a real number, got {value!r}.", TypeError),
        Rule(lambda v, _: v > 0,
             "Time '{name}' must be strictly positive (> 0), got {value}."),
        Rule(lambda v, _: v >= T_MIN,
             f"Time '{{name}}' is below T_MIN = {T_MIN}; numerical instability risk (got {{value}})."),
        Rule(lambda v, _: v <= T_MAX,
             f"Time '{{name}}' exceeds T_MAX = {T_MAX}; overflow risk (got {{value}})."),
    )

    # ── Physics-domain specific rules ─────────────────────────────────────────
    ANGLE_DEG = chain(
        Rule(lambda v, _: isinstance(v, (int, float)) and not isinstance(v, bool),
             "'{name}' must be a real number, got {value!r}.", TypeError),
        Rule(lambda v, _: 0 <= v <= 360,
             "'{name}' must be in [0, 360] degrees, got {value}."),
    )

    ANGLE_DEG_90 = chain(
        Rule(lambda v, _: isinstance(v, (int, float)) and not isinstance(v, bool),
             "'{name}' must be a real number, got {value!r}.", TypeError),
        Rule(lambda v, _: 0 <= v <= 90,
             "'{name}' must be in [0, 90] degrees, got {value}."),
    )

    COEFF_FRICTION = chain(
        Rule(lambda v, _: isinstance(v, (int, float)) and not isinstance(v, bool),
             "'{name}' must be a real number, got {value!r}.", TypeError),
        Rule(lambda v, _: 0 <= v <= 1,
             "'{name}' is a friction coefficient and must be in [0, 1], got {value}."),
    )

    SPRING_CONST = chain(
        Rule(lambda v, _: isinstance(v, (int, float)) and not isinstance(v, bool),
             "'{name}' must be a real number, got {value!r}.", TypeError),
        Rule(lambda v, _: v > 0,
             "Spring constant '{name}' must be strictly positive (> 0), got {value}."),
    )

    GRAVITY = chain(
        Rule(lambda v, _: isinstance(v, (int, float)) and not isinstance(v, bool),
             "'{name}' must be a real number, got {value!r}.", TypeError),
        Rule(lambda v, _: v > 0,
             "Gravitational acceleration '{name}' must be strictly positive, got {value}."),
        Rule(lambda v, _: v <= 300,
             "'{name}' = {value} m/s² seems unrealistically high (max ~274 m/s² for the Sun)."),
    )


# Module-level singleton — import and use as RULES.POSITIVE etc.
RULES = _Rules()


# ══════════════════════════════════════════════════════════════════════════════
# 4.  @validate()  — the decorator factory
# ══════════════════════════════════════════════════════════════════════════════

def validate(**param_rules: Rule):
    """
    Decorator factory: attach Rule instances to specific parameter names.

    Call it with keyword arguments mapping parameter names to Rules (or
    chained Rules). The decorator validates each named argument before
    the wrapped function body runs — positional or keyword, it doesn't matter.

    Project: Project Formulon-Physics
    License: MIT License ~ Open Source Project

    Parameters
    ----------
    **param_rules : Rule
        keyword = Rule (or chain(...))
        The keyword must exactly match the parameter name in the
        decorated function's signature.

    Returns
    -------
    Callable
        The decorated function with pre-call validation baked in.

    Raises
    ------
    TypeError
        If a parameter rule is not a Rule instance.
    NameError
        If a rule key does not match any parameter in the function signature.

    Examples
    --------
    Basic usage::

        @validate(m=RULES.POSITIVE, v=RULES.REAL, t=RULES.NON_NEG_TIME)
        def momentum(m, v, t):
            return m * v

    Custom rule composed inline::

        @validate(
            theta=chain(RULES.REAL,
                        Rule(lambda v, _: 0 < v < 90,
                             "'{name}' must be strictly between 0 and 90 degrees."))
        )
        def trajectory(theta, v0, g):
            ...

    Array-length validation (handled inside the function, not via decorator)::

        @validate(g=RULES.GRAVITY, t=RULES.NON_NEG_TIME)
        def free_fall_height(g, t):
            return 0.5 * g * t ** 2
    """
    # Verify all values passed to @validate() are Rule instances
    for key, rule in param_rules.items():
        if not isinstance(rule, Rule) and not callable(getattr(rule, "check", None)):
            raise TypeError(
                f"@validate: '{key}' must be a Rule instance, "
                f"got {type(rule).__name__!r}."
            )

    def decorator(func: Callable) -> Callable:
        # Inspect the function signature once at decoration time (cheap)
        sig        = inspect.signature(func)
        param_names = list(sig.parameters.keys())

        # Warn at import time if a rule key doesn't match any parameter
        for key in param_rules:
            if key not in param_names:
                raise NameError(
                    f"@validate on '{func.__name__}': rule key '{key}' does not "
                    f"match any parameter. Available: {param_names}"
                )

        @functools.wraps(func)           # preserves __name__, __doc__, etc.
        def wrapper(*args, **kwargs):
            # Bind the actual call arguments to parameter names
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()       # fills in default values

            # Run each rule against its corresponding argument value
            for param, rule in param_rules.items():
                if param in bound.arguments:
                    rule.check(bound.arguments[param], param)

            return func(*args, **kwargs)

        # Attach the rules dict to the wrapper for introspection
        wrapper._validate_rules = param_rules
        return wrapper

    return decorator


# ══════════════════════════════════════════════════════════════════════════════
# 5.  Array validators  (used inside functions, not as decorators)
# ══════════════════════════════════════════════════════════════════════════════

def validate_array_lengths(a, b, name_a: str, name_b: str) -> None:
    """
    Raise ValueError if two array-like objects differ in length.

    Project: Project Formulon-Physics
    """
    if len(a) != len(b):
        raise ValueError(
            f"'{name_a}' and '{name_b}' must have the same length "
            f"(got {len(a)} and {len(b)})."
        )


def validate_time_array(t, name: str = "t") -> np.ndarray:
    """
    Validate and return a time array for numerical stability.

    Checks: strictly positive, at least two distinct values,
    all values within [T_MIN, T_MAX].

    Project: Project Formulon-Physics

    Returns
    -------
    numpy.ndarray
        The validated array (converted from whatever array-like was passed).
    """
    try:
        t = np.asarray(t, dtype=float)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"'{name}' must be array-like of numbers. Detail: {exc}") from exc

    if t.ndim != 1:
        raise ValueError(f"'{name}' must be a 1-D array (got shape {t.shape}).")
    if len(t) < 2:
        raise ValueError(f"'{name}' must contain at least 2 elements.")
    if np.any(t <= 0):
        raise ValueError(f"All values in '{name}' must be strictly positive.")
    if t[-1] - t[0] == 0:
        raise ValueError(f"'{name}' must contain at least two distinct values.")
    if np.any(t < T_MIN):
        raise ValueError(f"All values in '{name}' must be >= T_MIN = {T_MIN}.")
    if np.any(t > T_MAX):
        raise ValueError(f"All values in '{name}' must be <= T_MAX = {T_MAX}.")

    return t


def validate_strictly_increasing(arr, name: str = "t") -> None:
    """
    Raise ValueError if a numeric array is not strictly increasing.

    Project: Project Formulon-Physics
    """
    arr = np.asarray(arr, dtype=float)
    if np.any(np.diff(arr) <= 0):
        raise ValueError(f"'{name}' must be strictly increasing (all consecutive differences > 0).")
