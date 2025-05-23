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

   # Saisie du nombre d'actions pour la société à valoriser (toujours affiché)
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
       # Liste de base
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
       # Gestion de l'exclusivité
       donnees_preselectionnees = st.session_state.get("donnees_disponibles", [])
       # Si capitalisation boursière sélectionnée, on retire les deux autres
       if "Capitalisation boursière" in donnees_preselectionnees:
           filtered_options = [d for d in donnees_possibles if d not in ["Cours de l'action", "Nombre d'actions"]]
       # Si l'un des deux autres sélectionné, on retire capitalisation boursière
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


       # Détection automatique de la capitalisation boursière si cours et nombre d'actions sont présents
       donnees_utilisables = set(donnees_disponibles)
       # On ajoute "Capitalisation boursière" virtuellement si les deux sont présents
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


       # Déterminer tous les agrégats nécessaires selon les multiples sélectionnés
       agregats_map = {
           "VE/EBITDA": ["EBE (EBITDA)"],
           "VE/CA": ["Chiffre d'affaires (CA)"],
           "P/EBIT": ["Résultat d'exploitation (EBIT)"],
           "P/S": ["Chiffre d'affaires (CA)"],
           "PER": ["Résultat net"],
           "PBR": ["Capitaux propres"]
       }
       st.markdown('<div class="subtitle"><span class="icon">🔢</span>Choix des agrégats à valoriser / utiliser</div>', unsafe_allow_html=True)
       # Proposer à l'utilisateur de sélectionner les agrégats associés aux multiples choisis
       agregats_possibles = []
       for m in multiples_choisis:
           if m in agregats_map:
               agregats_possibles.extend(agregats_map[m])
       agregats_selectionnes = st.multiselect(
           "Sélectionnez les agrégats de l'entreprise à valoriser",
           sorted(set(agregats_possibles))
       )
       # Saisie de la valeur de chaque agrégat sélectionné
       valeurs_agregats = {}
       st.markdown('<div class="subtitle"><span class="icon">🧮</span>Données de la société à valoriser</div>', unsafe_allow_html=True)
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
           if not nom_entreprise:
               st.warning(f"Veuillez renseigner le nom de l'entreprise {i+1} avant de saisir les autres champs.")
               continue
           for annee in range(nb_annees):
               st.markdown(f"**{nom_entreprise} - Année {annee + 1}**")
               ligne = {"Nom": nom_entreprise, "Année": annee + 1}
               for col in donnees_disponibles:
                   # Correction : adapte le type de step selon le type de la colonne
                   if col == "Cours de l'action" or col == "Nombre d'actions":
                       step_val = 0.01
                       min_val = 0.0
                   else:
                       step_val = 1000
                       min_val = 0
                   ligne[col] = st.number_input(
                       f"{col} - {nom_entreprise} - Année {annee + 1}",
                       min_value=min_val,
                       step=step_val,
                       key=f"{col}_{i}_{annee}"
                   )
               # Calcul automatique de la capitalisation boursière si besoin
               if "Cours de l'action" in ligne and "Nombre d'actions" in ligne:
                   ligne["Capitalisation boursière"] = ligne["Cours de l'action"] * ligne["Nombre d'actions"]
               data.append(ligne)


       if data:
           df = pd.DataFrame(data)


           # Calcul des multiples à partir des données financières
           if "VE/EBITDA" in multiples_choisis:
               df["VE/EBITDA"] = np.where(
                   (df.get("Valeur d'entreprise (VE)", 0) > 0) & (df.get("EBE (EBITDA)", 0) > 0),
                   df["Valeur d'entreprise (VE)"] / df["EBE (EBITDA)"],
                   np.nan
               )
           if "VE/CA" in multiples_choisis:
               df["VE/CA"] = np.where(
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
       # Ajout du choix des agrégats même en mode "Saisir directement les multiples"
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
           if not nom_entreprise:
               st.warning(f"Veuillez renseigner le nom de l'entreprise {i+1} avant de saisir les autres champs.")
               continue
           for annee in range(nb_annees):
               st.markdown(f"**{nom_entreprise} - Année {annee + 1}**")
               ligne = {"Nom": nom_entreprise, "Année": annee + 1}
               for m in multiples_choisis:
                   ligne[m] = st.number_input(
                       f"{m} - {nom_entreprise} - Année {annee + 1}",
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
       print(noms_entreprises)
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
       df_valeurs_ref = pd.DataFrame([
           {"Multiple": m, "Valeur retenue": valeurs_ref[m]} for m in valeurs_ref
       ])
       df_valeurs_ref["Valeur retenue"] = df_valeurs_ref["Valeur retenue"].apply(affiche_valeur)
       st.table(df_valeurs_ref)


       # Calcul de la valeur estimée pour l'entreprise à évaluer
       if len(valeurs_ref) > 0 and len(valeurs_agregats) > 0 and nb_actions_societe > 0:
           st.markdown('<div class="subtitle"><span class="icon">💰</span>Valeur estimée de l\'entreprise</div>', unsafe_allow_html=True)
           # Construction du tableau résultat
           result_rows = []
           prix_par_action = {}
           for agg in agregats_selectionnes:
               for m in valeurs_ref:
                   # Vérifie que l'agrégat correspond au multiple
                   agg_list = agregats_map.get(m, [])
                   if agg in agg_list and agg in valeurs_agregats and valeurs_agregats[agg] is not None:
                       valeur_agregat = valeurs_agregats[agg]
                       valeur_multiple = valeurs_ref[m]
                       valeur_entreprise = valeur_agregat * valeur_multiple
                       prix_action = valeur_entreprise / nb_actions_societe if nb_actions_societe > 0 else np.nan
                       prix_par_action[m] = prix_action
                       result_rows.append({
                           "Agrégat": agg,
                           "Valeur agrégat": affiche_valeur(valeur_agregat),
                           "Multiple retenu": affiche_valeur(valeur_multiple),
                           "Valeur estimée entreprise": affiche_valeur(valeur_entreprise),
                           "Prix par action": affiche_valeur(prix_action)
                       })
           if result_rows:
               st.table(pd.DataFrame(result_rows))
           # Tableau final prix unitaire par action (une ligne, colonnes = multiples)
           if prix_par_action:
               st.markdown('<div class="subtitle"><span class="icon">🏷️</span>Prix unitaire par action (par multiple)</div>', unsafe_allow_html=True)
               st.table(pd.DataFrame([{k: affiche_valeur(v) for k, v in prix_par_action.items()}], index=["Prix par action"]))
               # Ajout du prix unitaire moyen
               prix_vals = [v for v in prix_par_action.values() if v is not None and not np.isnan(v)]
               if prix_vals:
                   prix_moyen = sum(prix_vals) / len(prix_vals)
                   st.markdown('<div class="subtitle"><span class="icon">📏</span>Prix unitaire moyen</div>', unsafe_allow_html=True)
                   st.write(affiche_valeur(prix_moyen))


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


       st.table(pd.DataFrame(resume.items(), columns=["Élément", "Valeur"]).applymap(affiche_valeur))
