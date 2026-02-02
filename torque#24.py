import numpy as np
def torque(r,f,theta):
    if isinstance(r,(int,float)) and isinstance(f,(int,float)) and isinstance(theta,(int,float)):
        if r <= 0 or f <= 0 or theta < 0 or theta > 360:
            raise ValueError("The values should be greater than zero and angle should be less than 360")
        return r*f*(np.sin(theta))
    r = np.array(r,dtype=float)
    f = np.array(f,dtype=float)
    theta = np.array(theta,dtype=float)
    if r.shape != f.shape or theta.shape != f.shape:
        raise TypeError("Both of the values should be in the same length")
    if r <= 0 or f <=0 or theta < 0 or theta > 360:
        raise ValueError("The values should be greater than zero and angle should be less than 360")
    return r*f*(np.sin(theta))