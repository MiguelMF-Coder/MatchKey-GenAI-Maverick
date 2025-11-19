FROM python:3.11-slim

# Evitar prompts interactivos y mejorar logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema (psycopg2, tesseract, pdf2image/poppler, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    tesseract-ocr \
    tesseract-ocr-spa \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requirements
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
CMD ["/entrypoint.sh"]
