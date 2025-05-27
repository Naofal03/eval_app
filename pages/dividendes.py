import streamlit as st
import numpy as np
import pandas as pd

def page_dividendes():
    st.markdown('<div class="main-title">Méthode des Dividendes (Dividend Discount Model - DDM)</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="info-card">
        <b>Principe :</b> Cette méthode (DDM) évalue une entreprise selon la valeur actuelle des dividendes futurs attendus, en supposant un taux de croissance constant, nul ou estimé à partir de l'historique.<br>
        <b>Formule :</b> <code>Valeur = Somme des dividendes actualisés + Valeur terminale actualisée</code> ou <code>Valeur = D1 / (T - g)</code> ou <code>Valeur = D / T</code>
        </div>
        """, unsafe_allow_html=True
    )

    methode = st.radio(
        "Choisissez la méthode selon vos données disponibles :",
        (
            "Dividendes croissants à taux constant (g connu ou déterminé)",
            "Dividendes constants",
            "Taux de croissance estimé à partir de l'historique"
        )
    )

    # Cas 1 : Dividendes croissants à taux constant (g connu ou déterminé)
    if methode == "Dividendes croissants à taux constant (g connu ou déterminé)":
        with st.form("ddm_alpha_form"):
            D0 = st.number_input("Dernier dividende connu (D0)", min_value=0.0, value=2.0, step=0.1)
            t = st.number_input("Nombre d'années (t)", min_value=1, max_value=50, value=5, step=1)
            alpha = st.number_input("Augmentation/diminution de la dividende dans t années (alpha)", value=1.0, step=0.1)
            # Choix du mode de calcul du taux d'actualisation
            mode_taux = st.radio(
                "Comment souhaitez-vous renseigner la rentabilité exigée T (%) ?",
                (
                    "Entrer la valeur directement",
                    "Calcul via le modèle CAPM (fonds propres)",
                    "Calcul via le WACC (coût moyen pondéré du capital)"
                ),
                key="mode_taux_ddm1"
            )
            if mode_taux == "Entrer la valeur directement":
                T = st.number_input("Rentabilité exigée T (%)", min_value=0.01, max_value=100.0, value=8.0, step=0.1, key="taux_direct_ddm1") / 100
            elif mode_taux == "Calcul via le modèle CAPM (fonds propres)":
                taux_sans_risque = st.number_input("Taux sans risque (%)", min_value=0.0, max_value=100.0, value=2.0, key="tsr_ddm1") / 100
                prime_risque_marche = st.number_input("Prime de risque du marché (%)", min_value=0.0, max_value=100.0, value=6.0, key="prm_ddm1") / 100
                beta = st.number_input("Bêta de l'entreprise", min_value=0.0, value=1.0, key="beta_ddm1")
                T = taux_sans_risque + prime_risque_marche * beta
                st.info(f"Rentabilité exigée T (CAPM) = {T*100:.2f} %")
            elif mode_taux == "Calcul via le WACC (coût moyen pondéré du capital)":
                cout_fonds_propres = st.number_input("Coût des capitaux propres (%)", min_value=0.0, max_value=100.0, value=10.0, key="cfp_ddm1") / 100
                part_fonds_propres = st.number_input("Part des capitaux propres (%)", min_value=0.0, max_value=100.0, value=50.0, key="pfp_ddm1") / 100
                cout_dette = st.number_input("Coût de la dette (%)", min_value=0.0, max_value=100.0, value=5.0, key="cd_ddm1") / 100
                part_dette = st.number_input("Part de la dette (%)", min_value=0.0, max_value=100.0, value=50.0, key="pd_ddm1") / 100
                taux_imposition = st.number_input("Taux d'imposition (%)", min_value=0.0, max_value=100.0, value=10.0, key="ti_ddm1") / 100
                T = (
                    cout_fonds_propres * part_fonds_propres +
                    cout_dette * (1 - taux_imposition) * part_dette
                )
                st.info(f"Rentabilité exigée T (WACC) = {T*100:.2f} %")
            submitted = st.form_submit_button("Calculer la valeur de l'action")

        if submitted:
            D1 = D0 + alpha
            g = (D1 / D0) ** (1 / t) - 1 if D0 > 0 else 0.0
            if T <= g:
                st.error("La rentabilité exigée doit être strictement supérieure au taux de croissance.")
                return
            valeur_action = D1 / (T - g)
            recap = {
                "Paramètre": [
                    "Dernier dividende connu (D0)",
                    "Dividende dans t années (D1)",
                    "Augmentation/diminution (alpha)",
                    "Nombre d'années (t)",
                    "Taux de croissance (g)",
                    "Rentabilité exigée (T)",
                    "Valeur de l'action"
                ],
                "Valeur": [
                    D0,
                    D1,
                    alpha,
                    t,
                    f"{g*100:.2f}%",

                    f"{T*100:.2f}%",

                    f"{valeur_action:,.2f}"
                ]
            }
            st.markdown("### Récapitulatif")
            st.dataframe(pd.DataFrame(recap))
            st.success(f"**Valeur de l'action : {valeur_action:,.2f}**")

    # Cas 2 : Dividendes constants
    elif methode == "Dividendes constants":
        with st.form("ddm_constant_form"):
            D = st.number_input("Dividende annuel constant (D)", min_value=0.0, value=2.0, step=0.1)
            # Choix du mode de calcul du taux d'actualisation
            mode_taux = st.radio(
                "Comment souhaitez-vous renseigner la rentabilité exigée T (%) ?",
                (
                    "Entrer la valeur directement",
                    "Calcul via le modèle CAPM (fonds propres)",
                    "Calcul via le WACC (coût moyen pondéré du capital)"
                ),
                key="mode_taux_ddm2"
            )
            if mode_taux == "Entrer la valeur directement":
                T = st.number_input("Rentabilité exigée T (%)", min_value=0.01, max_value=100.0, value=8.0, step=0.1, key="taux_direct_ddm2") / 100
            elif mode_taux == "Calcul via le modèle CAPM (fonds propres)":
                taux_sans_risque = st.number_input("Taux sans risque (%)", min_value=0.0, max_value=100.0, value=2.0, key="tsr_ddm2") / 100
                prime_risque_marche = st.number_input("Prime de risque du marché (%)", min_value=0.0, max_value=100.0, value=6.0, key="prm_ddm2") / 100
                beta = st.number_input("Bêta de l'entreprise", min_value=0.0, value=1.0, key="beta_ddm2")
                T = taux_sans_risque + prime_risque_marche * beta
                st.info(f"Rentabilité exigée T (CAPM) = {T*100:.2f} %")
            elif mode_taux == "Calcul via le WACC (coût moyen pondéré du capital)":
                cout_fonds_propres = st.number_input("Coût des capitaux propres (%)", min_value=0.0, max_value=100.0, value=10.0, key="cfp_ddm2") / 100
                part_fonds_propres = st.number_input("Part des capitaux propres (%)", min_value=0.0, max_value=100.0, value=50.0, key="pfp_ddm2") / 100
                cout_dette = st.number_input("Coût de la dette (%)", min_value=0.0, max_value=100.0, value=5.0, key="cd_ddm2") / 100
                part_dette = st.number_input("Part de la dette (%)", min_value=0.0, max_value=100.0, value=50.0, key="pd_ddm2") / 100
                taux_imposition = st.number_input("Taux d'imposition (%)", min_value=0.0, max_value=100.0, value=10.0, key="ti_ddm2") / 100
                T = (
                    cout_fonds_propres * part_fonds_propres +
                    cout_dette * (1 - taux_imposition) * part_dette
                )
                st.info(f"Rentabilité exigée T (WACC) = {T*100:.2f} %")
            submitted = st.form_submit_button("Calculer la valeur de l'action")

        if submitted:
            if T <= 0:
                st.error("La rentabilité exigée doit être strictement positive.")
                return
            valeur_action = D / T
            recap = {
                "Paramètre": [
                    "Dividende annuel constant (D)",
                    "Rentabilité exigée (T)",
                    "Valeur de l'action"
                ],
                "Valeur": [
                    D,
                    f"{T*100:.2f}%",

                    f"{valeur_action:,.2f}"
                ]
            }
            st.markdown("### Récapitulatif")
            st.dataframe(pd.DataFrame(recap))
            st.success(f"**Valeur de l'action : {valeur_action:,.2f}**")

    # Cas 3 : Taux de croissance estimé à partir de l'historique
    else:
        nb_historique = st.number_input(
            "Nombre d'années d'historique disponible",
            min_value=2, max_value=50, value=5, step=1, key="nb_historique"
        )
        historiques = []
        for i in range(int(nb_historique)):
            dividende = st.number_input(
                f"Dividende année historique {i+1}",
                min_value=0.0,
                value=2.0,
                step=0.1,
                key=f"div_hist_{i}_n{nb_historique}"
            )
            historiques.append(dividende)
        n = nb_historique - 1
        try:
            g = (historiques[-1] / historiques[0]) ** (1 / n) - 1 if historiques[0] > 0 else 0.0
        except ZeroDivisionError:
            g = 0.0
        st.markdown(f"Taux de croissance moyen estimé : **{g*100:.2f}%**")
        last_div = historiques[-1] if historiques else 0.0
        nb_projection = st.number_input("Nombre d'années de projection (N)", min_value=1, max_value=50, value=5, step=1)
        # Choix du mode de calcul du taux d'actualisation
        mode_taux = st.radio(
            "Comment souhaitez-vous renseigner la rentabilité exigée T (%) ?",
            (
                "Entrer la valeur directement",
                "Calcul via le modèle CAPM (fonds propres)",
                "Calcul via le WACC (coût moyen pondéré du capital)"
            ),
            key="mode_taux_ddm3"
        )
        if mode_taux == "Entrer la valeur directement":
            T = st.number_input("Rentabilité exigée T (%)", min_value=0.01, max_value=100.0, value=8.0, step=0.1, key="taux_direct_ddm3") / 100
        elif mode_taux == "Calcul via le modèle CAPM (fonds propres)":
            taux_sans_risque = st.number_input("Taux sans risque (%)", min_value=0.0, max_value=100.0, value=2.0, key="tsr_ddm3") / 100
            prime_risque_marche = st.number_input("Prime de risque du marché (%)", min_value=0.0, max_value=100.0, value=6.0, key="prm_ddm3") / 100
            beta = st.number_input("Bêta de l'entreprise", min_value=0.0, value=1.0, key="beta_ddm3")
            T = taux_sans_risque + prime_risque_marche * beta
            st.info(f"Rentabilité exigée T (CAPM) = {T*100:.2f} %")
        elif mode_taux == "Calcul via le WACC (coût moyen pondéré du capital)":
            cout_fonds_propres = st.number_input("Coût des capitaux propres (%)", min_value=0.0, max_value=100.0, value=10.0, key="cfp_ddm3") / 100
            part_fonds_propres = st.number_input("Part des capitaux propres (%)", min_value=0.0, max_value=100.0, value=50.0, key="pfp_ddm3") / 100
            cout_dette = st.number_input("Coût de la dette (%)", min_value=0.0, max_value=100.0, value=5.0, key="cd_ddm3") / 100
            part_dette = st.number_input("Part de la dette (%)", min_value=0.0, max_value=100.0, value=50.0, key="pd_ddm3") / 100
            taux_imposition = st.number_input("Taux d'imposition (%)", min_value=0.0, max_value=100.0, value=10.0, key="ti_ddm3") / 100
            T = (
                cout_fonds_propres * part_fonds_propres +
                cout_dette * (1 - taux_imposition) * part_dette
            )
            st.info(f"Rentabilité exigée T (WACC) = {T*100:.2f} %")
        submitted = st.button("Calculer la valeur de l'action")

        if submitted:
            # Projeter les dividendes futurs (récursif)
            dividendes = []
            prev_div = last_div
            for i in range(int(nb_projection)):
                next_div = prev_div * (1 + g)
                dividendes.append(next_div)
                prev_div = next_div

            valeurs_actualisees = [dividendes[i] / ((1 + T) ** (i + 1)) for i in range(int(nb_projection))]
            somme_dividendes = sum(valeurs_actualisees)
            # Valeur terminale
            if T <= g:
                st.error("La rentabilité exigée doit être strictement supérieure au taux de croissance.")
                return
            D_N = dividendes[-1] if dividendes else 0.0
            D_N1 = D_N * (1 + g)
            valeur_terminale = D_N1 / (T - g)
            valeur_terminale_actualisee = valeur_terminale / ((1 + T) ** nb_projection)
            valeur_action = somme_dividendes + valeur_terminale_actualisee

            # Tableau récapitulatif
            recap_data = {
                "Année": [f"Hist. {i+1}" for i in range(int(nb_historique))] + [f"Prévision {i+1}" for i in range(int(nb_projection))],
                "Dividende": historiques + dividendes,
                "Prévisionnel": [np.nan]*len(historiques) + dividendes,
                "Prévisionnel actualisé": [np.nan]*len(historiques) + valeurs_actualisees
            }
            df_recap = pd.DataFrame(recap_data)
            st.markdown("### Tableau récapitulatif")
            st.dataframe(df_recap, use_container_width=True)

            st.markdown(f"""
            <div class="info-card">
            <b>Taux de croissance géométrique (g) :</b> {g*100:.2f}%<br>
            <b>Taux d'actualisation (T) :</b> {T*100:.2f}%<br>
            <b>Somme des dividendes actualisés :</b> {somme_dividendes:,.2f}<br>
            <b>Dividende terminal D<sub>N+1</sub> :</b> {D_N1:,.2f}<br>
            <b>Valeur terminale :</b> {valeur_terminale:,.2f}<br>
            <b>Valeur terminale actualisée :</b> {valeur_terminale_actualisee:,.2f}<br>
            <b>Valeur de l'action :</b> {valeur_action:,.2f}
            </div>
            """, unsafe_allow_html=True)

            st.success(f"**Valeur de l'action : {valeur_action:,.2f}**")