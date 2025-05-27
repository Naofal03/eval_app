# Application d'Évaluation d'Entreprise

Cette application Streamlit permet d'évaluer une entreprise selon plusieurs méthodes financières classiques.

## Structure des fichiers

- **main.py** : Interface principale, choix de la méthode, informations générales sur l'entreprise, navigation personnalisée.
- **pages/accueil.py** : Page d'accueil, explication des méthodes disponibles.
- **pages/comparables.py** : Module dédié à la méthode des comparables (valorisation par multiples).
- **pages/dcf.py** : Module dédié à la méthode DCF (Discounted Cash Flow).
- **pages/dividendes.py** : Module dédié à la méthode des dividendes (DDM).


## Méthodes disponibles

- **Méthode des comparables** : Valorisation par comparaison avec des sociétés similaires (multiples de marché).
- **Méthode DCF** : Valorisation par actualisation des flux de trésorerie futurs (Discounted Cash Flow).
- **Méthode des dividendes (DDM)** : Valorisation par actualisation des dividendes futurs attendus.
- **Navigation** : Personnalisée via des boutons en haut de page, liens directs possibles via l'URL (`?page=dcf`, `?page=dividendes`, etc.).

## Installation des dépendances

Avant de lancer l'application, installez les dépendances nécessaires avec la commande suivante :

```bash
pip install -r requirements.txt
```

## Lancement

Dans le dossier du projet, lancez :
```bash
streamlit run main.py
```

## Remarques

- L'application ne nécessite pas la sidebar native de Streamlit (navigation gérée en interne).
- Les modules dans `pages/` sont importés et utilisés par `main.py` ; ils ne sont pas des pages Streamlit autonomes.
- Les données ne sont pas sauvegardées entre les sessions sauf si vous utilisez explicitement `data_storage.py`.

## Auteurs

- Naofal AKANHO



