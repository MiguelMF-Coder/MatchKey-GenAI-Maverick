#!/usr/bin/env bash
set -e

echo "⏳ Inicializando base de datos (init_db)..."
python -m app.db.init_db || echo "⚠️ init_db ha fallado (quizá las tablas ya existen)"

echo "🌱 Haciendo seed/actualización de jobs desde jobs_final.json..."
python -m app.db.seed_jobs_from_scraping || echo "⚠️ seed_jobs_from_scraping ha fallado, continúo igualmente"

echo "🚀 Levantando backend FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
