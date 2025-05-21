import streamlit as st
from utils import discount_cash_flows

def show():
    st.header("💸 Méthode DCF (Discounted Cash Flow)")
    st.markdown("""
        Cette méthode repose sur l’actualisation des flux de trésorerie futurs générés par l’entreprise. 
        Elle permet d’estimer la valeur actuelle nette de ces flux futurs.
    """)
    years = st.number_input("Nombre d'années de prévision", min_value=1, max_value=10, value=5)
    cash_flows = []

    for i in range(1, years + 1):
        cf = st.number_input(f"Flux de trésorerie pour l'année {i} ($)", key=f"cf_{i}", step=1000.0)
        cash_flows.append(cf)

    discount_rate = st.slider("Taux d'actualisation (%)", min_value=0.0, max_value=20.0, value=10.0) / 100

    if st.button("Calculer la valeur actualisée"):
        value = discount_cash_flows(cash_flows, discount_rate)
        st.success(f"Valeur estimée de l'entreprise par DCF : ${value:,.2f}")