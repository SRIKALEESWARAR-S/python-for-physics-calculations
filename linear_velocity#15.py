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