import numpy as np
def orbital_period(m,g,r):
    
    if isinstance(r,(int,float)) and isinstance(m,(int,float)) and isinstance(g,(int,float)):
        if m <= 0 or r <= 0 or g<= 0:
            raise ValueError("The values should be greater than zero")
        return 2*3.14*np.sqrt(r**3/g*m)
    m = np.array(m,dtype=float)
    r = np.array(r,dtype=float)
    g = np.array(g,dtype=float)
    if m.shape != g.shape or g.shape != r.shape:
        raise TypeError("Both of the arguments should have same length")
    if np.any(m <=0) or np.any(g <= 0) or np.any(r<=0):
        raise ValueError("The values should be greater than 0")
    return 2*3.14*np.sqrt(r**3/g*m)
