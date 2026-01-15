def kinematics_displacement(u,v,t):
    if isinstance(u,(int,float)) and isinstance(v,(int,float)) and isinstance(v,(int,float)):
        if u < 0 or v <= 0 or t == 0:
            raise ValueError("The input data values seems like having low or negative values")
        return (u+v)*t/2
    if hasattr(u,"__iter__") and hasattr(v,"__iter__") and hasattr(t,"__iter__"):
        u_list,v_list,t_list = u,v,t
        if len(u_list) != len(v_list) and len(v_list) != len(t_list):
            raise ValueError(" Both of them must have same number of input data values")
        displacement = []
        for ti in t_list:
            if ti <= 0:
                raise ValueError("The time values should't be less than zero or zero ")
            displacement.append((u_list+v_list)*t_list/2)
        return displacement
    

        