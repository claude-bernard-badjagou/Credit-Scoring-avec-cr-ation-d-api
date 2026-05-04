# 1. Utiliser une image Python légère (slim) pour réduire la taille du conteneur
FROM python:3.9-slim

# 2. Définir le répertoire de travail à l'intérieur du conteneur
WORKDIR /app

# 3. Installer les dépendances système nécessaires (si besoin pour LightGBM/Sklearn)
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

# 4. Copier d'abord le fichier requirements.txt pour optimiser le cache Docker
COPY requirements.txt .

# 5. Installer les bibliothèques Python listées (FastAPI, uvicorn, scikit-learn, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copier tout le contenu de votre projet dans le conteneur (main.py, dossier model/, etc.)
COPY . .

# 7. Exposer le port sur lequel l'API va écouter (8000 par défaut pour FastAPI)
EXPOSE 8000

# 8. Commande de lancement du serveur uvicorn
# On utilise 0.0.0.0 pour que l'API soit accessible de l'extérieur du conteneur
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]