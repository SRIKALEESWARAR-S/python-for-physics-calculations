import numpy as np
def velocity(x,t):
  """
    This function would able to compute the values 
    of x,dx,t,dt to find the velocity.List,varibles,tuples and 
    other data types are supported

  """
  #varibles with single value
  if isinstance(x, (int, float)) and isinstance(t, (int, float)):
         if t == 0:
            raise ValueError("Time cannot be zero")
         return x / t

    # Case 2: iterables
  x = np.asarray(x, dtype=float)
  t = np.asarray(t, dtype=float)

  if x.shape != t.shape:
        raise ValueError("Position and time must have the same length")

  dx = np.diff(x)
  dt = np.diff(t)

  if np.any(dt == 0):
        raise ValueError("Time difference cannot be zero")

  velocities = dx / dt
  return velocities

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
    #case :2 iterables
    v = np.array(v,dtype=float)
    t = np.array(t,dtype=float)
    if v.shape != t.shape:
        raise TypeError("The arguments should have the same length")
    dv = np.diff(v)
    dt = np.diff(t)
    if any(dt == 0):
        raise ValueError("The time arguments should not be equal to zero")
    accelarations = dv/dt
    return accelarations
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
    if isinstance (t,(int,float)) and (a,(int,float)) and (u,(int,float)):
        if t <= 0 or a <= 0 or u <= 0:
            raise ValueError("the values can not be zero at this point")
        return u+(a*t)
    u = np.array(u,dtype=float)
    t = np.array(t,dtype=float)
    a = np.array(a,dtype=float)
    if u.shape != t.shape or u.shape != a.shape:
        raise TypeError("All the files should have the same length")
    velocity = u+(t*a)
    return velocity
def second_law_motion(u,a,t):
   if isinstance (t,(int,float)) and (a,(int,float)) and (u,(int,float)):
        if t <= 0 or a <= 0 or u <= 0:
            raise ValueError("the values can not be zero at this point")
        return u*t + (0.5*a*t**2)
   u = np.array(u,dtype=float)
   t = np.array(t,dtype=float)
   a = np.array(a,dtype=float)
   if u.shape != t.shape or u.shape != a.shape:
        raise TypeError("All the files should have the same length")
   if any(u <= 0) or any(t <= 0) or any(a<= 0 ):
       raise ValueError("The arguments should not be less than or equal to zero at any point")
   motion = u*t + (0.5*a*t**2)
   return motion
def final_velocity(s,u,a):
    """
    
    """
    if isinstance(s,(int,float)) and isinstance(u,(int,float)) and isinstance(a,(int,,float)):
        if s <= 0 or u <= 0 or a <=0:
            raise ValueError("The values can not be less than or equal to zero")
        v = u**2 + 2*a*s
        return np.sqrt(v)
    s = np.array(s,dtype=float)
    u = np.array(u,dtype=float)
    a = np.array(a,dtype=float)
    if s.shape != u.shape or u.shape != a.shape:
        raise TypeError("The values should be in the same length")
    final_velocitys = u**2 + 2*a*s
    return final_velocitys
def kinematics_displacement(u,v,t):
    if isinstance(u,(int,float)) and isinstance(v,(int,float)) and isinstance(v,(int,float)):
        if u < 0 or v <= 0 or t == 0:
            raise ValueError("The input data values seems like having low or negative values")
        return 
    u = np.array(u,dtype=float)
    v = np.array(v,dtype=float)
    t = np.array(t,dtype=float)
    if u.shape != v.shape or u.shape != t.shape:
        raise TypeError("The arguments should have the same length")
    if any(u <= 0) or any(v <= 0) or any(t <= 0):
        raise ValueError("The values should not be less than or equal to zero")
    displacement = (u+v)*t/2
    return displacement
def initial_velocity(v,a,t):

    """
    """
    if isinstance(v,(int,float)) and isinstance(a,(int,float)) and isinstance(a,(int,float)):
        if v <= 0 or t<= 0 or a <= 0:
            raise ValueError("The arguments can not be zero or negative")
        return v-a*t
    v,a,t = np.array(v,dtype=float),np.array(a,dtype=float),np.array(t,dtype=float)
    if v.shape != a.shape or v.shape != t.shape:
    if any(v <= 0) or any(t <= 0) or any(a <= 0):
        raise ValueError("The arguments should not be less than or equal to zero")
    velocity = v-a*t
    return velocity
def average_accelaration(v,u,t):
    """
    """
    if isinstance(v,(int,float)) and isinstance(u,(int,float)) and isinstance(t,(int,float)):
        if t <= 0 and v < 0 and u < 0:
            raise ValueError("the arguments should not be zero or negative value")
        return (v-u)/t
    v,u,t = np.array(v,dtype=float),np.array(u,dtype=float),np.array(t,dtype=float)
    if v.shape != u.shape or v.shape != t.shape:
        raise TypeError("The arguments should have the same length")
    if any(v <= 0) or any(t <= 0) or any(u <= 0):
        raise ValueError("The arguments should not be less than or equal to zero")
    accelaration = (v-u)/t
    return accelaration
def kinematics_time(v,u,a):
    """
    """
    if isinstance(v,(int,float)) and isinstance(u,(int,float) and isinstance(a,(int,float))):
        if v < 0 or u < 0 or a < 0:
            raise ValueError("Theres a negative value in the input, recheck ")
        return (v-u)/a
    if hasattr(v,"__iter__") and (u,"__iter__") and (a,"__iter__"):
        v_list,u_list,a_list = v,u,a
        if any(v_list <= 0) or any(u_list <= 0) or any(a_list <= 0):
            raise ValueError("The values should not be zero")
        return (v_list-u_list)/v_list
def average_velocity(distance,time):
    """
    """
    if isinstance(time,(int,float)) and isinstance(distance,(int,float)):
        if time <= 0 or distance <= 0:
            raise ValueError("I think some values seems like zero or negative")
        return distance/time
    if hasattr(time,"__iter__") and hasattr(distance,"__iter__"):
        t_list,d_list = time,distance
        if any(t_list <= 0) or any(d_list <= 0):
            raise ValueError("I think some values seems like zero or negative")
        return d_list/t_list
def average_speed(distance,time):
    """
    """
    if isinstance(distance,(int,float)) and isinstance(time,(int,float)):
        if distance <= 0 or time <= 0:
            raise ValueError("I think youre entered a lower value")
        return distance/time
    if hasattr(distance,"__iter__") and hasattr(time,"__iter__"):
        d_list,t_list = distance,time
        if any(d_list <= 0) or any(t_list <= 0):
            raise ValueError("I think you have entered a low value")
        return d_list/t_list
def angular_frequency(theta,time):
    """
    """
    if isinstance(theta,(int,float)) and isinstance(time(int,float)):
        if theta > 360 or time < 0 or theta < 0:
            raise ValueError("Theres a value error please check the values")
        return theta/time
    if hasattr(theta,"__iter__") and hasattr(time,"__iter__"):
        t_list,theta_list = time,theta
        for ti in t_list:
            if ti < 0:
                raise ValueError("Theres some low values. check")
        for di in theta_list:
            if di < 0 or di > 360:
                raise ValueError("The theta values should be from 0 to 360")
        return theta_list/t_list
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
def linear_velocity(r,w):
    """
    """
    if isinstance(r,(int,float)) and isinstance(w,(int,float)):
        if r <= 0 or w <= 0:
            raise ValueError("The values should be greater than 0")
        return r*w
    if hasattr(r,"__iter__") and hasattr(w,"__iter__"):
        r_list,w_list = list(r),list(w)
        for ri,wi in r_list and w_list:
            if ri <= 0 or wi <= 0:
                raise ValueError("The values cant be less than or equal to zero")
        l_velo = []
        l_velo.append(r_list*w_list)
        return l_velo
def force(m,a):
    """
    This code computes the value of force using the formula F=MA
    """
    if isinstance(m,(int,float)) and isinstance(a,(int,float)):
        if m < 0 or a < 0:
            raise ValueError("This values should be greater than 0")
        return m*a
    
    m_arr = np.array(m,d_type = float)
    a_arr = np.array(a,d_type=float)

    if m_arr.shape != a_arr.shape:
        raise ValueError("Both must have same length")
    if np.any(m_arr < 0) or np.any(a_arr < 0):
        raise ValueError("None of the value should be zero")
    return m_arr*a_arr
def weight(m, g):
    """
    Compute force using the formula:
    momentum = m × g

    Parameters
    ----------
    m : float or list/array of float
        Mass in kilograms (kg)
    g : float or list/array of float
        gravity

    Returns
    -------
    float or numpy.ndarray
       weight in (kg)
    """

    # Scalar case
    if isinstance(m, (int, float)) and isinstance(g, (int, float)):
        if m <= 0 or g <= 0:
            raise ValueError("Mass and acceleration must be positive values")
        return m * g

    # Array case
    m_arr = np.array(m, dtype=float)
    g_arr = np.array(g, dtype=float)

    if m_arr.shape != g_arr.shape:
        raise ValueError("Mass and acceleration must have the same length")

    if np.any(m_arr <= 0) or np.any(g_arr <= 0):
        raise ValueError("All values must be positive")

    return m_arr * g_arr 
def momentum(m, v):
    """
    Compute force using the formula:
    momentum = m × v

    Parameters
    ----------
    m : float or list/array of float
        Mass in kilograms (kg)
    v : float or list/array of float
        velocity (m/s)

    Returns
    -------
    float or numpy.ndarray
        momentum in (kg·m/s)
    """

    # Scalar case
    if isinstance(m, (int, float)) and isinstance(v, (int, float)):
        if m <= 0 or v <= 0:
            raise ValueError("Mass and acceleration must be positive values")
        return m * v

    # Array case
    m_arr = np.array(m, dtype=float)
    v_arr = np.array(v, dtype=float)

    if m_arr.shape != v_arr.shape:
        raise ValueError("Mass and acceleration must have the same length")

    if np.any(m_arr <= 0) or np.any(v_arr <= 0):
        raise ValueError("All values must be positive")

    return m_arr * v_arr
def force_momentum(p, t):
    """
    Compute force F = dp / dt
    """

    # Scalar case
    if isinstance(p, (int, float)) and isinstance(t, (int, float)):
        if p <= 0 or t <= 0:
            raise ValueError("values must be greater than zero")

        
        return p / t

    # Iterable case
    p_arr = np.array(p, dtype=float)
    t_arr = np.array(t, dtype=float)

    if p_arr.shape != t_arr.shape:
        raise ValueError("momentum and time must have same length")

    if np.any(p_arr <= 0) or np.any(t_arr <= 0):
        raise ValueError("both should be greater than 0")

   

   
    return p_arr / t_arr
def arc_length(r,theta):
    """
    """
    if isinstance(r,(int,float)) and isinstance(theta,(int,float)):
        if r <= 0 or theta < 0 or theta > 360:
            raise ValueError("""The values should be greater than zero,
                              and theta should be in the range of 0 to 360""")
        theta_rad = np.deg2rad(theta)
        return r*theta_rad
    r_arr = np.array(r,dtype = float)
    theta_arr = np.array(theta,dtype = float)
    if theta_arr.shape != r_arr.shape:
       raise ValueError("The both of the arguments should have same length")
    if np.any(theta_arr < 0) or np.any(theta_arr > 360):
        raise ValueError("Theta value must be in between 0 to 360")
    theta_rad = np.deg2rad(theta_arr)
    return r_arr*theta_rad
def inertia(m,r):
    """
    """
    if isinstance (m,(int,float)) and isinstance(r,(int,float)):
        if m <= 0 or r <= 0:
            raise ValueError("The values should not be less than or equal to 0")
        return m*(r**2)
    m_arr = np.array(m,dtype = float)
    r_arr = np.array(r,dtype = float)
    if m_arr.shape != r_arr.shape:
        raise TypeError("The arguments should be in same length")
    if np.any(m_arr <= 0) or np.any(r_arr <= 0):
        raise ValueError("The arguments should be greater than 0")
    return m_arr*(r_arr**2)
    