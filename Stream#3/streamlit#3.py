import numpy as np
import streamlit as st

# ---------------- FUNCTION ---------------- #
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


# ---------------- STREAMLIT UI ---------------- #
st.set_page_config(
    page_title="Momentum Calculator",
    layout="centered"
)

st.title("Momentum Calculator")
st.write("### Formula:  **p = m × v**")
st.write("Made by Sri kaleeswarar S using Python")

mode = st.radio(
    "Choose input type",
    ("Single value", "Multiple values")
)

try:
    # -------- SINGLE VALUE -------- #
    if mode == "Single value":
        m = st.number_input("Mass (kg)", min_value=0.000001)
        v = st.number_input("velocity(m/s)", min_value=0.000001)

        if st.button("Calculate"):
            result = momentum(m, v)
            st.success(f"momentum = {result:.6f} (kg·m/s)")

    # -------- MULTIPLE VALUES -------- #
    else:
        st.write("Enter values separated by commas")

        m_text = st.text_input("Mass values (kg)", "1, 2, 3")
        v_text = st.text_input("velocity values (m/s)", "2, 4, 6")

        if st.button("Calculate"):
            m_list = [float(x.strip()) for x in m_text.split(",")]
            v_list = [float(x.strip()) for x in v_text.split(",")]

            result = momentum(m_list, v_list)

            st.success("The momentum values ((kg·m/s))")
            st.write(result)
            st.line_chart(result)

except Exception as e:
    st.error(str(e))
