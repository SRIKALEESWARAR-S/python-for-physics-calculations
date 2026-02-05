import numpy as np
def spring_force(k,x):
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
        return -k*x
    k = np.array(k,dtype=float)
    x = np.array(u,dtype=float)
    return -k*x
            