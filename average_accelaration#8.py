def average_accelaration(v,u,t):
    """
    """
    if isinstance(v,(int,float)) and isinstance(u,(int,float)) and isinstance(t,(int,float)):
        if t <= 0 and v < 0 and u < 0:
            raise ValueError("the arguments should not be zero or negative value")
        return (v-u)/t
    if hasattr(v,(int,float)) and hasattr(u,(int,float)) and hasattr(t,(int,float)):
        v_list,u_list,t_list = v,u,t
        if v_list < 0 or u_list < 0 or t_list <= 0:
            raise ValueError("The aruguments should have positive values")
        accelaration = []
        for ti in t:
            if ti <= 0:
                raise ValueError("The time values should not be zero or negative")
            accelaration.append((v_list-u_list/t_list))
        return accelaration
    