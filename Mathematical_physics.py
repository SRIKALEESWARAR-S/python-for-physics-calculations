"""
Advanced mathematical physics computation module
This module provides advanced functions for mathematical physics computations
which includes:
1.Fourier analysis powered by scipy
2.tensor
3.gauss divergence theorem,stokes theorem,green's theorem
4.advanced linear algebra
5.differential equations solvers
6.special functions
7.heat equations
8.wave equations
All are implemented using scipy and numpy for efficient computation.
also the module is powered by numba for just-in-time compilation to enhance performance.
This module is designed for researchers and students in the field of mathematical physics
This module is open-source and contributions are welcome.
CCA MIT License powered by PROJECT FORMULON-PHYSICS
"""
import re
import numba
from numba import jit
import numpy as np
import scipy as si
from functools import wraps


MAX_NUMBER = 100000000
MAX_STR_LENGTH = 1280

# Combined decorator for error handling and numba JIT compilation
def safe_compute_jit(use_jit=True, nopython=False):
    """
    Combined decorator for global error handling and numba JIT compilation.
    Parameters:
    use_jit (bool): Whether to apply JIT compilation. Default is True.
    nopython (bool): Whether to use nopython mode for JIT. Default is False for compatibility.
    """
    def decorator(func):
        # Apply JIT if requested
        if use_jit:
            try:
                jitted_func = jit(func, nopython=nopython, cache=True)
            except Exception:
                # Fallback: use JIT with nopython=False
                jitted_func = jit(func, nopython=False, cache=True)
        else:
            jitted_func = func
        
        # Apply error handling wrapper
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return jitted_func(*args, **kwargs)
            except ValueError as e:
                raise ValueError(f"Validation error in {func.__name__}: {str(e)}")
            except (ZeroDivisionError, FloatingPointError) as e:
                raise ArithmeticError(f"Arithmetic error in {func.__name__}: {str(e)}")
            except Exception as e:
                raise RuntimeError(f"Unknown error in {func.__name__}: {type(e).__name__}: {str(e)}")
        return wrapper
    return decorator

# Alias for backward compatibility
def safe_compute(func):
    """Legacy decorator - now uses combined safe_compute_jit."""
    return safe_compute_jit(use_jit=True, nopython=False)(func)
@safe_compute
def validate_values(values):
    """
    Validate the input values for mathematical physics computations.
    Parameters:
    values (array-like): Input values to be validated.
    Returns:
    bool: True if the values are valid, False otherwise.
    """
    if isinstance(values, (int, float)):
        return -MAX_NUMBER <= values <= MAX_NUMBER
    elif isinstance(values, (list, np.ndarray)):
        return all(validate_values(v) for v in values)
    else:
        return False
@safe_compute
def validate_string(s):
    """
    Validate the input string for mathematical physics computations.
    Parameters:
    s (str): Input string to be validated.
    Returns:
    bool: True if the string is valid, False otherwise.
    """
    text = s.strip()
    if not text or len(text) > MAX_STR_LENGTH:
        raise ValueError("Invalid string")
    if any(ord(ch) < 32 for ch in text):
        raise ValueError("Invalid string")
    if any(ch in text for ch in '{}[]()<>$`\\'):
        raise ValueError("Invalid string")
    return text
@safe_compute
def validate_zeros_negatives(values):
    """
    Validate that the input values do not contain zeros for mathematical physics computations.
    Parameters:
    values (array-like): Input values to be validated.
    Returns:
    bool: True if the values do not contain zeros, False otherwise.
    """
    if isinstance(values, (int, float)):
        return values > 0
    elif isinstance(values, (list, np.ndarray)):
        return all(validate_zeros_negatives(v) for v in values)
    else:
        return False
@safe_compute
def safe_int_float(value):
    """
    Safely convert a value to an integer or float for mathematical physics computations.
    Parameters:
    value: Input value to be converted.
    Returns:
    int or float: The converted integer or float value.
    """
    if isinstance(value, (int, float)):
        return value
    elif isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                raise ValueError("Invalid input: not a number")
    else:
        raise ValueError("Invalid input type: expected int, float, or string")
@safe_compute
def fourier_series_expansion(x):
    """
    Compute the Fourier series expansion of a function at a given point x.
    Parameters:
    x (float): The point at which to compute the Fourier series expansion.
    Returns:
    float: The value of the Fourier series expansion at point x.
    """
    # Example implementation for a simple function f(t) = t on the interval [0, 2*pi]
    n_terms = 100  # Number of terms in the Fourier series
    a0 = 1 / (2 * np.pi) * si.integrate.quad(lambda t: t, 0, 2 * np.pi)[0]
    an = lambda n: 1 / np.pi * si.integrate.quad(lambda t: t * np.cos(n * t), 0, 2 * np.pi)[0]
    bn = lambda n: 1 / np.pi * si.integrate.quad(lambda t: t * np.sin(n * t), 0, 2 * np.pi)[0]
    
    fourier_sum = a0
    for n in range(1, n_terms + 1):
        fourier_sum += an(n) * np.cos(n * x) + bn(n) * np.sin(n * x)
    
    return fourier_sum
@safe_compute
def complex_fourier_series(x):
    """
    Compute the complex Fourier series expansion of a function at a given point x.
    Parameters:
    x (float): The point at which to compute the complex Fourier series expansion.
    Returns:
    complex: The value of the complex Fourier series expansion at point x.
    """
    # Example implementation for a simple function f(t) = t on the interval [0, 2*pi]
    n_terms = 100  # Number of terms in the Fourier series
    cn = lambda n: 1 / (2 * np.pi) * si.integrate.quad(lambda t: t * np.exp(-1j * n * t), 0, 2 * np.pi)[0]
    
    fourier_sum = 0
    for n in range(-n_terms, n_terms + 1):
        fourier_sum += cn(n) * np.exp(1j * n * x)
    
    return fourier_sum
@safe_compute
def fourier_transform(f, x):
    """
    Compute the Fourier transform of a function f at a given point x.
    Parameters:
    f (callable): The function to be transformed.
    x (float): The point at which to compute the Fourier transform.
    Returns:
    complex: The value of the Fourier transform at point x.
    """
    # Example implementation using numerical integration
    return si.integrate.quad(lambda t: f(t) * np.exp(-1j * x * t), -np.inf, np.inf)[0]
@safe_compute
def inverse_fourier_transform(F, t):
    """
    Compute the inverse Fourier transform of a function F at a given point t.
    Parameters:
    F (callable): The function to be transformed.
    t (float): The point at which to compute the inverse Fourier transform.
    Returns:
    complex: The value of the inverse Fourier transform at point t.
    """
    # Example implementation using numerical integration
    return si.integrate.quad(lambda x: F(x) * np.exp(1j * x * t), -np.inf, np.inf)[0] / (2 * np.pi) 
@safe_compute
def parsevals_theorem(f, x):
    """
    Compute the Parseval's theorem for a function f at a given point x.
    Parameters:
    f (callable): The function for which to compute Parseval's theorem.
    x (float): The point at which to compute Parseval's theorem.
    Returns:
    float: The value of Parseval's theorem at point x.
    """
    # Example implementation using numerical integration
    return si.integrate.quad(lambda t: abs(f(t))**2, -np.inf, np.inf)[0]
@safe_compute
def convolution(f, g, x):
    """Compute the convolution of two functions f and g at a given point x"""
    # Example implementation using numerical integration
    return si.integrate.quad(lambda t: f(t) * g(x - t), -np.inf, np.inf)[0]
@safe_compute
def legendres_polynomial(n, x):
    """
    Compute the Legendre polynomial of degree n at a given point x.
    Parameters:
    n (int): The degree of the Legendre polynomial.
    x (float): The point at which to compute the Legendre polynomial.
    Returns:
    float: The value of the Legendre polynomial of degree n at point x.
    """
    if n == 0:
        return 1
    elif n == 1:
        return x
    else:
        Pn_minus_2 = 1
        Pn_minus_1 = x
        for k in range(2, n + 1):
            Pn = ((2 * k - 1) * x * Pn_minus_1 - (k - 1) * Pn_minus_2) / k
            Pn_minus_2, Pn_minus_1 = Pn_minus_1, Pn
        return Pn
@safe_compute
def laguerre_polynomial(n, x):
    """
    Compute the Laguerre polynomial of degree n at a given point x.
    Parameters:
    n (int): The degree of the Laguerre polynomial.
    x (float): The point at which to compute the Laguerre polynomial.
    Returns:
    float: The value of the Laguerre polynomial of degree n at point x.
    """
    if n == 0:
        return 1
    elif n == 1:
        return 1 - x
    else:
        Ln_minus_2 = 1
        Ln_minus_1 = 1 - x
        for k in range(2, n + 1):
            Ln = ((2 * k - 1 - x) * Ln_minus_1 - (k - 1) * Ln_minus_2) / k
            Ln_minus_2, Ln_minus_1 = Ln_minus_1, Ln
        return Ln
@safe_compute
def hermite_polynomial(n, x):
    """
    Compute the Hermite polynomial of degree n at a given point x.
    Parameters:
    n (int): The degree of the Hermite polynomial.
    x (float): The point at which to compute the Hermite polynomial.
    Returns:
    float: The value of the Hermite polynomial of degree n at point x.
    """
    if n == 0:
        return 1
    elif n == 1:
        return 2 * x
    else:
        Hn_minus_2 = 1
        Hn_minus_1 = 2 * x
        for k in range(2, n + 1):
            Hn = 2 * x * Hn_minus_1 - 2 * (k - 1) * Hn_minus_2
            Hn_minus_2, Hn_minus_1 = Hn_minus_1, Hn
        return Hn
@safe_compute
def bessel_function(n, x):
    """
    Compute the Bessel function of the first kind of order n at a given point x.
    Parameters:
    n (int): The order of the Bessel function.
    x (float): The point at which to compute the Bessel function.
    Returns:
    float: The value of the Bessel function of the first kind of order n at point x.
    """
    if n == 0:
        return si.special.j0(x)
    elif n == 1:
        return si.special.j1(x)
    else:
        return si.special.jn(n, x)
@safe_compute
def spherical_bessel_function(n, x):
    """
    Compute the spherical Bessel function of the first kind of order n at a given point x.
    Parameters:
    n (int): The order of the spherical Bessel function.
    x (float): The point at which to compute the spherical Bessel function.
    Returns:
    float: The value of the spherical Bessel function of the first kind of order n at point x.
    """
    if n == 0:
        return si.special.spherical_jn(0, x)
    elif n == 1:
        return si.special.spherical_jn(1, x)
    else:
        return si.special.spherical_jn(n, x)
@safe_compute
def heat_equation_solution(initial_condition, x, t):
    """
    Compute the solution to the heat equation with a given initial condition at a point (x, t).
    Parameters:
    initial_condition (callable): The initial condition function.
    x (float): The spatial coordinate.
    t (float): The time coordinate.
    Returns:
    float: The value of the solution to the heat equation at point (x, t).
    """
    # Example implementation using separation of variables and Fourier series
    n_terms = 100  # Number of terms in the Fourier series
    L = 1  # Length of the spatial domain
    solution = 0
    for n in range(1, n_terms + 1):
        An = 2 / L * si.integrate.quad(lambda s: initial_condition(s) * np.sin(n * np.pi * s / L), 0, L)[0]
        solution += An * np.exp(-n**2 * np.pi**2 * t / L**2) * np.sin(n * np.pi * x / L)
    return solution
@safe_compute
def wave_equation_solution(initial_displacement, initial_velocity, x, t):
    """
    Compute the solution to the wave equation with given initial displacement and velocity at a point (x, t).
    Parameters:
    initial_displacement (callable): The initial displacement function.
    initial_velocity (callable): The initial velocity function.
    x (float): The spatial coordinate.
    t (float): The time coordinate.
    Returns:
    float: The value of the solution to the wave equation at point (x, t).
    """
    # Example implementation using separation of variables and Fourier series
    n_terms = 100  # Number of terms in the Fourier series
    L = 1  # Length of the spatial domain
    solution = 0
    for n in range(1, n_terms + 1):
        An = 2 / L * si.integrate.quad(lambda s: initial_displacement(s) * np.sin(n * np.pi * s / L), 0, L)[0]
        Bn = 2 / (n * np.pi) * si.integrate.quad(lambda s: initial_velocity(s) * np.sin(n * np.pi * s / L), 0, L)[0]
        solution += (An * np.cos(n * np.pi * t / L) + Bn * np.sin(n * np.pi * t / L)) * np.sin(n * np.pi * x / L)
    return solution
@safe_compute
def solve_differential_equation(equation, initial_conditions, x):
    """
    Solve a differential equation with given initial conditions at a point x.
    Parameters:
    equation (callable): The function representing the differential equation.
    initial_conditions (array-like): The initial conditions for the differential equation.
    x (float): The point at which to compute the solution.
    Returns:
    float: The value of the solution to the differential equation at point x.
    """
    # Example implementation using scipy's solve_ivp for ordinary differential equations
    from scipy.integrate import solve_ivp
    
    def system(t, y):
        return equation(t, y)
    
    t_span = (0, x)  # Time span for integration
    sol = solve_ivp(system, t_span, initial_conditions, method='RK45')
    
    return sol.y[:, -1]  # Return the solution at the final time point
@safe_compute
def advanced_linear_algebra(matrix):
    """
    Perform advanced linear algebra operations on a given matrix.
    Parameters:
    matrix (array-like): The input matrix for linear algebra operations.
    Returns:
    dict: A dictionary containing results of various linear algebra operations.
    """
    # Example implementation using numpy for linear algebra operations
    results = {}
    
    # Eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    results['eigenvalues'] = eigenvalues
    results['eigenvectors'] = eigenvectors
    
    # Singular Value Decomposition
    U, S, Vh = np.linalg.svd(matrix)
    results['U'] = U
    results['S'] = S
    results['Vh'] = Vh
    
    # Matrix inverse (if the matrix is invertible)
    if np.linalg.det(matrix) != 0:
        results['inverse'] = np.linalg.inv(matrix)
    
    return results
@safe_compute
def gauss_divergence_theorem(vector_field, surface, limits):
    """
    Compute the flux of a vector field through a closed surface using Gauss's divergence theorem.
    Parameters:
    vector_field (callable): The vector field for which to compute the flux.
    surface (callable): The closed surface through which to compute the flux.
    limits (list): Integration limits for the volume.
    Returns:
    float: The value of the flux of the vector field through the surface.
    """
    # Example implementation using numerical integration
    from scipy.integrate import nquad
    
    def integrand(x, y, z):
        return np.dot(vector_field(x, y, z), surface(x, y, z))
    
    flux = nquad(integrand, limits)[0]
    
    return flux
@safe_compute
def stokes_theorem(vector_field, curve, surface, limits):
    """
    Compute the circulation of a vector field around a closed curve using Stokes' theorem.
    Parameters:
    vector_field (callable): The vector field for which to compute the circulation.
    curve (callable): The closed curve around which to compute the circulation.
    surface (callable): The surface bounded by the curve.
    limits (list): Integration limits for the surface.
    Returns:
    float: The value of the circulation of the vector field around the curve.
    """
    # Example implementation using numerical integration
    from scipy.integrate import nquad
    
    def integrand(x, y, z):
        return np.dot(vector_field(x, y, z), np.cross(surface(x, y, z), [0, 0, 1]))
    
    circulation = nquad(integrand, limits)[0]
    
    return circulation
@safe_compute
def greens_theorem(vector_field, curve, limits):
    """
    Compute the circulation of a vector field around a closed curve using Green's theorem.
    Parameters:
    vector_field (callable): The vector field for which to compute the circulation.
    curve (callable): The closed curve around which to compute the circulation.
    limits (list): Integration limits for the curve.
    Returns:
    float: The value of the circulation of the vector field around the curve.
    """
    # Example implementation using numerical integration
    from scipy.integrate import nquad
    
    def integrand(x, y):
        return np.dot(vector_field(x, y), [0, 0, 1])
    
    circulation = nquad(integrand, limits)[0]
    
    return circulation
@safe_compute
def tensor_operations(tensor1, tensor2):
    """
    Perform various tensor operations on two given tensors.
    Parameters:
    tensor1 (array-like): The first input tensor for operations.
    tensor2 (array-like): The second input tensor for operations.
    Returns:
    dict: A dictionary containing results of various tensor operations.
    """
    # Example implementation using numpy for tensor operations
    results = {}
    
    # Tensor addition
    results['addition'] = np.add(tensor1, tensor2)
    
    # Tensor multiplication (dot product)
    results['dot_product'] = np.tensordot(tensor1, tensor2, axes=([0], [0]))
    
    # Tensor contraction
    results['contraction'] = np.tensordot(tensor1, tensor2, axes=([0, 1], [0, 1]))
    
    return results
all = {
    'validate_values': validate_values,
    'validate_string': validate_string,
    'validate_zeros_negatives': validate_zeros_negatives,
    'safe_int_float': safe_int_float,
    'fourier_series_expansion': fourier_series_expansion,
    'complex_fourier_series': complex_fourier_series,
    'fourier_transform': fourier_transform,
    'inverse_fourier_transform': inverse_fourier_transform,
    'parsevals_theorem': parsevals_theorem,
    'convolution': convolution,
    'legendres_polynomial': legendres_polynomial,
    'laguerre_polynomial': laguerre_polynomial,
    'hermite_polynomial': hermite_polynomial,
    'bessel_function': bessel_function,
    'spherical_bessel_function': spherical_bessel_function,
    'heat_equation_solution': heat_equation_solution,
    'wave_equation_solution': wave_equation_solution,
    'solve_differential_equation': solve_differential_equation,
    'advanced_linear_algebra': advanced_linear_algebra,
    'gauss_divergence_theorem': gauss_divergence_theorem,
    'stokes_theorem': stokes_theorem,
    'greens_theorem': greens_theorem,
    'tensor_operations': tensor_operations
}
