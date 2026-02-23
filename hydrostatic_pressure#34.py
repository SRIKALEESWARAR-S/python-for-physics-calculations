import numpy as np
def hydrostatic_pressure(p,g,h):
    """_summary_

    Parameters
    ----------
    p : _type_
        _description_
    g : _type_
        _description_
    h : _type_
        _description_
    """
    if isinstance(p,(int,float)) and isinstance(g,(int,float)) and isinstance(h,(int,float)):
        return p*g*h
    p = np.array(p,dtype=float)
    g = np.array(g,dtype=float)
    h = np.array(h,dtype=float)
    return p*g*h