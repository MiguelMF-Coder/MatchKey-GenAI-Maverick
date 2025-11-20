FROM python:3.11-slim

# Evitar prompts interactivos
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema (psycopg2, tesseract, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    tesseract-ocr \
    tesseract-ocr-spa \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*
# Note: ffmpeg removed - using Groq API for audio transcription instead of local Whisper

# Instalar requirements
COPY requirements.txt .
# Añadimos script inline con reintentos para instalación
RUN set -e; \
    for i in 1 2 3; do \
      echo "[pip install intento $i]"; \
      pip install --no-cache-dir -r requirements.txt && break || sleep 5; \
    done; \
    python -m pip install --upgrade pip; \
    echo "Instalando modelo spaCy es_core_news_md con reintentos"; \
    for i in 1 2 3; do \
      python -m spacy download es_core_news_md && break || sleep 5; \
    done

# Copiar la app
COPY app ./app

# Copiar entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
