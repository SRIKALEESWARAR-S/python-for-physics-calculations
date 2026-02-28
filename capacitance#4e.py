import numpy as np
def capacitance(q,v):
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
    if isinstance(q,(int,float)) and isinstance(v,(int,float)):
        return q/v
    q = np.array(q,dtype=float)
    v = np.array(v,dtype=float)
    return q/v