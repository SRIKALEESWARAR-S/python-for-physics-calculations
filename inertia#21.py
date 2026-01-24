import numpy as np
def inertia(m,r):
    """
    """
    if isinstance (m,(int,float)) and isinstance(r,(int,float)):
        if m <= 0 or r <= 0:
            raise ValueError("The values should not be less than or equal to 0")
        return m*(r**2)
    m_arr = np.array(m,dtype = float)
    r_arr = np.array(r,dtype = float)
    if m_arr.shape != r_arr.shape:
        raise TypeError("The arguments should be in same length")
    if np.any(m_arr <= 0) or np.any(r_arr <= 0):
        raise ValueError("The arguments should be greater than 0")
    return m_arr*(r_arr**2)
    
    

