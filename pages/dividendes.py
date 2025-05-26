import streamlit as st
import numpy as np
import pandas as pd

def page_dividendes():
    st.markdown('<div class="main-title">Méthode des Dividendes (Gordon-Shapiro / DDM)</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="info-card">
        <b>Principe :</b> Cette méthode évalue une entreprise selon la valeur actuelle des dividendes futurs attendus, en supposant un taux de croissance constant ou estimé.<br>
        <b>Formule :</b> <code>Valeur = Somme des dividendes actualisés + Valeur terminale actualisée</code>
        </div>
        """, unsafe_allow_html=True
    )

    with st.form("dividendes_form"):
        nb_projection = st.number_input("Nombre d'années de projection", min_value=1, max_value=50, value=5, step=1)
        nb_historique = st.number_input("Nombre d'années d'historique disponible", min_value=0, max_value=50, value=0, step=1)

        dividendes = []
        taux_croissance = None
        historiques = []

        if nb_historique == 0:
            st.markdown("**Entrez les dividendes attendus pour chaque année de projection :**")
            for i in range(int(nb_projection)):
                dividende = st.number_input(f"Dividende attendu année {i+1}", min_value=0.0, value=2.0, step=0.1, key=f"div_proj_{i}")
                dividendes.append(dividende)
        else:
            st.markdown("**Entrez les dividendes historiques :**")
            for i in range(int(nb_historique)):
                dividende = st.number_input(f"Dividende année historique {i+1}", min_value=0.0, value=2.0, step=0.1, key=f"div_hist_{i}")
                historiques.append(dividende)
            if nb_historique > 1:
                n = nb_historique - 1
                try:
                    taux_croissance = (historiques[-1] / historiques[0]) ** (1 / n) - 1
                except ZeroDivisionError:
                    taux_croissance = 0.0
            else:
                taux_croissance = 0.0
            st.markdown(f"Taux de croissance moyen estimé : **{taux_croissance*100:.2f}%**")
            last_div = historiques[-1] if historiques else 0.0
            for i in range(int(nb_projection)):
                dividende = last_div * ((1 + taux_croissance) ** (i + 1))
                dividendes.append(dividende)

        taux_actualisation = st.number_input("Taux d'actualisation (%)", min_value=0.01, max_value=100.0, value=8.0, step=0.1) / 100
        nb_actions = st.number_input("Nombre d'actions", min_value=1, value=1000, step=1)
        submitted = st.form_submit_button("Calculer la valeur de l'action")

    if submitted:
        # Actualisation des dividendes
        valeurs_actualisees = [dividendes[i] / ((1 + taux_actualisation) ** (i + 1)) for i in range(int(nb_projection))]
        somme_dividendes = sum(valeurs_actualisees)

        # Calcul de la valeur terminale (Gordon-Shapiro sur la dernière année)
        if nb_historique == 0:
            taux_croissance_terminal = st.number_input("Taux de croissance terminal (%)", min_value=0.0, max_value=100.0, value=2.0, step=0.1, key="g_terminal") / 100
        else:
            taux_croissance_terminal = taux_croissance if taux_croissance is not None else 0.0

        dernier_dividende_projete = dividendes[-1]
        if taux_actualisation <= taux_croissance_terminal:
            st.error("Le taux d'actualisation doit être strictement supérieur au taux de croissance terminal.")
            return

        valeur_terminale = (dernier_dividende_projete * (1 + taux_croissance_terminal)) / (taux_actualisation - taux_croissance_terminal)
        valeur_terminale_actualisee = valeur_terminale / ((1 + taux_actualisation) ** nb_projection)

        prix_action = somme_dividendes + valeur_terminale_actualisee

        # Tableau récapitulatif
        recap_data = {}
        if nb_historique > 0:
            recap_data["Année"] = [f"Hist. {i+1}" for i in range(int(nb_historique))] + [f"Prévision {i+1}" for i in range(int(nb_projection))]
            recap_data["Dividende"] = historiques + dividendes
            recap_data["Prévisionnel"] = [np.nan]*len(historiques) + dividendes
            recap_data["Prévisionnel actualisé"] = [np.nan]*len(historiques) + valeurs_actualisees
        else:
            recap_data["Année"] = [f"Prévision {i+1}" for i in range(int(nb_projection))]
            recap_data["Dividende"] = dividendes
            recap_data["Prévisionnel"] = dividendes
            recap_data["Prévisionnel actualisé"] = valeurs_actualisees

        df_recap = pd.DataFrame(recap_data)
        st.markdown("### Tableau récapitulatif")
        st.dataframe(df_recap, use_container_width=True)

        st.markdown(f"""
        <div class="info-card">
        <b>Valeur terminale :</b> {valeur_terminale:,.2f}<br>
        <b>Valeur terminale actualisée :</b> {valeur_terminale_actualisee:,.2f}<br>
        <b>Somme des dividendes actualisés :</b> {somme_dividendes:,.2f}<br>
        <b>Valeur  de l'action :</b> {prix_action:,.2f}<br>
        <b>Nombre d'actions :</b> {nb_actions:,}<br>
        <b>Taux de croissance moyen :</b> {taux_croissance*100 if taux_croissance is not None else 0:.2f}%<br>
        <b>Taux de croissance terminal :</b> {taux_croissance_terminal*100:.2f}%<br>
        <b>Taux d'actualisation :</b> {taux_actualisation*100:.2f}%
        </div>
        """, unsafe_allow_html=True)

        st.success(f"**Prix théorique par action : {prix_action:,.2f}**")