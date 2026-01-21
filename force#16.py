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