import numpy as np 
def static_friction(u,n):
    """_summary_

    Parameters
    ----------
    u : _type_
        _description_
    n : _type_
        _description_
    """
    if isinstance(u,(int,float)) and isinstance(n,(int,float)):
        if u <= 0 or n <= 0:
            raise ValueError("The arguments can not be zero or less than zero")
        return u*n
    u = np.array(u,dtype=float)
    n = np.array(n,dtype=float)
    if u <= 0 or n <= 0:
        raise ValueError("The arguments can not be zero or less than zero")
    return u*n
    
