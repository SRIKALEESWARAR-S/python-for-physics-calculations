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