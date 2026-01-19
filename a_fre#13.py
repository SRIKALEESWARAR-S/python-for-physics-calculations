def angular_frequency(theta,time):
    """
    """
    if isinstance(theta,(int,float)) and isinstance(time(int,float)):
        if theta > 360 or time < 0 or theta < 0:
            raise ValueError("Theres a value error please check the values")
        return theta/time
    if hasattr(theta,"__iter__") and hasattr(time,"__iter__"):
        t_list,theta_list = time,theta
        for ti in t_list:
            if ti < 0:
                raise ValueError("Theres some low values. check")
        for di in theta_list:
            if di < 0 or di > 360:
                raise ValueError("The theta values should be from 0 to 360")
        return theta_list/t_list
    
        
        
