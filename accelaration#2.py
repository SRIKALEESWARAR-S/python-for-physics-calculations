def accelaration(v,t):
    """
      This function calculates the values of Accelaration
      by taking the diffrent values of velocity and time.
      This function is capable of handling both the file types 
      like iterables and single values.

      kindly enter Non zero values to avoid the ValueError
      use appropraiate file formats and accurate values to 
      avoid the computational errors.

      If any queries or bugs reach us at the forum
    
    
    
    
    """
    if isinstance(v,(int,float)) and isinstance(t,(int,float)):
        if t == 0:
            raise ValueError("The Time values can not be zero")
        return v/t
    if hasattr(v,"__iter__") and hasattr(t,"__iter__"):
        v_list,t_list = list(v),list(t)
        if len(v_list) != len(t_list):
            raise ValueError("we need to have same number of velocity and time values")
        
        accelaration = []
        for i in range(len(v_list)-1):
            dv = v_list[i+1]- v_list[i]
            dt = t_list[i+1] - t_list[i]
            if dt == 0:
                raise ValueError("Time component cant be zero")
            if dv == 0:
                print("Theres no change in velocity,so Accelaration is Zero")
                
            accelaration.append(dv/dt)
        return accelaration
    raise TypeError("Unsupported data types")
print(accelaration(24,56))
print(accelaration([1,27,638,3476.28],[123,7289,789.89,56]))

