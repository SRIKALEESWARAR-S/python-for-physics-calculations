import numpy as np
import streamlit as st

# ---------------- FUNCTION ---------------- #
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


# ---------------- STREAMLIT UI ---------------- #
st.set_page_config(
    page_title="Weight Calculator",
    layout="centered"
)

st.title("weight Calculator")
st.write("### Formula:  **w = m × g**")
st.write("Made by Sri kaleeswarar S using Python")

mode = st.radio(
    "Choose input type",
    ("Single value", "Multiple values")
)

try:
    # -------- SINGLE VALUE -------- #
    if mode == "Single value":
        m = st.number_input("Mass (kg)", min_value=0.000001)
        v = st.number_input("gravity", min_value=0.000001)

        if st.button("Calculate"):
            result = weight(m, v)
            st.success(f"weight = {result:.6f} (kg)")

    # -------- MULTIPLE VALUES -------- #
    else:
        st.write("Enter values separated by commas")

        m_text = st.text_input("Mass values (kg)", "1, 2, 3")
        g_text = st.text_input("gravity", "2, 4, 6")

        if st.button("Calculate"):
            m_list = [float(x.strip()) for x in m_text.split(",")]
            g_list = [float(x.strip()) for x in g_text.split(",")]

            result = weight(m_list, g_list)

            st.success("Theweight values  ((kg))")
            st.write(result)
            st.line_chart(result)

except Exception as e:
    st.error(str(e))