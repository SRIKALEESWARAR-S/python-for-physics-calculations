import numpy as np
def density(sigma):
    """_summary_

    Parameters
    ----------
    sigma : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    if isinstance(sigma,(int,float)):
        return 1/sigma
    f = np.array(sigma,dtype=float)
    return 1/sigma