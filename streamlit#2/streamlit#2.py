import numpy as np
import streamlit as st
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

#stream lit

st.set_page_config(page_title = "Force",layout = "centered")

st.title("Force calculator")
st.write("formula is f = ma")
 
button = st.radio(
    "Choose input type",
    ("single values","many values")
)

try:
    if button == "single values":
        m = st.number_input("mass(kg)",min_value = 0.000001)
        a = st.number_input("accelaration",min_value = 0.000001)
        if st.option == ("calculate"):
            force1 = force(m,a)
            st.success("The given force value is F = {force1:.8f} Newton")
        else:
            st.write("give values separated by commas")
            m_text = st.text_input("The values would be", " 1kg,2kg")
            a_text = st.text_input("The values would be"," 1,2,3")
            
            if st.button("Calculate"):
                m_list = [float(x) for x in m_text.split(",")]
                a_list = [float(x) for x in a_text.split(",")]

                force1 = force(m_list, a_list)

                st.success("Force (Newton)")
                st.write(force)
  
                st.line_chart(force)

except Exception as e:
    st.error(str(e))









