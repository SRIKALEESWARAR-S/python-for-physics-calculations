def kinematics_time(v,u,a):
    """
    """
    if isinstance(v,(int,float)) and isinstance(u,(int,float) and isinstance(q,(int,float))):
        if v < 0 or u < 0 or a < 0:
            raise ValueError("Theres a negative value in the input, recheck ")
        return (v-u)/a
    if hasattr(v,"__iter__") and (u,"__iter__") and (a,"__iter__"):
        v_list,u_list,a_list = v,u,a
        if v_list < 0 or u_list <0 or a_list < 0:
            raise ValueError("The values should not be zero")
        return (v_list-u_list)/v_list
    


        