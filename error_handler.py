import numpy as np
def error_handler(x,name = "Value"):#finds 
    """
    """
    if x is None:
        raise ValueError(f"The input {name} arguments should not be None")
    
    if isinstance(x,str):# finds string input and empty string
        if x == "":
            raise ValueError("The values should not be a empty string")

        raise TypeError(f"The {name} argument should not be string,it must be number")
    if isinstance(x,tuple,list):
        if len(x) == 0:
            raise ValueError(f"The {name} list or tuple should not be zero")
        x = np.array(x,dtype=float)
    if isinstance(x,np.ndarray):
        if x.size == 0:
            raise ValueError(f"The {name} numpy array cant be zero")
        if not np.all(np.isfinite(x)):
            raise ValueError(f"The {name} values should be finite ")
        return x
    if isinstance(x, (int, float)):
        if not np.isfinite(x):
            raise ValueError(f"{name} contains NaN or Inf")
        return x

    # Anything else
    raise TypeError(f"{name} has invalid type: {type(x)}")
        

