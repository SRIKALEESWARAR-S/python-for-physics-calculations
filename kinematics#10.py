def kinematics_displacement2(v,a,t):
    """
    """
    if isinstance(v,(int,float)) and isinstance(a,(int,float)) and isinstance(t,(int,float)):
        if v < 0 and a < 0 and t <= 0:
            raise ValueError("it seems like you have a entered a negative or zero value")
        return (v*t - 0.5*a*t**2)
    if hasattr(a,"__iter__") and hasattr (v,"__iter__") and hasattr(t,"__iter__"):
        a_list,v_list,t_list = a,v,t 
        if a_list < 0 and v_list < 0 and t_list:
            raise ValueError("It seems like you have entered some lower values ")
        return (v_list*t_list - 0.5*a_list*t_list**2)
