import numpy as np
import functools 
def error_handler(x,name = "Value"):#finds the error 
    """
    Validate a numeric input and raise appropriate errors for invalid values.

    This function performs basic input sanitation for numerical computations.
    It checks for common invalid inputs such as strings, empty containers,
    NaN, infinite values, and unsupported data types. Lists and tuples are
    converted to NumPy arrays for consistency.

    Parameters
    ----------
    x : int, float, list, tuple, or numpy.ndarray
        Input value to be validated.
    name : str, optional
        Name of the variable (used in error messages).
        Default is "Value".

    Returns
    -------
    int, float, or numpy.ndarray
        The validated input. Lists and tuples are returned as NumPy arrays.

    Raises
    ------
    ValueError
        If the input is None, empty, NaN, infinite, or an empty container.
    TypeError
        If the input is a string or an unsupported data type.

    Examples
    --------
    >>> error_handler(10)
    10

    >>> error_handler([1, 2, 3])
    array([1., 2., 3.])

    >>> error_handler(np.inf)
    ValueError: Value contains NaN or Inf

    >>> error_handler("abc")
    TypeError: The Value argument should not be string,it must be number
    """
    if x is None:#None argument
        raise ValueError(f"The input {name} arguments should not be None")
    
    if isinstance(x,str):# finds string input and empty string
        if x == "":
            raise ValueError("The values should not be a empty string")

        raise TypeError(f"The {name} argument should not be string,it must be number")
    if isinstance(x,tuple,list):#empty list
        if len(x) == 0:
            raise ValueError(f"The {name} list or tuple should not be zero")
        x = np.array(x,dtype=float)
    if isinstance(x,np.ndarray):#empty numpy array
        if x.size == 0:
            raise ValueError(f"The {name} numpy array cant be zero")
        if not np.all(np.isfinite(x)):#Non finite Arguments
            raise ValueError(f"The {name} values should be finite ")
        return x
    if isinstance(x, (int, float)):#handles NaN and infitite value errors
        if not np.isfinite(x):
            raise ValueError(f"{name} contains NaN or Inf")
        return x

    # Anything else
    raise TypeError(f"{name} has invalid type: {type(x)}")
        


def validate_inputs(*arg_names):
    """
    Decorator to validate selected positional arguments
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args = list(args)

            for i, name in enumerate(arg_names):
                if i < len(args):
                    args[i] = error_handler(args[i], name)

            return func(*args, **kwargs)
        return wrapper
    return decorator