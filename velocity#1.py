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
  if hasattr(x, "__iter__") and hasattr(t, "__iter__"):
        x_list = list(x)
        t_list = list(t)

        if len(x_list) != len(t_list):
            raise ValueError("Position and time must have the same length")

        velocities = []
        for i in range(len(x_list) - 1):
            dx = x_list[i + 1] - x_list[i]
            dt = t_list[i + 1] - t_list[i]

            if dt == 0:
                raise ValueError("Time difference cannot be zero")

            velocities.append(dx / dt)

        return velocities
        
        raise TypeError("Unsupported data types")
print(velocity(5,6))