import numpy as np
def spring_pe(k,x):
    """_summary_

    Parameters
    ----------
    k : _type_
        _description_
    x : _type_
        _description_
    """
    if isinstance(k,(int,float)) and isinstance(x,(int,float)):
        if k < 0 or x == 0:
            raise ValueError("The force constant cant be zero lessthan zero and displacement x should not be 0 ")
        return 0.5*k*x**2
    k = np.array(k,dtype=float)
    x = np.array(u,dtype=float)
    return 0.5*k*x**2
            