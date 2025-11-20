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
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Instalar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Descargar modelo de spaCy en español (para CVParser)
RUN python -m spacy download es_core_news_md

# Copiar la app
COPY app ./app

# Copiar entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
