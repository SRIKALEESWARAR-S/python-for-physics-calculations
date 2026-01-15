import math as  m
def final_velocity(s,u,a):
    """
    
    """
    if issubclass(s,(int,float)):
        if s <= 0:
            raise ValueError("The value of displacement can not be zero")
        v = u**2 + 2*a*s
        return m.sqrt(v),v
    velocities = []
    for si in s:
        if si < 0:
            raise ValueError("The displacement value cannot be zero")
        velocities.append(u**2 + 2*a*si)
    return velocities,m.sqrt(velocities)
        
