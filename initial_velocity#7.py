import numba
@numba.jit
def initial_velocity(v,a,t):

    """
    """
    if isinstance(v,(int,float)) and isinstance(a,(int,float)) and isinstance(a,(int,float)):
        if v < 0 or t<= 0 or a < 0:
            raise ValueError("The arguments can not be zero or negative")
        return v-a*t
    if hasattr(v,"__iter__") and hasattr(a,"__iter__") and hasattr(t,"__iter__"):
        v_list,a_list,t_list = v,a,t

        for ti in t_list:
            if ti <= 0:
                raise ValueError("The time arguments can not be zero")
        return (v_list-a_list)/t_list
    
            
    