import streamlit as st
import pandas as pd
import numpy as np


def affiche_valeur(val):
   if isinstance(val, float):
       s = str(val)
       if '.' in s:
           s = s.rstrip('0').rstrip('.')
       return s
   return val


def page_dcf():
   st.markdown('<div class="main-title">💸 Méthode DCF</div>', unsafe_allow_html=True)
   st.markdown('<div class="info-card">Estimez la valeur de votre entreprise par actualisation des flux de trésorerie futurs.<br><br>'
               'Vous pouvez saisir les historiques pour générer les flux prévisionnels automatiquement.</div>', unsafe_allow_html=True)


   st.markdown('<div class="subtitle"><span class="icon">📝</span>Informations sur l\'entreprise à évaluer</div>', unsafe_allow_html=True)
   nom = st.text_input("Nom de l'entreprise")
   secteur = st.text_input("Secteur d'activité")
   taux_impot = st.number_input("Taux d'impôt (%)", min_value=0.0, max_value=100.0, value=10.0 ) / 100


   nb_annees_hist = st.number_input("Nombre d'années d'historique disponible", min_value=0, max_value=10, value=0)
   nb_annees_prev = st.number_input("Nombre d'années de prévision", min_value=1, max_value=10, value=5)


   if nb_annees_hist > 0:
       # Saisie particulière pour l'année en cours (1er, 2e, 3e trimestre)
       st.markdown('<div class="subtitle"><span class="icon">📅</span>Chiffre d\'affaires de l\'année en cours (optionnel)</div>', unsafe_allow_html=True)
       ca_annee_courante = None
       nb_trimestres = 0
       use_partial_ca = st.checkbox("Avez-vous des chiffres d'affaires partiels pour l'année en cours ?")
       if use_partial_ca:
           nb_trimestres = st.selectbox("Nombre de trimestres disponibles", [1, 2, 3], index=0)
           ca_trimestres = []
           for t in range(nb_trimestres):
               ca_trim = st.number_input(f"Chiffre d'affaires T{t+1}", key=f"ca_trim_{t}", step=1000.0)
               ca_trimestres.append(ca_trim)
           if nb_trimestres == 1:
               ca_annee_courante = ca_trimestres[0] * 4
           elif nb_trimestres == 2:
               ca_annee_courante = sum(ca_trimestres) * 2
           elif nb_trimestres == 3:
               ca_annee_courante = sum(ca_trimestres) + (sum(ca_trimestres) / 3)
           st.markdown(f"**Estimation du chiffre d'affaires pour l'année en cours : {affiche_valeur(ca_annee_courante)}**")


       st.markdown('<div class="subtitle"><span class="icon">📊</span>Données historiques</div>', unsafe_allow_html=True)
       hist_data = []
       for i in range(nb_annees_hist):
           annee = f"Année -{nb_annees_hist - i}"
           ca = st.number_input(f"Chiffre d'affaires {annee}", key=f"ca_hist_{i}", step=1000.0)
           rex = st.number_input(f"Résultat d'exploitation {annee}", key=f"rex_hist_{i}", step=1000.0)
           dot = st.number_input(f"Dotations aux amortissements {annee}", key=f"dot_hist_{i}", step=1000.0)
           ac = st.number_input(f"Actif circulant {annee}", key=f"ac_hist_{i}", step=1000.0)
           pc = st.number_input(f"Passif circulant {annee}", key=f"pc_hist_{i}", step=1000.0)
           inv = st.number_input(f"Investissements nets {annee}", key=f"inv_hist_{i}", step=1000.0)
           hist_data.append({
               "Année": annee,
               "CA": ca,
               "REX": rex,
               "Dot": dot,
               "AC": ac,
               "PC": pc,
               "INV": inv
           })
       df_hist = pd.DataFrame(hist_data)
       # Calcul du BFR et du %BFR/CA
       df_hist["BFR"] = df_hist["AC"] - df_hist["PC"]
       df_hist["%BFR/CA"] = df_hist["BFR"] / df_hist["CA"].replace(0, np.nan)
       df_hist["ΔBFR"] = df_hist["BFR"].diff().fillna(0)


       # Taux de croissance du CA (année à année)
       df_hist["Taux croissance CA"] = df_hist["CA"].pct_change().fillna(0)
       # CAGR
       if nb_annees_hist > 1 and df_hist["CA"].iloc[0] > 0:
           cagr = (df_hist["CA"].iloc[-1] / df_hist["CA"].iloc[0]) ** (1/(nb_annees_hist-1)) - 1
       else:
           cagr = 0
       # Moyenne et médiane du taux de croissance
       moyenne_croissance = df_hist["Taux croissance CA"][1:].mean() if nb_annees_hist > 1 else 0
       mediane_croissance = df_hist["Taux croissance CA"][1:].median() if nb_annees_hist > 1 else 0
       taux_croissance_retenu = min(cagr, moyenne_croissance, mediane_croissance)


       # Tableau CA (historique + prévision)
       st.markdown('<div class="subtitle"><span class="icon">📈</span>Tableau Chiffre d\'Affaires (historique + prévision)</div>', unsafe_allow_html=True)
       ca_prev = []
       if use_partial_ca and ca_annee_courante is not None:
           ca_prev.append(ca_annee_courante)
           start_idx = 1
           last_ca = ca_annee_courante
       else:
           start_idx = 0
           last_ca = df_hist["CA"].iloc[-1] if not df_hist.empty else 0


       for i in range(start_idx, nb_annees_prev):
           ca = last_ca * ((1 + taux_croissance_retenu) ** (i + 1 - start_idx))
           ca_prev.append(ca)


       ca_full = pd.concat([
           df_hist[["Année", "CA", "Taux croissance CA"]],
           pd.DataFrame({
               "Année": [f"Année {i+1}" for i in range(nb_annees_prev)],
               "CA": ca_prev,
               "Taux croissance CA": [taux_croissance_retenu]*nb_annees_prev
           })
       ], ignore_index=True)
       ca_full.loc["Moyenne"] = ["", "", affiche_valeur(moyenne_croissance)]
       ca_full.loc["Médiane"] = ["", "", affiche_valeur(mediane_croissance)]
       ca_full.loc["CAGR"] = ["", "", affiche_valeur(cagr)]
       st.dataframe(ca_full)


       # Taux de marge REX
       df_hist["Taux marge REX"] = df_hist["REX"] / df_hist["CA"].replace(0, np.nan)
       moyenne_marge = df_hist["Taux marge REX"].mean()
       mediane_marge = df_hist["Taux marge REX"].median()
       taux_marge_retenu = mediane_marge


       # Tableau REX (historique + prévision)
       st.markdown('<div class="subtitle"><span class="icon">📈</span>Tableau Résultat d\'Exploitation (historique + prévision)</div>', unsafe_allow_html=True)
       rex_prev = [ca_prev[i] * taux_marge_retenu for i in range(nb_annees_prev)]
       rex_full = pd.concat([
           df_hist[["Année", "REX", "Taux marge REX"]],
           pd.DataFrame({
               "Année": [f"Année {i+1}" for i in range(nb_annees_prev)],
               "REX": rex_prev,
               "Taux marge REX": [taux_marge_retenu]*nb_annees_prev
           })
       ], ignore_index=True)
       rex_full.loc["Moyenne"] = ["", "", affiche_valeur(moyenne_marge)]
       rex_full.loc["Médiane"] = ["", "", affiche_valeur(mediane_marge)]
       st.dataframe(rex_full)


       # Calcul du % DAP/CA (dotations aux amortissements)
       df_hist["%DAP/CA"] = df_hist["Dot"] / df_hist["CA"].replace(0, np.nan)
       moyenne_dap = df_hist["%DAP/CA"].mean()
       mediane_dap = df_hist["%DAP/CA"].median()
       taux_dap_retenu = max(moyenne_dap, mediane_dap)


       # Calcul du DAP prévisionnel
       dap_prev = [ca_prev[i] * taux_dap_retenu for i in range(nb_annees_prev)]


       # Tableau DAP (historique + prévision)
       dap_full = pd.DataFrame(
           columns=["Type"] + [row for row in list(df_hist["Année"])+[f"Année {i+1}" for i in range(nb_annees_prev)]]
       )
       dap_full.loc[0] = ["Chiffre d'affaires"] + list(df_hist["CA"]) + ca_prev
       dap_full.loc[1] = ["Dotations"] + list(df_hist["Dot"]) + dap_prev
       dap_full.loc[2] = ["%DAP/CA"] + list(df_hist["%DAP/CA"]) + [taux_dap_retenu]*nb_annees_prev
       st.markdown('<div class="subtitle"><span class="icon">🧮</span>Tableau Dotations aux amortissements (historique + prévision)</div>', unsafe_allow_html=True)
       st.dataframe(dap_full)


       # Calcul du %INV/CA (investissements nets)
       df_hist["%INV/CA"] = df_hist["INV"] / df_hist["CA"].replace(0, np.nan)
       moyenne_inv = df_hist["%INV/CA"].mean()
       mediane_inv = df_hist["%INV/CA"].median()
       taux_inv_retenu = max(moyenne_inv, mediane_inv)


       # Calcul de l'investissement net prévisionnel
       inv_prev = [ca_prev[i] * taux_inv_retenu for i in range(nb_annees_prev)]


       # Tableau Investissements (historique + prévision)
       inv_full = pd.DataFrame(
           columns=["Type"] + [row for row in list(df_hist["Année"])+[f"Année {i+1}" for i in range(nb_annees_prev)]]
       )
       inv_full.loc[0] = ["Chiffre d'affaires"] + list(df_hist["CA"]) + ca_prev
       inv_full.loc[1] = ["Investissements"] + list(df_hist["INV"]) + inv_prev
       inv_full.loc[2] = ["%INV/CA"] + list(df_hist["%INV/CA"]) + [taux_inv_retenu]*nb_annees_prev
       st.markdown('<div class="subtitle"><span class="icon">🏗️</span>Tableau Investissements nets (historique + prévision)</div>', unsafe_allow_html=True)
       st.dataframe(inv_full)


       # Tableau BFR (historique + prévision)
       st.markdown('<div class="subtitle"><span class="icon">📈</span>Tableau BFR & %BFR/CA (historique + prévision)</div>', unsafe_allow_html=True)
       median_bfr_ca = df_hist["%BFR/CA"].median()
       last_bfr = df_hist["BFR"].iloc[-1] if not df_hist.empty else 0
       bfr_prev = [median_bfr_ca * ca_prev[i] for i in range(nb_annees_prev)]
       delta_bfr_prev = [bfr_prev[0] - last_bfr] + [bfr_prev[i] - bfr_prev[i-1] for i in range(1, nb_annees_prev)]
       bfr_full = pd.concat([
           df_hist[["Année", "AC", "PC", "CA", "BFR", "%BFR/CA", "ΔBFR"]],
           pd.DataFrame({
               "Année": [f"Année {i+1}" for i in range(nb_annees_prev)],
               "AC": [np.nan]*nb_annees_prev,
               "PC": [np.nan]*nb_annees_prev,
               "CA": ca_prev,
               "BFR": bfr_prev,
               "%BFR/CA": [median_bfr_ca]*nb_annees_prev,
               "ΔBFR": delta_bfr_prev
           })
       ], ignore_index=True)
       bfr_full.loc["Médiane"] = [""]*4 + [affiche_valeur(df_hist["BFR"].median()), affiche_valeur(df_hist["%BFR/CA"].median()), ""]
       st.dataframe(bfr_full)


       # Tableau flux de trésorerie (historique + prévision)
       st.markdown('<div class="subtitle"><span class="icon">📋</span>Flux de trésorerie disponibles et actualisés (historique + prévision)</div>', unsafe_allow_html=True)
       # Historique : calcul FTD
       df_hist["Impôt REX"] = df_hist["REX"] * taux_impot
       df_hist["F. trésorerie dispo"] = (
           df_hist["REX"] - df_hist["Impôt REX"] + df_hist["Dot"] - df_hist["ΔBFR"] - df_hist["INV"]
       )
       # Prévision : calcul FTD prévisionnel (formule correcte)
       rex_prev = [ca_prev[i] * taux_marge_retenu for i in range(nb_annees_prev)]
       impots_prev = [rex_prev[i] * taux_impot for i in range(nb_annees_prev)]
       delta_bfr_prev = [bfr_prev[0] - last_bfr] + [bfr_prev[i] - bfr_prev[i-1] for i in range(1, nb_annees_prev)]
       ft_prev = [
           rex_prev[i] - impots_prev[i] + dap_prev[i] - delta_bfr_prev[i] - inv_prev[i]
           for i in range(nb_annees_prev)
       ]
       # Saisie ou calcul du taux d'actualisation
       st.markdown('<div class="subtitle"><span class="icon">💡</span>Choix du taux d\'actualisation</div>', unsafe_allow_html=True)
       mode_taux = st.radio(
           "Comment souhaitez-vous renseigner le taux d'actualisation ?",
           (
               "Entrer la valeur directement",
               "Calcul via le modèle CAPM (fonds propres)",
               "Calcul via le WACC (coût moyen pondéré du capital)"
           )
       )


       if mode_taux == "Entrer la valeur directement":
           taux_actualisation = st.number_input("Taux d'actualisation (%)", min_value=0.0, max_value=100.0, value=10.0) / 100
       elif mode_taux == "Calcul via le modèle CAPM (fonds propres)":
           taux_sans_risque = st.number_input("Taux sans risque (%)", min_value=0.0, max_value=100.0, value=2.0) / 100
           prime_risque_marche = st.number_input("Prime de risque du marché (%)", min_value=0.0, max_value=100.0, value=6.0) / 100
           beta = st.number_input("Bêta de l'entreprise", min_value=0.0, value=1.0)
           taux_actualisation = taux_sans_risque + prime_risque_marche * beta
           st.info(f"Taux d'actualisation (CAPM) = {affiche_valeur(taux_actualisation*100)} %")
       elif mode_taux == "Calcul via le WACC (coût moyen pondéré du capital)":
           cout_fonds_propres = st.number_input("Coût des capitaux propres (%)", min_value=0.0, max_value=100.0, value=10.0) / 100
           part_fonds_propres = st.number_input("Part des capitaux propres (%)", min_value=0.0, max_value=100.0, value=50.0) / 100
           cout_dette = st.number_input("Coût de la dette (%)", min_value=0.0, max_value=100.0, value=5.0) / 100
           part_dette = st.number_input("Part de la dette (%)", min_value=0.0, max_value=100.0, value=50.0) / 100
           taux_imposition = st.number_input("Taux d'imposition (%)", min_value=0.0, max_value=100.0, value=10.0) / 100
           taux_actualisation = (
               cout_fonds_propres * part_fonds_propres +
               cout_dette * (1 - taux_imposition) * part_dette
           )
           st.info(f"Taux d'actualisation (WACC) = {affiche_valeur(taux_actualisation*100)} %")


       ft_prev_actualise = [
           ft_prev[i] / (1 + taux_actualisation) ** (i + 1) for i in range(nb_annees_prev)
       ]


       # Valeur terminale
       st.markdown('<div class="subtitle"><span class="icon">🔁</span>Calcul de la valeur terminale</div>', unsafe_allow_html=True)
       taux_croissance_g = st.number_input("Taux de croissance à long terme g (%)", min_value=0.0, max_value=20.0, value=2.0) / 100
       flux_utilise_vt = ft_prev[-1]
       vt = flux_utilise_vt * (1 + taux_croissance_g) / (taux_actualisation - taux_croissance_g) if taux_actualisation > taux_croissance_g else 0
       vt_actuelle = vt / (1 + taux_actualisation) ** nb_annees_prev


       # Tableau récapitulatif valeur terminale
       vt_df = pd.DataFrame({
           "Élément": [
               "Flux de trésorerie utilisé (année finale)",
               "Taux de croissance g",
               "Taux d'actualisation",
               "Valeur terminale",
               "Valeur actuelle de la valeur terminale"
           ],
           "Valeur": [
               affiche_valeur(flux_utilise_vt),
               f"{affiche_valeur(taux_croissance_g*100)} %",
               f"{affiche_valeur(taux_actualisation*100)} %",
               affiche_valeur(vt),
               affiche_valeur(vt_actuelle)
           ]
       })
       st.dataframe(vt_df)


       # Tableau flux de trésorerie prévisionnel détaillé (années de prévision uniquement)
       st.markdown('<div class="subtitle"><span class="icon">📋</span>Tableau de calcul du flux de trésorerie prévisionnel</div>', unsafe_allow_html=True)
       tableau_flux = pd.DataFrame({
           "Année": [f"Année {i+1}" for i in range(nb_annees_prev)] + ["Somme"],
           "Résultat d'exploitation": [affiche_valeur(rex_prev[i]) for i in range(nb_annees_prev)] + [""],
           "Impôt sur REX": [affiche_valeur(impots_prev[i]) for i in range(nb_annees_prev)] + [""],
           "Dotations aux amortissements": [affiche_valeur(dap_prev[i]) for i in range(nb_annees_prev)] + [""],
           "Variation du BFR": [affiche_valeur(delta_bfr_prev[i]) for i in range(nb_annees_prev)] + [""],
           "Investissements nets": [affiche_valeur(inv_prev[i]) for i in range(nb_annees_prev)] + [""],
           "Flux de trésorerie disponible": [affiche_valeur(ft_prev[i]) for i in range(nb_annees_prev)] + [""],
           "Flux de trésorerie actualisé": [affiche_valeur(ft_prev_actualise[i]) for i in range(nb_annees_prev)] + [affiche_valeur(sum(ft_prev_actualise))]
       })
       st.dataframe(tableau_flux)


       # Tableau flux de trésorerie prévisionnel détaillé (années de prévision uniquement)
       flux_prev_df = pd.DataFrame({
           f"Année {i+1}": [
               rex_prev[i],
               impots_prev[i],
               dap_prev[i],
               delta_bfr_prev[i],
               inv_prev[i],
               ft_prev[i],
               ft_prev_actualise[i]
           ]
           for i in range(nb_annees_prev)
       }, index=[
           "Résultat d'exploitation",
           "Impôt sur REX",
           "Dotations aux amortissements",
           "Variation du BFR",
           "Investissements nets",
           "Flux de trésorerie disponible",
           "Flux de trésorerie actualisé"
       ])
       # Ajout de la somme des flux actualisés en bas du tableau
       somme_flux_actualises = sum(ft_prev_actualise)
       flux_prev_df.loc["Somme flux actualisés"] = [""]* (len(flux_prev_df.columns)-1) + [somme_flux_actualises]
       st.markdown('<div class="subtitle"><span class="icon">📋</span>Tableau flux de trésorerie prévisionnel détaillé</div>', unsafe_allow_html=True)
       st.dataframe(flux_prev_df)


       # Tableau récapitulatif final
       st.markdown('<div class="subtitle"><span class="icon">🧾</span>Récapitulatif de l\'évaluation</div>', unsafe_allow_html=True)
       valeur_entreprise = somme_flux_actualises + vt_actuelle


       # Saisie de la dette nette si non déjà connue
       dette_nette = st.number_input("Valeur de la dette nette (si connue, sinon saisir 0)", min_value=0.0, step=1000.0, value=0.0)
       valeur_capitaux_propres = valeur_entreprise - dette_nette
       nb_titres = st.number_input("Nombre de titres (actions)", min_value=1, step=1, value=1000)
       valeur_action = valeur_capitaux_propres / nb_titres if nb_titres > 0 else 0


       recap_df = pd.DataFrame({
           "Élément": [
               "Somme des flux de trésorerie actualisés",
               "Valeur actuelle de la valeur terminale",
               "Valeur de l'entreprise",
               "Valeur de la dette nette",
               "Valeur des capitaux propres",
               "Nombre de titres",
               "Valeur d'une action"
           ],
           "Valeur": [
               affiche_valeur(somme_flux_actualises),
               affiche_valeur(vt_actuelle),
               affiche_valeur(valeur_entreprise),
               affiche_valeur(dette_nette),
               affiche_valeur(valeur_capitaux_propres),
               affiche_valeur(nb_titres),
               affiche_valeur(valeur_action)
           ]
       })
       st.dataframe(recap_df)


       if st.button("Calculer la valeur DCF"):
           st.success(f"🎯 Valeur estimée par DCF : {affiche_valeur(valeur_entreprise)}")
           st.markdown('<div class="subtitle"><span class="icon">🧾</span>Résumé de l\'évaluation</div>', unsafe_allow_html=True)
           resume = {
               "Nom de l'entreprise": nom,
               "Secteur": secteur,
               "Méthode": "DCF",
               "Taux d'actualisation (%)": taux_actualisation * 100,
               "Taux de croissance g (%)": taux_croissance_g * 100,
               "Valeur de l'entreprise": valeur_entreprise,
               "Valeur de la dette nette": dette_nette,
               "Valeur des capitaux propres": valeur_capitaux_propres,
               "Nombre de titres": nb_titres,
               "Valeur d'une action": valeur_action
           }
           for i, ft in enumerate(ft_prev):
               resume[f"Flux disponible année {i+1}"] = ft
           st.table(pd.DataFrame(resume.items(), columns=["Élément", "Valeur"]).applymap(affiche_valeur))
   else:
       # Mode simple : saisie directe des flux prévisionnels
       st.markdown('<div class="subtitle"><span class="icon">💵</span>Flux de trésorerie prévisionnels</div>', unsafe_allow_html=True)
       cash_flows = []
       for i in range(nb_annees_prev):
           cf = st.number_input(f"Flux année {i+1}", key=f"cf_{i}", step=1000.0)
           cash_flows.append(cf)


       # Choix du taux d'actualisation (même logique que dans le if)
       st.markdown('<div class="subtitle"><span class="icon">💡</span>Choix du taux d\'actualisation</div>', unsafe_allow_html=True)
       mode_taux = st.radio(
           "Comment souhaitez-vous renseigner le taux d'actualisation ?",
           (
               "Entrer la valeur directement",
               "Calcul via le modèle CAPM (fonds propres)",
               "Calcul via le WACC (coût moyen pondéré du capital)"
           ),
           key="mode_taux_simple"
       )
       if mode_taux == "Entrer la valeur directement":
           taux_actualisation = st.number_input("Taux d'actualisation (%)", min_value=0.0, max_value=100.0, value=10.0, key="taux_direct_simple") / 100
       elif mode_taux == "Calcul via le modèle CAPM (fonds propres)":
           taux_sans_risque = st.number_input("Taux sans risque (%)", min_value=0.0, max_value=100.0, value=2.0, key="tsr_simple") / 100
           prime_risque_marche = st.number_input("Prime de risque du marché (%)", min_value=0.0, max_value=100.0, value=6.0, key="prm_simple") / 100
           beta = st.number_input("Bêta de l'entreprise", min_value=0.0, value=1.0, key="beta_simple")
           taux_actualisation = taux_sans_risque + prime_risque_marche * beta
           st.info(f"Taux d'actualisation (CAPM) = {affiche_valeur(taux_actualisation*100)} %")
       elif mode_taux == "Calcul via le WACC (coût moyen pondéré du capital)":
           cout_fonds_propres = st.number_input("Coût des capitaux propres (%)", min_value=0.0, max_value=100.0, value=10.0, key="cfp_simple") / 100
           part_fonds_propres = st.number_input("Part des capitaux propres (%)", min_value=0.0, max_value=100.0, value=50.0, key="pfp_simple") / 100
           cout_dette = st.number_input("Coût de la dette (%)", min_value=0.0, max_value=100.0, value=5.0, key="cd_simple") / 100
           part_dette = st.number_input("Part de la dette (%)", min_value=0.0, max_value=100.0, value=50.0, key="pd_simple") / 100
           taux_imposition = st.number_input("Taux d'imposition (%)", min_value=0.0, max_value=100.0, value=10.0, key="ti_simple") / 100
           taux_actualisation = (
               cout_fonds_propres * part_fonds_propres +
               cout_dette * (1 - taux_imposition) * part_dette
           )
           st.info(f"Taux d'actualisation (WACC) = {affiche_valeur(taux_actualisation*100)} %")


       # Demander toutes les informations nécessaires AVANT le calcul
       st.markdown('<div class="subtitle"><span class="icon">🔁</span>Calcul de la valeur terminale</div>', unsafe_allow_html=True)
       taux_croissance_g = st.number_input("Taux de croissance à long terme g (%)", min_value=0.0, max_value=20.0, value=2.0, key="g_simple") / 100
       dette_nette = st.number_input("Valeur de la dette nette (si connue, sinon saisir 0)", min_value=0.0, step=1000.0, value=0.0, key="dette_simple")
       nb_titres = st.number_input("Nombre de titres (actions)", min_value=1, step=1, value=1000, key="titres_simple")


       # Calculs
       flux_utilise_vt = cash_flows[-1] if cash_flows else 0
       vt = flux_utilise_vt * (1 + taux_croissance_g) / (taux_actualisation - taux_croissance_g) if taux_actualisation > taux_croissance_g else 0
       vt_actuelle = vt / (1 + taux_actualisation) ** nb_annees_prev
       flux_actualises = [cf / (1 + taux_actualisation) ** (i + 1) for i, cf in enumerate(cash_flows)]
       somme_flux_actualises = sum(flux_actualises)
       valeur_entreprise = somme_flux_actualises + vt_actuelle
       valeur_capitaux_propres = valeur_entreprise - dette_nette
       valeur_action = valeur_capitaux_propres / nb_titres if nb_titres > 0 else 0


       # Tableau valeur terminale
       vt_df = pd.DataFrame({
           "Élément": [
               "Flux de trésorerie utilisé (année finale)",
               "Taux de croissance g",
               "Taux d'actualisation",
               "Valeur terminale",
               "Valeur actuelle de la valeur terminale"
           ],
           "Valeur": [
               affiche_valeur(flux_utilise_vt),
               f"{affiche_valeur(taux_croissance_g*100)} %",
               f"{affiche_valeur(taux_actualisation*100)} %",
               affiche_valeur(vt),
               affiche_valeur(vt_actuelle)
           ]
       })
       st.dataframe(vt_df)


       # Tableau flux de trésorerie prévisionnel détaillé
       st.markdown('<div class="subtitle"><span class="icon">📋</span>Tableau de calcul du flux de trésorerie prévisionnel</div>', unsafe_allow_html=True)
       tableau_flux = pd.DataFrame({
           "Année": [f"Année {i+1}" for i in range(nb_annees_prev)] + ["Somme"],
           "Flux de trésorerie disponible": [affiche_valeur(cf) for cf in cash_flows] + [""],
           "Flux de trésorerie actualisé": [affiche_valeur(fa) for fa in flux_actualises] + [affiche_valeur(somme_flux_actualises)]
       })
       st.dataframe(tableau_flux)


       # Tableau récapitulatif final
       recap_df = pd.DataFrame({
           "Élément": [
               "Somme des flux de trésorerie actualisés",
               "Valeur actuelle de la valeur terminale",
               "Valeur de l'entreprise",
               "Valeur de la dette nette",
               "Valeur des capitaux propres",
               "Nombre de titres",
               "Valeur d'une action"
           ],
           "Valeur": [
               affiche_valeur(somme_flux_actualises),
               affiche_valeur(vt_actuelle),
               affiche_valeur(valeur_entreprise),
               affiche_valeur(dette_nette),
               affiche_valeur(valeur_capitaux_propres),
               affiche_valeur(nb_titres),
               affiche_valeur(valeur_action)
           ]
       })
       st.dataframe(recap_df)


       if st.button("Calculer la valeur DCF"):
           st.success(f"🎯 Valeur estimée par DCF : {affiche_valeur(valeur_entreprise)}")
           st.markdown('<div class="subtitle"><span class="icon">🧾</span>Résumé de l\'évaluation</div>', unsafe_allow_html=True)
           resume = {
               "Nom de l'entreprise": nom,
               "Secteur": secteur,
               "Méthode": "DCF",
               "Taux d'actualisation (%)": taux_actualisation * 100,
               "Taux de croissance g (%)": taux_croissance_g * 100,
               "Valeur de l'entreprise": valeur_entreprise,
               "Valeur de la dette nette": dette_nette,
               "Valeur des capitaux propres": valeur_capitaux_propres,
               "Nombre de titres": nb_titres,
               "Valeur d'une action": valeur_action
           }
           for i, cf in enumerate(cash_flows):
               resume[f"Flux année {i+1}"] = cf
           st.table(pd.DataFrame(resume.items(), columns=["Élément", "Valeur"]).applymap(affiche_valeur))





