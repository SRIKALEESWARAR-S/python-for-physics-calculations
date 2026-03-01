import numpy as np
def capacitor_potential(c,v):
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
    if isinstance(c,(int,float)) and isinstance(v,(int,float)) 
        return 0.5*c*v**2
    c = np.array(c,dtype=float)
    v = np.array(v,dtype=float)
    
    return 0.5*c*v**2