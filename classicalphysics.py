import numpy as np
from .error_handler import validator
@validator("x","t")
def velocity(x,t):
  """
   Compute velocity from position and time.

For scalar inputs, velocity is calculated as v = x / t.
For iterable inputs, velocity is computed using finite differences:
v = Δx / Δt.

Parameters
----------
x : float or array-like
    Position value(s).
t : float or array-like
    Time value(s).

Returns
-------
float or numpy.ndarray
    Velocity value(s).

Raises
------
ValueError
    If time or time differences are zero.
ValueError
    If input arrays have mismatched lengths.

  """
  #varibles with single value
  if isinstance(x, (int, float)) and isinstance(t, (int, float)):
         if t == 0:
            raise ValueError("Time cannot be zero")
         return x / t

    # Case 2: iterables
  x = np.array(x, dtype=float)
  t = np.array(t, dtype=float)

  if x.shape != t.shape:
        raise ValueError("Position and time must have the same length")

  dx = np.diff(x)
  dt = np.diff(t)

  if np.any(dt == 0):
        raise ValueError("Time difference cannot be zero")

  velocities = dx / dt
  return velocities
@validator("v","t")
def accelaration(v,t):
    """
     Compute acceleration from velocity and time.

For scalar inputs, acceleration is calculated as a = v / t.
For iterable inputs, acceleration is computed using finite differences:
a = Δv / Δt.

Parameters
----------
v : float or array-like
    Velocity value(s).
t : float or array-like
    Time value(s).

Returns
-------
float or numpy.ndarray
    Acceleration value(s).

Raises
------
ValueError
    If time or time differences are zero.
TypeError
    If input arrays have mismatched lengths.
  
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
    if np.any(dt == 0):
        raise ValueError("The time arguments should not be equal to zero")
    accelarations = dv/dt
    return accelarations
@validator("u","a","t")
def velocity_at_const_accelaration(u,a,t):
    """ 
      Compute final velocity under constant acceleration.

Uses the kinematic equation:
v = u + at

Parameters
----------
u : float or array-like
    Initial velocity.
a : float or array-like
    Constant acceleration.
t : float or array-like
    Time interval.

Returns
-------
float or numpy.ndarray
    Final velocity.

Raises
------
ValueError
    If any input value is zero or negative.
TypeError
    If input arrays have mismatched lengths.
    """
    
    if isinstance (t,(int,float)) and isinstance(a,(int,float)) and isinstance(u,(int,float)):
        if t <= 0:
            raise ValueError("the values can not be zero at this point")
        return u+(a*t)
    u = np.array(u,dtype=float)
    t = np.array(t,dtype=float)
    a = np.array(a,dtype=float)
    if u.shape != t.shape or u.shape != a.shape:
        raise TypeError("All the files should have the same length")
    if t <= 0:
      raise v
    velocity = u+(t*a)
    return velocity
@validator("u","a","t")
def second_law_motion(u,a,t):
  """
  Compute displacement using the second equation of motion.

Uses the formula:
s = ut + (1/2)at²

Parameters
----------
u : float or array-like
    Initial velocity.
a : float or array-like
    Acceleration.
t : float or array-like
    Time.

Returns
-------
float or numpy.ndarray
    Displacement.

Raises
------
ValueError
    If any input value is zero or negative.
TypeError
    If input arrays have mismatched lengths.
    """
   if isinstance (t,(int,float)) and isinstance(a,(int,float)) and isinstance(u,(int,float)):
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
@validator("s","u","a")
def final_velocity(s,u,a):
    """
    Compute final velocity using the third equation of motion.

Uses the formula:
v² = u² + 2as

Parameters
----------
s : float or array-like
    Displacement.
u : float or array-like
    Initial velocity.
a : float or array-like
    Acceleration.

Returns
-------
float or numpy.ndarray
    Final velocity (or velocity squared for arrays).

Raises
------
ValueError
    If any input value is zero or negative.
TypeError
    If input arrays have mismatched lengths.
    
    """
    if isinstance(s,(int,float)) and isinstance(u,(int,float)) and isinstance(a,(int,float)):
        if s <= 0 or u <= 0 or a <=0:
            raise ValueError("The values can not be less than or equal to zero")
        v = u**2 + 2*a*s
        return np.sqrt(v)
    s = np.array(s,dtype=float)
    u = np.array(u,dtype=float)
    a = np.array(a,dtype=float)
    if s.shape != u.shape or u.shape != a.shape:
        raise TypeError("The values should be in the same length")
    final_velocitys = np.sqrt(u**2 + 2*a*s)
    return final_velocitys
def kinematics_displacement(u,v,t):
  """
  Compute displacement using average velocity.

Uses the formula:
s = (u + v)t / 2

Parameters
----------
u : float or array-like
    Initial velocity.
v : float or array-like
    Final velocity.
t : float or array-like
    Time.

Returns
-------
float or numpy.ndarray
    Displacement.

Raises
------
ValueError
    If inputs contain zero or negative values.
TypeError
    If input arrays have mismatched lengths.
  """
    if isinstance(u,(int,float)) and isinstance(v,(int,float)) and isinstance(t,(int,float)):
        if u < 0 or v <= 0 or t == 0:
            raise ValueError("The input data values seems like having low or negative values")
        return (u+v)*t/2
    u = np.array(u,dtype=float)
    v = np.array(v,dtype=float)
    t = np.array(t,dtype=float)
    if u.shape != v.shape or u.shape != t.shape:
        raise TypeError("The arguments should have the same length")
    if any(u <= 0) or any(v <= 0) or any(t <= 0):
        raise ValueError("The values should not be less than or equal to zero")
    displacement = (u+v)*t/2
    return displacement
@validator("v","a","t")
def initial_velocity(v,a,t):

   """
Compute initial velocity from final velocity, acceleration, and time.

Uses the formula:
u = v − at

Parameters
----------
v : float or array-like
    Final velocity.
a : float or array-like
    Acceleration.
t : float or array-like
    Time.

Returns
-------
float or numpy.ndarray
    Initial velocity.

Raises
------
ValueError
    If inputs contain zero or negative values.
TypeError
    If input arrays have mismatched lengths.
"""

    if isinstance(v,(int,float)) and isinstance(a,(int,float)) and isinstance(t,(int,float)):
        if v <= 0 or t<= 0 or a <= 0:
            raise ValueError("The arguments can not be zero or negative")
        return v-a*t
    v,a,t = np.array(v,dtype=float),np.array(a,dtype=float),np.array(t,dtype=float)
    if v.shape != a.shape or v.shape != t.shape:
      raise TypeError("The arguments should have the same length")
    if any(v <= 0) or any(t <= 0) or any(a <= 0):
        raise ValueError("The arguments should not be less than or equal to zero")
    velocity = v-a*t
    return velocity
def average_acceleration(v,u,t):
   """
Compute average acceleration.

Uses the formula:
a = (v − u) / t

Parameters
----------
v : float or array-like
    Final velocity.
u : float or array-like
    Initial velocity.
t : float or array-like
    Time interval.

Returns
-------
float or numpy.ndarray
    Average acceleration.

Raises
------
ValueError
    If inputs contain zero or negative values.
TypeError
    If input arrays have mismatched lengths.
"""

    if isinstance(v,(int,float)) and isinstance(u,(int,float)) and isinstance(t,(int,float)):
        if t <= 0 or v < 0 or u < 0:
            raise ValueError("the arguments should not be zero or negative value")
        return (v-u)/t
    v,u,t = np.array(v,dtype=float),np.array(u,dtype=float),np.array(t,dtype=float)
    if v.shape != u.shape or v.shape != t.shape:
        raise TypeError("The arguments should have the same length")
    if np.any(v <= 0) or np.any(t <= 0) or np.any(u <= 0):
        raise ValueError("The arguments should not be less than or equal to zero")
    acceleration = (v-u)/t
    return acceleration
@validator("v","u","a")
def kinematics_time(v,u,a):
    """
Compute time using velocity and acceleration.

Uses the formula:
t = (v − u) / a

Parameters
----------
v : float or array-like
    Final velocity.
u : float or array-like
    Initial velocity.
a : float or array-like
    Acceleration.

Returns
-------
float or numpy.ndarray
    Time.

Raises
------
ValueError
    If inputs contain negative values.
"""

    if isinstance(v,(int,float)) and isinstance(u,(int,float) and isinstance(a,(int,float)):
        if v < 0 or u < 0 or a < 0:
            raise ValueError("Theres a negative value in the input, recheck ")
        return (v-u)/a
    if hasattr(v,"__iter__") and hasattr(u,"__iter__") and hasattr(a,"__iter__"):
        v_list,u_list,a_list = v,u,a
        if any(v_list <= 0) or any(u_list <= 0) or any(a_list <= 0):
            raise ValueError("The values should not be zero")
        return (v_list-u_list)/a_list
@validator("distance","time")
def average_velocity(distance,time):
    """
Compute average velocity.

Uses the formula:
v_avg = distance / time

Parameters
----------
distance : float or array-like
    Total displacement.
time : float or array-like
    Total time.

Returns
-------
float or numpy.ndarray
    Average velocity.

Raises
------
ValueError
    If inputs contain zero or negative values.
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

@validator("distance","time")
def average_speed(distance,time):
    """
Compute average speed.

Uses the formula:
speed = distance / time

Parameters
----------
distance : float or array-like
    Total distance travelled.
time : float or array-like
    Time taken.

Returns
-------
float or numpy.ndarray
    Average speed.

Raises
------
ValueError
    If inputs contain zero or negative values.
"""

    if isinstance(distance,(int,float)) and isinstance(time,(int,float)):
        if distance <= 0 or time <= 0:
            raise ValueError("I think youre entered a lower value")
        return distance/time
    if hasattr(distance,"__iter__") and hasattr(time,"__iter__"):
        d_list,t_list = distance,time
        if np.any(d_list <= 0) or np.any(t_list <= 0):
            raise ValueError("I think you have entered a low value")
        return d_list/t_list
@validator("theta","time")
def angular_frequency(theta,time):
    """
Compute angular frequency.

Uses the formula:
ω = θ / t

Parameters
----------
theta : float or array-like
    Angular displacement in degrees.
time : float or array-like
    Time interval.

Returns
-------
float or numpy.ndarray
    Angular frequency.

Raises
------
ValueError
    If theta is outside 0–360 degrees or time is negative.
"""

    if isinstance(theta,(int,float)) and isinstance(time,(int,float)):
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
@validator("omega","time")
def alpha(omega,time):
    """
Compute angular acceleration.

Uses the formula:
α = Δω / Δt

Parameters
----------
omega : float or array-like
    Angular velocity.
time : float or array-like
    Time.

Returns
-------
float or numpy.ndarray
    Angular acceleration.

Raises
------
ValueError
    If inputs contain zero or negative values.
"""

    if isinstance(omega,(int,float)) and isinstance(time,(int,float)):
        if omega <= 0 or time <= 0:
            raise ValueError("The arguments should not be less than zero")
        return omega/time
    if hasattr(omega,"__iter__") and hasattr(time,"__iter__"):
        omega_list,t_list = list(omega),list(time)
        if len(omega_list) != len(t_list):
           raise IndexError("Both of the arguments have the same length")
        if np.any(omega_list <= 0) or np.any(t_list <= 0):
            raise("Value ERROR due to low value arguments")
           
        alphas  = []
        for i in range(len(omega_list) - 1):
            da = omega_list[i + 1] - omega_list[i]
            dt = t_list[i + 1] - t_list[i]
            alphas.append(da/dt)

        return alphas
@validator("v","w")
def linear_velocity(r,w):
    """
Compute linear velocity from angular velocity.

Uses the formula:
v = rω

Parameters
----------
r : float or array-like
    Radius.
w : float or array-like
    Angular velocity.

Returns
-------
float or numpy.ndarray
    Linear velocity.

Raises
------
ValueError
    If inputs contain zero or negative values.
"""

    if isinstance(r,(int,float)) and isinstance(w,(int,float)):
        if r <= 0 or w <= 0:
            raise ValueError("The values should be greater than 0")
        return r*w
    if hasattr(r,"__iter__") and hasattr(w,"__iter__"):
        r_list,w_list = list(r),list(w)
        if np.any(r_list <= 0) or np.any(w_list <= 0):
                raise ValueError("The values cant be less than or equal to zero")
        l_velo = []
        l_velo.append(r_list*w_list)#has to revise the code in the next version
        return l_velo#runtime issues
@validator("m","a")
def force(m,a):
    """
Compute force using Newton’s second law.

Uses the formula:
F = ma

Parameters
----------
m : float or array-like
    Mass.
a : float or array-like
    Acceleration.

Returns
-------
float or numpy.ndarray
    Force.

Raises
------
ValueError
    If inputs contain negative values.
"""

    if isinstance(m,(int,float)) and isinstance(a,(int,float)):
        if m < 0 or a < 0:
            raise ValueError("This values should be greater than 0")
        return m*a
    
    m_arr = np.array(m,dtype = float)
    a_arr = np.array(a,dtype=float)

    if m_arr.shape != a_arr.shape:
        raise ValueError("Both must have same length")
    if np.any(m_arr <= 0) or np.any(a_arr <= 0):
        raise ValueError("None of the value should be zero or negative")
    return m_arr*a_arr
validator("m","g")
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
@validator("m","v")
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
            raise ValueError("Mass and velocity must be positive values")
        return m * v

    # Array case
    m_arr = np.array(m, dtype=float)
    v_arr = np.array(v, dtype=float)

    if m_arr.shape != v_arr.shape:
        raise ValueError("Mass and velocity must have the same length")

    if np.any(m_arr <= 0) or np.any(v_arr <= 0):
        raise ValueError("All values must be positive")

    return m_arr * v_arr
@validator("p","t")
def force_momentum(p, t):
    """
Compute force from rate of change of momentum.

Uses the formula:
F = dp / dt

Parameters
----------
p : float or array-like
    Momentum.
t : float or array-like
    Time interval.

Returns
-------
float or numpy.ndarray
    Force.

Raises
------
ValueError
    If inputs contain zero or negative values.
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
@validator("r","theta")
def arc_length(r,theta):
    """
Compute arc length of a circle.

Uses the formula:
s = rθ

Parameters
----------
r : float or array-like
    Radius.
theta : float or array-like
    Angle in degrees.

Returns
-------
float or numpy.ndarray
    Arc length.

Raises
------
ValueError
    If theta is outside 0–360 degrees.
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
@validator("m","r")
def inertia(m,r):
    """
Compute moment of inertia of a point mass.

Uses the formula:
I = mr²

Parameters
----------
m : float or array-like
    Mass.
r : float or array-like
    Radius.

Returns
-------
float or numpy.ndarray
    Moment of inertia.

Raises
------
ValueError
    If inputs contain zero or negative values.
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
    
