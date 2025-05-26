import streamlit as st
from pages.accueil import page_accueil
from pages.comparables import page_comparables
from pages.dcf import page_dcf
from pages.dividendes import page_dividendes  
st.set_page_config(page_title="Évaluation d'Entreprise", layout="wide")

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

st.markdown("---")

if st.session_state.page == "Accueil":
    page_accueil()
elif st.session_state.page == "Méthode des comparables":
    page_comparables()
elif st.session_state.page == "Méthode DCF":
    page_dcf()
elif st.session_state.page == "Méthode des dividendes":
    page_dividendes()  



