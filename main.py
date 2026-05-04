from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import pickle
import pandas as pd
import os

# 1. Définition du schéma de données (Pydantic)
# Cela remplace "additionalProp1": {} par un formulaire structuré dans Swagger
class CreditRequest(BaseModel):
    SK_ID_CURR: int = Field(..., example=100001)
    AMT_INCOME_TOTAL: float = Field(..., example=500000.0)
    AMT_CREDIT: float = Field(..., example=200000.0)
    AMT_ANNUITY: float = Field(..., example=15000.0)
    AMT_GOODS_PRICE: float = Field(..., example=200000.0)
    AVG_PAYMENT_DAYS_EARLY: float = Field(..., example=10.5)
    TOTAL_REPAID: float = Field(..., example=150000.0)
    NB_PREVIOUS_LOANS: int = Field(..., example=2)
    TOTAL_EXTERNAL_DEBT: float = Field(..., example=0.0)
    DEBT_INCOME_RATIO: float = Field(..., example=0.03)
    LOAN_TO_VALUE_RATIO: float = Field(..., example=1.0)
    # Note : Ajoutez ici les autres colonnes nécessaires si votre modèle en utilise plus

app = FastAPI(
    title="Djamo Credit Scoring Service",
    description="API de prédiction du risque de crédit pour l'inclusion financière.",
    version="1.0.0"
)

# 2. Chargement du modèle au lancement
MODEL_PATH = 'model/model_credit_scoring_v1.pkl'

if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
else:
    print(f"ERREUR : Le fichier {MODEL_PATH} est introuvable.")

# --- ROUTES POUR CORRIGER LES ERREURS 404 ---

@app.get("/")
def read_root():
    """Corrige l'erreur 404 sur '/' en redirigeant vers la doc ou un statut."""
    return {
        "status": "Online",
        "message": "Bienvenue sur l'API de Scoring Djamo",
        "documentation": "/docs"
    }

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Corrige l'erreur 404 sur 'favicon.ico' réclamée par les navigateurs."""
    return FileResponse(os.path.join("static", "favicon.ico")) if os.path.exists("static/favicon.ico") else None

# --- ENDPOINT DE SCORING ---

@app.post("/v1/score")
async def get_score(data: CreditRequest):
    """
    Calcule le score de crédit à partir des données transactionnelles et profil.
    """
    try:
        # Transformation de l'input Pydantic en DataFrame Pandas
        input_df = pd.DataFrame([data.model_dump()])
        
        # Calcul de la probabilité de défaut (classe 1)
        # Assurez-vous que les colonnes dans input_df correspondent exactement à l'entraînement
        probability = model.predict_proba(input_df)[0][1]
        
        # Transformation en Score Djamo (Échelle de 300 à 850)
        # Formule : Score haut = Risque bas
        djamo_score = int(850 - (probability * 550))
        
        return {
            "client_id": data.SK_ID_CURR,
            "score": djamo_score,
            "decision": "APPROUVÉ" if djamo_score > 600 else "REFUSÉ",
            "risk_level": "FAIBLE" if djamo_score > 750 else "ÉLEVÉ",
            "probability_of_default": round(float(probability), 4)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction : {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)