import numpy as np
def arc_length(r,theta):
    """
    """
    if isinstance(r,(int,float)) and isinstance(theta,(int,float)):
        if r <= 0 or theta < 0 or theta > 360:
            raise ValueError("""The values should be greater than zero,
                              and theta should be in the range of 0 to 360""")
        theta_rad = np.deg2rad(theta)
        return r*theta_rad
    r_arr = np.array(r,dtype = float)
    theta_arr = np.array(theta,dtype = float)
    if theta_arr.shape != r_arr.shape:
       raise ValueError("The both of the arguments should have same length")
    if np.any(theta_arr < 0) or np.any(theta_arr > 360):
        raise ValueError("Theta value must be in between 0 to 360")
    theta_rad = np.deg2rad(theta_arr)
    return r_arr*theta_rad
    