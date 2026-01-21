import numpy as np
import streamlit as st

# ---------------- FUNCTION ---------------- #
def force(m, a):
    """
    Compute force using the formula:
    F = m × a

    Parameters
    ----------
    m : float or list/array of float
        Mass in kilograms (kg)
    a : float or list/array of float
        Acceleration in m/s²

    Returns
    -------
    float or numpy.ndarray
        Force in Newtons (N)
    """

    # Scalar case
    if isinstance(m, (int, float)) and isinstance(a, (int, float)):
        if m <= 0 or a <= 0:
            raise ValueError("Mass and acceleration must be positive values")
        return m * a

    # Array case
    m_arr = np.array(m, dtype=float)
    a_arr = np.array(a, dtype=float)

    if m_arr.shape != a_arr.shape:
        raise ValueError("Mass and acceleration must have the same length")

    if np.any(m_arr <= 0) or np.any(a_arr <= 0):
        raise ValueError("All values must be positive")

    return m_arr * a_arr


# ---------------- STREAMLIT UI ---------------- #
st.set_page_config(
    page_title="Force Calculator",
    layout="centered"
)

st.title("Force Calculator")
st.write("### Formula:  **F = m × a**")

mode = st.radio(
    "Choose input type",
    ("Single value", "Multiple values")
)

try:
    # -------- SINGLE VALUE -------- #
    if mode == "Single value":
        m = st.number_input("Mass (kg)", min_value=0.000001)
        a = st.number_input("Acceleration (m/s²)", min_value=0.000001)

        if st.button("Calculate"):
            result = force(m, a)
            st.success(f"Force = {result:.6f} N")

    # -------- MULTIPLE VALUES -------- #
    else:
        st.write("Enter values separated by commas")

        m_text = st.text_input("Mass values (kg)", "1, 2, 3")
        a_text = st.text_input("Acceleration values (m/s²)", "2, 4, 6")

        if st.button("Calculate"):
            m_list = [float(x.strip()) for x in m_text.split(",")]
            a_list = [float(x.strip()) for x in a_text.split(",")]

            result = force(m_list, a_list)

            st.success("Force values (N)")
            st.write(result)
            st.line_chart(result)

except Exception as e:
    st.error(str(e))
