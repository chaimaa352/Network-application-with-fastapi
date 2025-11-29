FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copie des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY . .

# Exposition du port
EXPOSE 8000

# Santé check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000')" || exit 1

# Commande de démarrage
# ⚠️ IMPORTANT: Adaptez selon votre fichier principal
# Si votre fichier s'appelle main.py avec app = FastAPI():
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Alternatives selon votre structure:
# Si app.py: CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
# Si src/main.py: CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Si server.py: CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]