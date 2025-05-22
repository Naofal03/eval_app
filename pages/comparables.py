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

def page_comparables():
    st.markdown('<div class="main-title">📊 Méthode des comparables</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card">Comparez votre entreprise à des sociétés similaires pour estimer sa valeur.</div>', unsafe_allow_html=True)

    st.markdown('<div class="subtitle"><span class="icon">📝</span>Informations générales</div>', unsafe_allow_html=True)
    nom = st.text_input("Nom de l'entreprise")
    secteur = st.text_input("Secteur d'activité")
    nb_entreprises = st.number_input("Nombre d'entreprises comparables", min_value=1, max_value=100, value=1)
    nb_annees = st.number_input("Nombre d'années à considérer", min_value=1, max_value=100, value=1)

    mode_saisie = st.radio(
        "Mode de saisie des données",
        ["Saisir les données financières (CA, EBITDA...)", "Saisir directement les multiples"]
    )

    nb_actions_societe = st.number_input(
        "Nombre d'actions de la société à valoriser",
        min_value=0.0,
        step=100.0,
        key="nb_actions_societe"
    )

    multiples_dependances = {
        "VE/EBITDA": ["Valeur d'entreprise (VE)", "EBE (EBITDA)"],
        "VE/CA": ["Valeur d'entreprise (VE)", "Chiffre d'affaires (CA)"],
        "P/EBIT": ["Capitalisation boursière", "Résultat d'exploitation (EBIT)"],
        "P/S": ["Capitalisation boursière", "Chiffre d'affaires (CA)"],
        "PER": ["Capitalisation boursière", "Résultat net"],
        "PBR": ["Capitalisation boursière", "Capitaux propres"]
    }

    if mode_saisie == "Saisir les données financières (CA, EBITDA...)":
        st.markdown('<div class="subtitle"><span class="icon">📑</span>Données disponibles</div>', unsafe_allow_html=True)
        donnees_possibles = [
            "Capitalisation boursière",
            "Valeur d'entreprise (VE)",
            "Dettes nettes",
            "Chiffre d'affaires (CA)",
            "EBE (EBITDA)",
            "Résultat d'exploitation (EBIT)",
            "Résultat net",
            "Capitaux propres",
            "Cours de l'action",
            "Nombre d'actions"
        ]
        donnees_preselectionnees = st.session_state.get("donnees_disponibles", [])
        if "Capitalisation boursière" in donnees_preselectionnees:
            filtered_options = [d for d in donnees_possibles if d not in ["Cours de l'action", "Nombre d'actions"]]
        elif "Cours de l'action" in donnees_preselectionnees or "Nombre d'actions" in donnees_preselectionnees:
            filtered_options = [d for d in donnees_possibles if d != "Capitalisation boursière"]
        else:
            filtered_options = donnees_possibles

        donnees_disponibles = st.multiselect(
            "Cochez les données que vous avez pour chaque entreprise et année",
            filtered_options,
            default=donnees_preselectionnees,
            key="donnees_disponibles"
        )

        donnees_utilisables = set(donnees_disponibles)
        if "Cours de l'action" in donnees_utilisables and "Nombre d'actions" in donnees_utilisables:
            donnees_utilisables.add("Capitalisation boursière")

        multiples_possibles = [
            m for m, deps in multiples_dependances.items()
            if all(dep in donnees_utilisables for dep in deps)
        ]

        st.markdown('<div class="subtitle"><span class="icon">🔢</span>Choix des multiples à calculer/utiliser</div>', unsafe_allow_html=True)
        multiples_choisis = st.multiselect(
            "Sélectionnez les multiples à utiliser",
            multiples_possibles
        )

        agregats_map = {
            "VE/EBITDA": ["EBE (EBITDA)"],
            "VE/CA": ["Chiffre d'affaires (CA)"],
            "P/EBIT": ["Résultat d'exploitation (EBIT)"],
            "P/S": ["Chiffre d'affaires (CA)"],
            "PER": ["Résultat net"],
            "PBR": ["Capitaux propres"]
        }
        st.markdown('<div class="subtitle"><span class="icon">🔢</span>Choix des agrégats à valoriser / utiliser</div>', unsafe_allow_html=True)
        agregats_possibles = []
        for m in multiples_choisis:
            if m in agregats_map:
                agregats_possibles.extend(agregats_map[m])
        agregats_selectionnes = st.multiselect(
            "Sélectionnez les agrégats de l'entreprise à valoriser",
            sorted(set(agregats_possibles))
        )
        valeurs_agregats = {}
        st.markdown('<div class="subtitle"><span class="icon">🧮</span>Données de la société à valoriser</div>', unsafe_allow_html=True)
        afficher_dette_nette = (
            "Dettes nettes" in donnees_disponibles or
            any(m in ["VE/EBITDA", "VE/CA"] for m in multiples_choisis)
        )
        if afficher_dette_nette:
            dette_nette_societe = st.number_input(
                "Dettes nettes de la société à valoriser",
                min_value=0.0,
                step=1000.0,
                key="dette_nette_societe"
            )
            valeurs_agregats["Dettes nettes"] = dette_nette_societe
        for agg in agregats_selectionnes:
            valeurs_agregats[agg] = st.number_input(
                f"Valeur de l'agrégat '{agg}' de l'entreprise à évaluer",
                min_value=0,
                step=1000,
                key=f"agregat_{agg}"
            )

        data = []
        for i in range(nb_entreprises):
            nom_entreprise = st.text_input(f"Nom de l'entreprise {i+1}", key=f"nom_{i}")
            for annee in range(nb_annees):
                st.markdown(f"**{nom_entreprise or f'Entreprise {i+1}'} - Année {annee + 1}**")
                ligne = {"Nom": nom_entreprise, "Année": annee + 1}
                for col in donnees_disponibles:
                    if col == "Cours de l'action" or col == "Nombre d'actions":
                        step_val = 0.01
                        min_val = 0.0
                    else:
                        step_val = 1000
                        min_val = 0
                    ligne[col] = st.number_input(
                        f"{col} - {nom_entreprise or f'Entreprise {i+1}'} - Année {annee + 1}",
                        min_value=min_val,
                        step=step_val,
                        key=f"{col}_{i}_{annee}"
                    )
                if "Cours de l'action" in ligne and "Nombre d'actions" in ligne:
                    ligne["Capitalisation boursière"] = ligne["Cours de l'action"] * ligne["Nombre d'actions"]
                data.append(ligne)

        if data:
            df = pd.DataFrame(data)
            # ...calculs des multiples, affichages, etc. (reprendre la logique du main)...
            # ...existing code...
    else:
        # Saisie directe des multiples
        st.markdown('<div class="subtitle"><span class="icon">🔢</span>Choix des multiples à utiliser</div>', unsafe_allow_html=True)
        multiples_choisis = st.multiselect(
            "Sélectionnez les multiples à utiliser",
            list(multiples_dependances.keys())
        )
        agregats_map = {
            "VE/EBITDA": ["EBE (EBITDA)"],
            "VE/CA": ["Chiffre d'affaires (CA)"],
            "P/EBIT": ["Résultat d'exploitation (EBIT)"],
            "P/S": ["Chiffre d'affaires (CA)"],
            "PER": ["Résultat net"],
            "PBR": ["Capitaux propres"]
        }
        st.markdown('<div class="subtitle"><span class="icon">🔢</span>Choix des agrégats à valoriser / utiliser</div>', unsafe_allow_html=True)
        agregats_possibles = []
        for m in multiples_choisis:
            if m in agregats_map:
                agregats_possibles.extend(agregats_map[m])
        agregats_selectionnes = st.multiselect(
            "Sélectionnez les agrégats de l'entreprise à valoriser",
            sorted(set(agregats_possibles))
        )
        valeurs_agregats = {}
        st.markdown('<div class="subtitle"><span class="icon">🧮</span>Données de la société à valoriser</div>', unsafe_allow_html=True)
        afficher_dette_nette = any(m in ["VE/EBITDA", "VE/CA"] for m in multiples_choisis)
        if afficher_dette_nette:
            dette_nette_societe = st.number_input(
                "Dettes nettes de la société à valoriser",
                min_value=0.0,
                step=1000.0,
                key="dette_nette_societe"
            )
            valeurs_agregats["Dettes nettes"] = dette_nette_societe
        for agg in agregats_selectionnes:
            valeurs_agregats[agg] = st.number_input(
                f"Valeur de l'agrégat '{agg}' de l'entreprise à évaluer",
                min_value=0,
                step=1000,
                key=f"agregat_{agg}"
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
            # ...affichage des tableaux, calculs, etc. (reprendre la logique du main)...
            # ...existing code...
