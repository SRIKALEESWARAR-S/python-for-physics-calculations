import numpy as np
def Nyquist_rate(f,m):
    """_summary_

    Parameters
    ----------
    f : _type_
        _description_
    m : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    if isinstance(f,(int,float)) and isinstance(m,(int,float)):
        return 2*f*m
    f = np.array(f,dtype=float)
    m = np.array(m,dtype=float)
    return 2*f*m