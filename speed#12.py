def average_speed(distance,time):
    """
    """
    if isinstance(distance,(int,float)) and isinstance(time,(int,float)):
        if distance <= 0 or time <= 0:
            raise ValueError("I think youre entered a lower value")
        return distance/time
    if hasattr(distance,"__iter__") and hasattr(time,"__iter__"):
        d_list,t_list = distance,time
        if d_list <= 0 or t_list <= 0:
            raise ValueError("I think you have entered a low value")
        return d_list/t_list
    