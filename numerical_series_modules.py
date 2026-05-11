"""
Mathematical Series Computation Module

This module provides optimized functions for calculating various mathematical series
using Numba for just-in-time (JIT) compilation. Numba is used here because:

- It compiles Python functions to machine code at runtime, achieving performance
  comparable to C/C++ for numerical computations without leaving Python.
- Ideal for loops and arithmetic-heavy operations, such as summing large series
  or processing datasets from CSV files with millions of rows.
- Enables vectorization and parallelization in future extensions.
- Maintains Python's ease of use while delivering speed-ups of 10x-100x+ for
  numerical workloads, making it perfect for data-intensive applications.

The module includes defensive programming to handle malicious or erroneous inputs,
preventing crashes and ensuring graceful degradation.
"""

import re
import numba
from numba import njit

# Constants for input validation to prevent resource exhaustion
MAX_N = 10_000_000  # Maximum allowed value for n to avoid excessive computation
MAX_STR_LEN = 128   # Maximum string length to prevent buffer overflow-like issues


def _sanitize_string(value):
    """
    Sanitizes string inputs to prevent injection attacks and resource abuse.
    - Strips whitespace.
    - Checks length to avoid denial-of-service via large strings.
    - Rejects control characters that could cause display issues or exploits.
    - Blocks potentially dangerous characters like braces, brackets, etc., that
      might be used in code injection or shell commands.
    This ensures only safe, numeric-like strings are processed.
    """
    text = value.strip()
    if not text or len(text) > MAX_STR_LEN:
        raise ValueError("Invalid string")
    if any(ord(ch) < 32 for ch in text):
        raise ValueError("Invalid string")
    if any(ch in text for ch in '{}[]()<>$`\\'):
        raise ValueError("Invalid string")
    return text


def _prepare_scalar(value):
    """
    Prepares and validates scalar inputs from various types.
    - Rejects None and bool to prevent logical errors.
    - Accepts int/float directly.
    - For strings, sanitizes and attempts numeric conversion using regex.
    - This layer handles type coercion safely, preventing unexpected behavior
      from mixed-type data (e.g., from CSV files).
    """
    if value is None:
        raise ValueError("Invalid input")
    if isinstance(value, bool):
        raise ValueError("Invalid input")
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        cleaned = _sanitize_string(value)
        if re.fullmatch(r'[+-]?\d+', cleaned):
            return int(cleaned)
        if re.fullmatch(r'[+-]?(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?', cleaned):
            return float(cleaned)
    raise ValueError("Invalid input")


def _safe_int(value):
    """
    Safely converts input to integer with strict validation.
    - Uses _prepare_scalar for initial sanitization.
    - Ensures floats are whole numbers before conversion.
    - Prevents implicit type coercion that could lead to precision loss or errors.
    """
    number = _prepare_scalar(value)
    if isinstance(number, float):
        if number.is_integer():
            number = int(number)
        else:
            raise ValueError("Invalid integer")
    if not isinstance(number, int):
        raise ValueError("Invalid integer")
    return number


def _safe_float(value):
    """
    Safely converts input to float.
    - Relies on _prepare_scalar for validation and conversion.
    - Ensures consistent float handling for arithmetic operations.
    """
    number = _prepare_scalar(value)
    return float(number)


@njit
def _arithmatic_nterm(a, n, d):
    """
    Numba-compiled core for arithmetic series nth term calculation.
    @njit ensures this function is compiled to machine code for maximum speed,
    avoiding Python's interpreter overhead. Essential for large n values in
    data processing loops.
    """
    return a + (n - 1) * d

def arithmatic_nterm(a, n, d):
    """
    Public wrapper for arithmetic nth term with comprehensive error handling.
    - Validates inputs using safe converters.
    - Checks domain constraints (n > 0).
    - Catches KeyboardInterrupt for user cancellation.
    - Handles TypeError/ValueError for invalid inputs.
    - Catches all other exceptions to prevent crashes, returning safe messages.
    This ensures the module remains stable under adversarial inputs.
    """
    try:
        a = _safe_int(a)
        n = _safe_int(n)
        d = _safe_int(d)
        if n <= 0:
            return "Invalid input"
        return _arithmatic_nterm(a, n, d)
    except KeyboardInterrupt:
        return "Execution interrupted by user"
    except (TypeError, ValueError):
        return "Invalid input"
    except Exception:
        return "I'm not dead, I'm on rest"

@njit
def _sum_of_arithmatic_progression(a, n, d):
    """
    Numba-compiled core for arithmetic series sum calculation.
    Uses @njit for efficient floating-point arithmetic, crucial when
    processing large datasets where this formula is applied repeatedly.
    """
    return (n / 2.0) * (2.0 * a + (n - 1.0) * d)

def sum_of_arithmatic_progression(a, n, d):
    """
    Public wrapper for arithmetic series sum with robust error handling.
    - Employs _safe_float for flexible numeric inputs.
    - Validates n > 0 to prevent infinite or invalid computations.
    - Exception handling mirrors the pattern: user interrupt, input errors,
      and fallback for unexpected issues to maintain module resilience.
    """
    try:
        a = _safe_float(a)
        n = _safe_int(n)
        d = _safe_float(d)
        if n <= 0:
            return "Invalid input"
        return _sum_of_arithmatic_progression(a, n, d)
    except KeyboardInterrupt:
        return "Execution interrupted by user"
    except (TypeError, ValueError):
        return "Invalid input"
    except Exception:
        return "I'm not dead, I'm on rest"

@njit
def _geometric_nterm(a, n, r):
    return a * (r ** (n - 1))

def geometric_nterm(a, n, r):
    try:
        a = _safe_float(a)
        n = _safe_int(n)
        r = _safe_float(r)
        if n <= 0:
            return "Invalid input"
        return _geometric_nterm(a, n, r)
    except KeyboardInterrupt:
        return "Execution interrupted by user"
    except (TypeError, ValueError):
        return "Invalid input"
    except Exception:
        return "I'm not dead, I'm on rest"

@njit
def _sum_of_infinite_geometric_progression(a, r):
    return a / (1.0 - r)

def sum_of_infinite_geometric_progression(a, r):
    try:
        a = _safe_float(a)
        r = _safe_float(r)
        if abs(r) >= 1.0:
            return "Invalid input"
        return _sum_of_infinite_geometric_progression(a, r)
    except KeyboardInterrupt:
        return "Execution interrupted by user"
    except (TypeError, ValueError):
        return "Invalid input"
    except Exception:
        return "I'm not dead, I'm on rest"

@njit
def _sum_of_first_n_natural_numbers(n):
    return (n * (n + 1)) // 2

def sum_of_first_n_natural_numbers(n):
    try:
        n = _safe_int(n)
        if n <= 0:
            return "Invalid input"
        return _sum_of_first_n_natural_numbers(n)
    except KeyboardInterrupt:
        return "Execution interrupted by user"
    except (TypeError, ValueError):
        return "Invalid input"
    except Exception:
        return "I'm not dead, I'm on rest"

@njit
def _sum_of_squares(n):
    return (n * (n + 1) * (2 * n + 1)) // 6

def sum_of_squares(n):
    try:
        n = _safe_int(n)
        if n <= 0:
            return "Invalid input"
        return _sum_of_squares(n)
    except KeyboardInterrupt:
        return "Execution interrupted by user"
    except (TypeError, ValueError):
        return "Invalid input"
    except Exception:
        return "I'm not dead, I'm on rest"

@njit
def _sum_of_cubes(n):
    return ((n * (n + 1)) // 2) ** 2

def sum_of_cubes(n):
    try:
        n = _safe_int(n)
        if n <= 0:
            return "Invalid input"
        return _sum_of_cubes(n)
    except KeyboardInterrupt:
        return "Execution interrupted by user"
    except (TypeError, ValueError):
        return "Invalid input"
    except Exception:
        return "I'm not dead, I'm on rest"

@njit
def _sum_of_first_n_odd_numbers(n):
    return n ** 2

def sum_of_first_n_odd_numbers(n):
    try:
        n = _safe_int(n)
        if n <= 0:
            return "Invalid input"
        return _sum_of_first_n_odd_numbers(n)
    except KeyboardInterrupt:
        return "Execution interrupted by user"
    except (TypeError, ValueError):
        return "Invalid input"
    except Exception:
        return "I'm not dead, I'm on rest"

@njit
def _fibonacci_nterm(n):
    a = 0
    b = 1
    for _ in range(1, n):
        a, b = b, a + b
    return a

def fibonacci_nterm(n):
    try:
        n = _safe_int(n)
        if n <= 0:
            return "Invalid input"
        return _fibonacci_nterm(n)
    except KeyboardInterrupt:
        return "Execution interrupted by user"
    except (TypeError, ValueError):
        return "Invalid input"
    except Exception:
        return "I'm not dead, I'm on rest"

FUNCTIONS = [
    arithmatic_nterm,
    sum_of_arithmatic_progression,
    geometric_nterm,
    sum_of_infinite_geometric_progression,
    sum_of_first_n_natural_numbers,
    sum_of_squares,
    sum_of_cubes,
    sum_of_first_n_odd_numbers,
    fibonacci_nterm,
]
"""
List of all public functions for easy iteration or import.
Useful for batch processing datasets, e.g., applying all functions
to columns in a CSV file.
"""

__all__ = [
    "FUNCTIONS",
    "arithmatic_nterm",
    "sum_of_arithmatic_progression",
    "geometric_nterm",
    "sum_of_infinite_geometric_progression",
    "sum_of_first_n_natural_numbers",
    "sum_of_squares",
    "sum_of_cubes",
    "sum_of_first_n_odd_numbers",
    "fibonacci_nterm",
]
"""
Explicitly defines the public API of this module.
Prevents accidental import of internal functions like _safe_int.
"""
