import streamlit as st
from utils import calculate_enterprise_value

def show():
    st.header("🧮 Méthode des Comparables")
    st.markdown("""
        Cette méthode consiste à comparer l'entreprise évaluée à d'autres entreprises similaires 
        pour estimer sa valeur à partir de multiples financiers (ex : multiple d’EBITDA).
    """)
    ebitda = st.number_input("EBITDA de l'entreprise ($)", min_value=0.0, step=1000.0)
    multiple = st.number_input("Multiple de marché (ex: 6x, 8x)", min_value=0.0, step=0.1)

    if st.button("Calculer la valeur"):
        value = calculate_enterprise_value(ebitda, multiple)
        st.success(f"Valeur estimée de l'entreprise : ${value:,.2f}")

