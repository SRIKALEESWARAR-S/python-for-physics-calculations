
def average_velocity(distance,time):
    """
    """
    if isinstance(time,(int,float)) and isinstance(distance,(int,float)):
        if time <= 0 or distance <= 0:
            raise ValueError("I think some values seems like zero or negative")
        return distance/time
    if hasattr(time,"__iter__") and hasattr(distance,"__iter__"):
        t_list,d_list = time,distance
        if t_list <= 0 or d_list <= 0:
            raise ValueError("I think some values seems like zero or negative")
        return d_list/t_list
    
    


