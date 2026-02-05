import numpy as np
def inclined_plane_accelaration(u,g,theta):
    """_summary_

    Parameters
    ----------
    u : _type_
        _description_
    g : _type_
        _description_
    theta : _type_
        _description_

    Returns
    -------
    _type_
        _description_

    Raises
    ------
    ValueError
        _description_
    """
    if isinstance(u,(int,float)) and isinstance(g,(int,float)) and isinstance(g,(int,float)):
        if u <= 0 or g <= 0 or theta <= 0 or theta > 90:
            raise ValueError("The values are in a out of range!!! ")
        return g*(np.sin(theta))-u*np.cos(theta)
    u = np.array(u,dtype=float)
    g = np.array(g,dtype=float)
    theta = np.array(theta,dtype=float)
    return g*(np.sin(theta))-u*np.cos(theta)
            