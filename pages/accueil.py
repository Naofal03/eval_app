import streamlit as st

def page_accueil():
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
       .info-card {
           background: #f7fafc;
           border-radius: 10px;
           padding: 1.5em;
           margin-bottom: 1em;
           box-shadow: 0 2px 8px rgba(44,62,80,0.07);
           animation: fadein 1.2s;
       }
       @keyframes fadein {
           from { opacity: 0; transform: translateY(30px);}
           to { opacity: 1; transform: translateY(0);}
       }
       </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="main-title">👋 Bienvenue dans l\'application d\'évaluation</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card">Choisissez une méthode pour commencer votre évaluation.<br><br>'
                '<span style="font-size:1.1em;">'
                '📊 <b>Méthode des comparables</b> : Comparez votre entreprise à des sociétés similaires.<br>'
                '💸 <b>Méthode DCF</b> : Actualisez les flux de trésorerie futurs pour estimer la valeur.<br>'
                '📈 <b>Méthode des dividendes (DDM)</b> : Actualisez les dividendes futurs attendus pour valoriser l\'entreprise.<br>'
                '</span></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="margin-top:2em; text-align:center;">
            <img src="https://cdn.pixabay.com/photo/2017/01/10/19/05/analysis-1974641_1280.png" width="45%" style="border-radius:12px;box-shadow:0 2px 8px rgba(44,62,80,0.07);">
        </div>
        """,
        unsafe_allow_html=True
    )
