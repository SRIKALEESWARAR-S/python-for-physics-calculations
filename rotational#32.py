import numpy as np
def rotational_dynamics(i,alpha):
    """_summary_

    Parameters
    ----------
    i : _type_
        _description_
    alpha : _type_
        _description_

    Returns
    -------
    _type_
        _description_

    Raises
    ------
    ValueError
        _description_
    TypeError
        _description_
    ValueError
        _description_
    """
    if isinstance(i,(int,float)) and isinstance(alpha,(int,float)):
        if i <= 0 or alpha <= 0:
            raise ValueError("The values should be greater than zero")
        return i*alpha
    i = np.array(i,dtype=float)
    alpha = np.array(alpha,dtype=float)
    if i.shape != alpha.shape:
        raise TypeError("Both of the arguments should have same length")
    if np.any(alpha <=0) or np.any(i <= 0):
        raise ValueError("The values should be greater than 0")
    return i*alpha
