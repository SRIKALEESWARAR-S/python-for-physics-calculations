def velocity_at_const_accelaration(u,a,t):
    """ 
       This formula calculates the velocity when accelaration 
       is constant. you can give one data inputvalue to the 
       initial velocity and accelaration. you can compute the formula
       for varies time values.
       You can give time as a instance(single value) or as a 
       iterable(list,tuples etc). avoid giving time = 0 to
       avoid the value errors.
       if you're facing any bugs/issues kindly reach us at the forum. 
    """
    if isinstance (t,(int,float)):
        if t <= 0:
            raise ValueError("Time can not be zero at this point")
        return u+(a*t)
    velocities = []
    for ti in t:
        velocities.append(u+a*ti)
    return velocities
print(velocity_at_const_accelaration(1,3,7))
print(velocity_at_const_accelaration(1,2,[1,2,3,4,5,6.7,34,56,6787,4567.8899]))