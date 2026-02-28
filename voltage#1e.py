import numpy as np
def voltage(i,r):
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
    if isinstance(i,(int,float)) and isinstance(r,(int,float)):
        return i*r
    i = np.array(i,dtype=float)
    r = np.array(r,dtype=float)
    return i*r