# Utilisation d'une image de base légère
FROM python:3.11-slim

# Sécurité : Création d'un utilisateur non-root
RUN adduser --disabled-password --gecos '' appuser

# Définition du répertoire de travail
WORKDIR /app

# Installation des dépendances (optimisation du cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Sécurité : Bascule sur l'utilisateur restreint
USER appuser

# Exposition du port
EXPOSE 8000

# Commande de lancement
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]