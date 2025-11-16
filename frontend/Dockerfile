FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la app de Streamlit
COPY . .

EXPOSE 8501

# Comando de arranque
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
