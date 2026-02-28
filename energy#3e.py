import numpy as np
def voltage(p,t):
    """_summary_

    Parameters
    ----------
    p : _type_
        _description_
    t : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    if isinstance(p,(int,float)) and isinstance(t,(int,float)):
        return p*t
    p = np.array(p,dtype=float)
    t = np.array(t,dtype=float)
    return p*t