import numpy as np
def gravitional_field(g,mass,r):
    """_summary_

    Parameters
    ----------
    g : _type_
        _description_
    mass : _type_
        _description_
    r : _type_
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
   
    if isinstance(mass,(int,float)) and isinstance(g,(int,float)) and isinstance(r,(int,float)):
        if r <= 0 or mass <= 0 or g <= 0:
            raise ValueError("The gravity cant be zero less than zero and radius r, masses should not be 0 ")
        return (g*mass)/r
    mass = np.array(mass,dtype=float)
    r = np.array(r,dtype=float)
    g = np.array(g,dtype=float)
    return (g*mass)/r

            