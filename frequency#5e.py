import numpy as np
def frequency(f):
    """_summary_

    Parameters
    ----------
    f : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    if isinstance(f,(int,float)):
        return 2*np.pi*f
    f = np.array(f,dtype=float)
    return 2*np.pi*f
