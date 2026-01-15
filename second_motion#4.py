def second_law_motion(u,a,t):
    if isinstance(t,(int,float)):
         if t == 0:
              raise ValueError("Time can not be zero at this point")
         return u*t + (0.5*a*t**2)
    displacement = []
    for ti in t:
         if ti == 0:
              raise ValueError("Time components cant be zero")
         displacement.append(u*ti +(0.5*a*ti**2))
    return displacement
         