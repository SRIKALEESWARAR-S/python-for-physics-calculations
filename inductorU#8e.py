import numpy as np
def inductor_potential(l,i):
    """_summary_

    Parameters
    ----------
    l : _type_
        _description_
    i : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    if isinstance(l,(int,float)) and isinstance(i,(int,float)):
        return 0.5*l*i**2
    l = np.array(l,dtype=float)
    i = np.array(i,dtype=float)
    return 0.5*l*i**2