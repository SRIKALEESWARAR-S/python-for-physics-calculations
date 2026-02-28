import numpy as np
def power(i,v):
    """_summary_

    Parameters
    ----------
    i : _type_
        _description_
    r : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    if isinstance(i,(int,float)) and isinstance(v,(int,float)):
        return i*v
    i = np.array(i,dtype=float)
    v = np.array(v,dtype=float)
    return i*v