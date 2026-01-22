import streamlit as st
import numpy as np

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

    if np.any(p_arr <= 0) or np.any(t_arr <= 360):
        raise ValueError("both should be greater than 0")

   

   
    return p_arr / t_arr


# ---------------- STREAMLIT UI ---------------- #

st.set_page_config(page_title="force using momentum Calculator", layout="centered")

st.title("force Calculator")
st.write("Formula:  f = dp / dt  (t in seconds)")

mode = st.radio(
    "Choose input type",
    ("Single value", "Multiple values")
)

try:
    if mode == "Single value":
        p = st.number_input("momentum (kg·m/s)", min_value=0.0)
        t = st.number_input("Time (seconds)", min_value=0.0001)

        if st.button("Calculate"):
            result = force_momentum(p, t)
            st.success(f"force = {result:.4f} N")

    else:
        st.write("Enter values separated by commas")

        p_text = st.text_input("momentum values (kg·m/s)", "9, 1, 70")
        t_text = st.text_input("Time values (seconds)", "1, 2, 3")

        if st.button("Calculate"):
            p_list = [float(x) for x in p_text.split(",")]
            t_list = [float(x) for x in t_text.split(",")]

            result = force_momentum(p_list, t_list)

            st.success("Force(N)")
            st.write(result)

            st.line_chart(result)

except Exception as e:
    st.error(str(e))