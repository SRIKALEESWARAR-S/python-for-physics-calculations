import numpy as np
def friction_kinetic(u,n):
    """_summary_

    Parameters
    ----------
    u : _type_
        _description_
    n : _type_
        _description_
    """
    if isinstance(u,(int,float)) and isinstance(n,(int,float)):
        return u*n
    u = np.array(u,dtype=float)
    n = np.array(n,dtype=float)
    return u*n