import streamlit as st
import requests

# Configuration de la page
st.set_page_config(page_title="Djamo Credit Scoring", page_icon="💳")

st.title("💳 Simulateur de Crédit Djamo")
st.write("Entrez les informations du client pour obtenir une décision instantanée.")

# Formulaire de saisie
with st.sidebar:
    st.header("Paramètres du Client")
    income = st.number_input("Revenu mensuel (FCFA)", min_value=0, value=500000)
    loan_amount = st.number_input("Montant du prêt souhaité", min_value=0, value=2000000)
    age = st.slider("Âge du client", 18, 80, 35)
    employment_years = st.slider("Années d'expérience", 0, 40, 10)

# Bouton de prédiction
if st.button("Évaluer le dossier"):
    # L'URL de votre API sur Render
    url = "https://credit-scoring-api-376e.onrender.com/v1/score"
    
    data = {
        "income": income,
        "loan_amount": loan_amount,
        "age": age,
        "employment_years": employment_years
    }
    
    with st.spinner("Analyse du risque en cours..."):
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                
                # Affichage du résultat
                score = result["score"]
                decision = result["decision"]
                
                st.subheader(f"Résultat : {decision}")
                
                if decision == "Accordé":
                    st.success(f"Le prêt est approuvé avec un score de {score:.2f}")
                else:
                    st.error(f"Le prêt est refusé. Score de risque : {score:.2f}")
                    
                st.progress(score)
            else:
                st.error("Erreur lors de l'appel à l'API. Vérifiez que Render est actif.")
        except Exception as e:
            st.error(f"Impossible de contacter l'API : {e}")