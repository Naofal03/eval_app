import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Évaluation d'Entreprise", layout="wide")

# Ajout d'un style CSS pour améliorer l'apparence et les animations
st.markdown("""
    <style>
    .main-title {
        font-size:2.5em;
        font-weight:bold;
        color:#2d3a4b;
        text-align:center;
        margin-bottom:0.5em;
        animation: fadein 1.2s;
    }
    .subtitle {
        font-size:1.3em;
        color:#1abc9c;
        font-weight:bold;
        margin-top:1em;
        display: flex;
        align-items: center;
        gap: 0.5em;
        animation: fadein 1.2s;
    }
    .info-card {
        background: #f7fafc;
        border-radius: 10px;
        padding: 1.5em;
        margin-bottom: 1em;
        box-shadow: 0 2px 8px rgba(44,62,80,0.07);
        animation: fadein 1.2s;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-size: 1.1em;
        font-weight: bold;
        margin-bottom: 0.5em;
        background: linear-gradient(90deg, #1abc9c 0%, #3498db 100%);
        color: white;
        border: none;
        transition: 0.2s;
        box-shadow: 0 2px 8px rgba(44,62,80,0.07);
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #3498db 0%, #1abc9c 100%);
        color: #fff;
        transform: scale(1.03);
    }
    @keyframes fadein {
        from { opacity: 0; transform: translateY(30px);}
        to { opacity: 1; transform: translateY(0);}
    }
    .icon {
        font-size: 1.3em;
        margin-right: 0.3em;
        vertical-align: middle;
    }
    </style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "Accueil"

# Navigation avec icônes
pages = [
    ("Accueil", "🏠"),
    ("Méthode des comparables", "📊"),
    ("Méthode DCF", "💸")
]
cols = st.columns(len(pages))
for i, (p, icon) in enumerate(pages):
    if cols[i].button(f"{icon} {p}"):
        st.session_state.page = p

st.markdown("---")

if st.session_state.page == "Accueil":
    st.markdown('<div class="main-title">👋 Bienvenue dans l\'application d\'évaluation</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card">Choisissez une méthode pour commencer votre évaluation.<br><br>'
                '<span style="font-size:1.1em;">'
                '📊 <b>Méthode des comparables</b> : Comparez votre entreprise à des sociétés similaires.<br>'
                '💸 <b>Méthode DCF</b> : Actualisez les flux de trésorerie futurs pour estimer la valeur.<br>'
                '</span></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="margin-top:2em; text-align:center;">
            <img src="https://cdn.pixabay.com/photo/2017/01/10/19/05/analysis-1974641_1280.png" width="45%" style="border-radius:12px;box-shadow:0 2px 8px rgba(44,62,80,0.07);">
        </div>
        """,
        unsafe_allow_html=True
    )

elif st.session_state.page == "Méthode des comparables":
    st.markdown('<div class="main-title">📊 Méthode des comparables</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card">Comparez votre entreprise à des sociétés similaires pour estimer sa valeur.</div>', unsafe_allow_html=True)

    st.markdown('<div class="subtitle"><span class="icon">📝</span>Informations générales</div>', unsafe_allow_html=True)
    nom = st.text_input("Nom de l'entreprise")
    secteur = st.text_input("Secteur d'activité")
    nb_entreprises = st.number_input("Nombre d'entreprises comparables", min_value=1, max_value=100, value=3)
    nb_annees = st.number_input("Nombre d'années à considérer", min_value=1, max_value=100, value=3)

    mode_saisie = st.radio(
        "Mode de saisie des données",
        ["Saisir les données financières (CA, EBITDA...)", "Saisir directement les multiples"]
    )

    multiples_dependances = {
        "EV/EBITDA": ["Valeur d'entreprise (VE)", "EBE (EBITDA)"],
        "EV/CA": ["Valeur d'entreprise (VE)", "Chiffre d'affaires (CA)"],
        "P/EBIT": ["Capitalisation boursière", "Résultat d'exploitation (EBIT)"],
        "P/S": ["Capitalisation boursière", "Chiffre d'affaires (CA)"],
        "PER": ["Capitalisation boursière", "Résultat net"],
        "PBR": ["Capitalisation boursière", "Capitaux propres"]
    }

    if mode_saisie == "Saisir les données financières (CA, EBITDA...)":
        st.markdown('<div class="subtitle"><span class="icon">📑</span>Données disponibles</div>', unsafe_allow_html=True)
        donnees_disponibles = st.multiselect(
            "Cochez les données que vous avez pour chaque entreprise et année",
            [
                "Capitalisation boursière",
                "Valeur d'entreprise (VE)",
                "Dettes nettes",
                "Chiffre d'affaires (CA)",
                "EBE (EBITDA)",
                "Résultat d'exploitation (EBIT)",
                "Résultat net",
                "Capitaux propres"
            ]
        )

        multiples_possibles = [
            m for m, deps in multiples_dependances.items()
            if all(dep in donnees_disponibles for dep in deps)
        ]

        st.markdown('<div class="subtitle"><span class="icon">🔢</span>Choix des multiples à calculer/utiliser</div>', unsafe_allow_html=True)
        multiples_choisis = st.multiselect(
            "Sélectionnez les multiples à utiliser",
            multiples_possibles
        )

        # Déterminer tous les agrégats nécessaires selon les multiples sélectionnés
        agregats_possibles = set()
        agregats_map = {
            "EV/EBITDA": "EBITDA",
            "EV/CA": "Chiffre d'affaires (CA)",
            "P/EBIT": "EBIT",
            "P/S": "Chiffre d'affaires (CA)",
            "PER": "Résultat net",
            "PBR": "Capitaux propres"
        }
        for m in multiples_choisis:
            agregats_possibles.add(agregats_map[m])
        # Saisie de la valeur de chaque agrégat utile pour la valorisation
        valeurs_agregats = {}
        for agg in agregats_possibles:
            valeurs_agregats[agg] = st.number_input(
                f"Valeur de l'agrégat '{agg}' de l'entreprise à évaluer",
                min_value=0.0,
                step=1000.0,
                key=f"agregat_{agg}"
            )

        data = []
        for i in range(nb_entreprises):
            nom_entreprise = st.text_input(f"Nom de l'entreprise {i+1}", key=f"nom_{i}")
            for annee in range(nb_annees):
                st.markdown(f"**{nom_entreprise or f'Entreprise {i+1}'} - Année {annee + 1}**")
                ligne = {"Nom": nom_entreprise, "Année": annee + 1}
                for col in donnees_disponibles:
                    ligne[col] = st.number_input(
                        f"{col} - {nom_entreprise or f'Entreprise {i+1}'} - Année {annee + 1}",
                        min_value=0.0,
                        step=1000.0,
                        key=f"{col}_{i}_{annee}"
                    )
                data.append(ligne)

        if data:
            df = pd.DataFrame(data)

            # Calcul des multiples à partir des données financières
            if "EV/EBITDA" in multiples_choisis:
                df["EV/EBITDA"] = np.where(
                    (df.get("Valeur d'entreprise (VE)", 0) > 0) & (df.get("EBE (EBITDA)", 0) > 0),
                    df["Valeur d'entreprise (VE)"] / df["EBE (EBITDA)"],
                    np.nan
                )
            if "EV/CA" in multiples_choisis:
                df["EV/CA"] = np.where(
                    (df.get("Valeur d'entreprise (VE)", 0) > 0) & (df.get("Chiffre d'affaires (CA)", 0) > 0),
                    df["Valeur d'entreprise (VE)"] / df["Chiffre d'affaires (CA)"],
                    np.nan
                )
            if "P/EBIT" in multiples_choisis:
                df["P/EBIT"] = np.where(
                    (df.get("Capitalisation boursière", 0) > 0) & (df.get("Résultat d'exploitation (EBIT)", 0) > 0),
                    df["Capitalisation boursière"] / df["Résultat d'exploitation (EBIT)"],
                    np.nan
                )
            if "P/S" in multiples_choisis:
                df["P/S"] = np.where(
                    (df.get("Capitalisation boursière", 0) > 0) & (df.get("Chiffre d'affaires (CA)", 0) > 0),
                    df["Capitalisation boursière"] / df["Chiffre d'affaires (CA)"],
                    np.nan
                )
            if "PER" in multiples_choisis:
                df["PER"] = np.where(
                    (df.get("Capitalisation boursière", 0) > 0) & (df.get("Résultat net", 0) > 0),
                    df["Capitalisation boursière"] / df["Résultat net"],
                    np.nan
                )
            if "PBR" in multiples_choisis:
                df["PBR"] = np.where(
                    (df.get("Capitalisation boursière", 0) > 0) & (df.get("Capitaux propres", 0) > 0),
                    df["Capitalisation boursière"] / df["Capitaux propres"],
                    np.nan
                )
    else:
        # Saisie directe des multiples
        st.markdown('<div class="subtitle"><span class="icon">🔢</span>Choix des multiples à utiliser</div>', unsafe_allow_html=True)
        multiples_choisis = st.multiselect(
            "Sélectionnez les multiples à utiliser",
            list(multiples_dependances.keys())
        )
        data = []
        for i in range(nb_entreprises):
            nom_entreprise = st.text_input(f"Nom de l'entreprise {i+1}", key=f"nom_{i}")
            for annee in range(nb_annees):
                st.markdown(f"**{nom_entreprise or f'Entreprise {i+1}'} - Année {annee + 1}**")
                ligne = {"Nom": nom_entreprise, "Année": annee + 1}
                for m in multiples_choisis:
                    ligne[m] = st.number_input(
                        f"{m} - {nom_entreprise or f'Entreprise {i+1}'} - Année {annee + 1}",
                        min_value=0.0,
                        step=0.01,
                        key=f"{m}_{i}_{annee}"
                    )
                data.append(ligne)
        if data:
            df = pd.DataFrame(data)

    # Affichage du tableau formaté avec MultiIndex pour colonnes (Multiple, Année)
    if multiples_choisis and data:
        noms_entreprises = df["Nom"].unique()
        annees = [int(a) for a in range(1, int(nb_annees)+1)]
        columns = []
        for m in multiples_choisis:
            for annee in annees:
                columns.append((m, f"Année {annee}"))
        table = []
        for nom_entreprise in noms_entreprises:
            ligne = []
            df_entreprise = df[df["Nom"] == nom_entreprise]
            for m in multiples_choisis:
                for annee in annees:
                    val = df_entreprise[df_entreprise["Année"] == annee][m].values
                    ligne.append(val[0] if len(val) > 0 else np.nan)
            table.append([nom_entreprise] + ligne)
        multi_columns = pd.MultiIndex.from_tuples([("Nom", "")] + columns)
        df_table = pd.DataFrame(table, columns=multi_columns)

        # Calcul des moyennes et médianes pour chaque colonne de multiple/année
        moyennes = ["Moyenne"]
        medianes = ["Médiane"]
        for col in columns:
            moyennes.append(df_table[col].mean())
            medianes.append(df_table[col].median())
        df_table.loc[len(df_table)] = moyennes
        df_table.loc[len(df_table)] = medianes

        st.markdown('<div class="subtitle"><span class="icon">📈</span>Tableau des multiples</div>', unsafe_allow_html=True)
        st.dataframe(df_table)

        # Sélection automatique de la valeur de référence pour chaque multiple (médiane année la plus récente)
        valeurs_ref = {}
        annee_recente = annees[-1]
        for m in multiples_choisis:
            mediane = df_table[(m, f"Année {annee_recente}")].iloc[-1]
            moyenne = df_table[(m, f"Année {annee_recente}")].iloc[-2]
            valeurs_ref[m] = mediane if not np.isnan(mediane) else moyenne

        st.markdown('<div class="subtitle"><span class="icon">⭐</span>Valeur de référence retenue</div>', unsafe_allow_html=True)
        st.table(pd.DataFrame([
            {"Multiple": m, "Valeur retenue": valeurs_ref[m]} for m in valeurs_ref
        ]))

        # Saisie de la valeur de l'agrégat si ce n'est pas déjà fait
        if not ('valeur_agregat' in locals() and valeur_agregat is not None):
            valeur_agregat = st.number_input(
                "Valeur de l'agrégat de l'entreprise à évaluer (ex: EBITDA, CA, etc.)",
                min_value=0.0,
                step=1000.0
            )

        # Calcul de la valeur estimée pour l'entreprise à évaluer
        if len(valeurs_ref) > 0 and len(valeurs_agregats) > 0:
            st.markdown('<div class="subtitle"><span class="icon">💰</span>Valeur estimée de l\'entreprise</div>', unsafe_allow_html=True)
            for m in valeurs_ref:
                agg = agregats_map[m]
                if agg in valeurs_agregats and valeurs_agregats[agg] is not None:
                    valeur = valeurs_ref[m] * valeurs_agregats[agg]
                    st.write(f"**{m}** : {valeurs_ref[m]:.2f} × {valeurs_agregats[agg]:.2f} ({agg}) = **{valeur:,.2f}**")

        st.markdown('<div class="subtitle"><span class="icon">🧾</span>Résumé de l\'évaluation</div>', unsafe_allow_html=True)
        resume = {
            "Nom de l'entreprise": nom,
            "Secteur": secteur,
            "Méthode": "Comparables (multi-années, variables dynamiques)",
            "Multiples choisis": ", ".join(multiples_choisis),
            "Nombre d'années": nb_annees,
            "Nombre d'entreprises": nb_entreprises
        }
        if mode_saisie == "Saisir les données financières (CA, EBITDA...)":
            resume["Données utilisées"] = ", ".join(donnees_disponibles)
        if 'ebitda_user' in locals():
            resume["EBITDA utilisateur"] = ebitda_user

        st.table(pd.DataFrame(resume.items(), columns=["Élément", "Valeur"]))

elif st.session_state.page == "Méthode DCF":
    st.markdown('<div class="main-title">💸 Méthode DCF</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card">Estimez la valeur de votre entreprise par actualisation des flux de trésorerie futurs.</div>', unsafe_allow_html=True)

    st.markdown('<div class="subtitle"><span class="icon">📝</span>Informations sur l\'entreprise à évaluer</div>', unsafe_allow_html=True)
    nom = st.text_input("Nom de l'entreprise")
    secteur = st.text_input("Secteur d'activité")
    nb_annees = st.number_input("Nombre d'années de prévision", min_value=1, max_value=10, value=5)

    st.markdown('<div class="subtitle"><span class="icon">💵</span>Flux de trésorerie prévisionnels</div>', unsafe_allow_html=True)
    cash_flows = []
    for i in range(nb_annees):
        cf = st.number_input(f"Flux année {i+1}", key=f"cf_{i}", step=1000.0)
        cash_flows.append(cf)

    taux_actualisation = st.slider("Taux d'actualisation (%)", 0.0, 20.0, 10.0) / 100

    st.markdown('<div class="subtitle"><span class="icon">⏳</span>Flux de trésorerie actualisés</div>', unsafe_allow_html=True)
    def actualise(flux, taux):
        return sum(cf / (1 + taux) ** (i + 1) for i, cf in enumerate(flux))
    if st.button("Calculer la valeur DCF"):
        valeur = actualise(cash_flows, taux_actualisation)
        st.success(f"🎯 Valeur estimée par DCF : {valeur:,.2f}")
        df_flux = pd.DataFrame({
            "Année": [f"Année {i+1}" for i in range(nb_annees)],
            "Flux": cash_flows,
            "Flux actualisé": [cf / (1 + taux_actualisation) ** (i + 1) for i, cf in enumerate(cash_flows)]
        })
        st.dataframe(df_flux.style.format("{:.2f}"))

        st.markdown('<div class="subtitle"><span class="icon">🧾</span>Résumé de l\'évaluation</div>', unsafe_allow_html=True)
        resume = {
            "Nom de l'entreprise": nom,
            "Secteur": secteur,
            "Méthode": "DCF",
            "Taux d'actualisation (%)": taux_actualisation * 100,
            "Valeur estimée": valeur
        }
        for i, cf in enumerate(cash_flows):
            resume[f"Flux année {i+1}"] = cf

        st.table(pd.DataFrame(resume.items(), columns=["Élément", "Valeur"]))
