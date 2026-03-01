import numpy as np
def current_density(n,q,v):
    """_summary_

    Parameters
    ----------
    n : _type_
        _description_
    q : _type_
        _description_
    v : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    if isinstance(n,(int,float)) and isinstance(v,(int,float)) and isinstance(q,(int,float)):
        return n*q*v
    n = np.array(n,dtype=float)
    v = np.array(v,dtype=float)
    q = np.array(q,dtype=float)
    return n*q*v