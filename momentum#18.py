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
