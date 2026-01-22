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