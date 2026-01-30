import numpy as np
def period_mass_spring_system(m,k):
    """_summary_

    Parameters
    ----------
    m : _type_
        _description_
    k : _type_
        _description_
    """
    if isinstance(m,(int,float)) and isinstance(k,(int,float)):
        if m <= 0 or k <= 0:
            raise ValueError("The values should be greater than zero")
        return 2*3.14*np.sqrt(m/k)
    m = np.array(m,dtype=float)
    k = np.array(k,dtype=float)
    if m.shape != k.shape:
        raise TypeError("Both of the arguments should have same length")
    if np.any(m <=0) or np.any(k <= 0):
        raise ValueError("The values should be greater than 0")
    return 2*3.14*np.sqrt(m/k)
