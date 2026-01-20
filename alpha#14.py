def alpha(omega,time):
    """
    """
    if isinstance(omega,(int,float)) and isinstance(time,(int,float)):
        if omega <= 0 or time <= 0:
            raise ValueError("The arguments should not be less than zero")
        return omega/time
    if hasattr(omega,"__iter__") and hasattr(time,"__iter__"):
        omega_list,t_list = list(omega),list(time)
        if len(omega_list) != len(t_list):
           raise IndexError("Both of the arguments have the same length")
        for oi,ti in omega_list and t_list:

           if oi in omega_list <= 0 or ti in t_list <= 0 :
            raise("Value ERROR due to low value arguments")
           
        alphas  = []
        for i in range(len(omega_list) - 1):
            da = omega_list[i + 1] - omega_list[i]
            dt = t_list[i + 1] - t_list[i]
        alphas.append(da/dt)

        return alphas
