import streamlit as st

def page_dividendes():
    # Barre de navigation principale (identique à main.py)
    pages = [
        ("Accueil", "🏠"),
        ("Méthode des comparables", "📊"),
        ("Méthode DCF", "💸"),
        ("Méthode des dividendes", "💰")
    ]
    cols = st.columns(len(pages))
    for i, (p, icon) in enumerate(pages):
        if cols[i].button(f"{icon} {p}"):
            st.session_state.page = p
            st.experimental_rerun()

    st.markdown("---")

    st.markdown('<div class="main-title">Méthode des Dividendes (Gordon-Shapiro)</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="info-card">
        <b>Principe :</b> Cette méthode évalue une entreprise selon la valeur actuelle des dividendes futurs attendus, en supposant un taux de croissance constant.<br>
        <b>Formule :</b> <code>Valeur = Dividende / (Taux d'actualisation - Taux de croissance)</code>
        </div>
        """, unsafe_allow_html=True
    )

    with st.form("dividendes_form"):
        dividende = st.number_input("Dividende annuel par action (€)", min_value=0.0, value=2.0, step=0.1)
        taux_croissance = st.number_input("Taux de croissance des dividendes (%)", min_value=0.0, max_value=100.0, value=3.0, step=0.1) / 100
        taux_actualisation = st.number_input("Taux d'actualisation (%)", min_value=0.01, max_value=100.0, value=8.0, step=0.1) / 100
        submitted = st.form_submit_button("Calculer la valeur de l'action")

    if submitted:
        if taux_actualisation <= taux_croissance:
            st.error("Le taux d'actualisation doit être strictement supérieur au taux de croissance.")
        else:
            valeur = dividende / (taux_actualisation - taux_croissance)
            st.success(f"**Valeur de l'action selon la méthode des dividendes : {valeur:,.2f} €**")
