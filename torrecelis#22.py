import numpy as np
def torricellis_formula(g,h):
    """_summary_

    Parameters
    ----------
    g : _type_
        _description_
    h : _type_
        _description_
    """
    if isinstance(g,(int,float)) and isinstance(h,(int,float)):
        if g <= 0 or h <= 0:
            raise ValueError("The arguments should be greater than zero!!!")
        return np.sqrt(2*g*h)
    g = np.array(g,dtype=float)
    h = np.array(h,dtype=float)
    if g.shape != h.shape:
        raise TypeError("both of the arguments should have the same length")
    if np.any(g <= 0) or np.any(h <= 0):
        raise ValueError("The arguments should greater than zero")
    return np.sqrt(2*g*h)
    