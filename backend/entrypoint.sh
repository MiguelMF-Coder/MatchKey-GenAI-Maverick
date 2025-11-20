#!/usr/bin/env bash
set -e

echo "⏳ Inicializando base de datos (init_db)..."
python -m app.db.init_db || echo "⚠️ init_db ha fallado (quizá las tablas ya existen)"

echo "🌱 Haciendo seed/actualización de jobs desde jobs_final.json..."
python -m app.db.seed_jobs_from_scraping || echo "⚠️ seed_jobs_from_scraping ha fallado, continúo igualmente"

echo "🌱 Haciendo seed de empresas + cultura desde values_dataset.json..."
python -m app.db.seed_companies_from_values_dataset || echo "⚠️ seed_companies_from_values_dataset ha fallado, continúo igualmente"

echo "🌱 Haciendo seed de candidatos desde OCR (si aplica)..."
python -m app.db.seed_candidates_from_ocr || echo "⚠️ seed_candidates_from_ocr ha fallado, continúo igualmente"

echo "🌱 Haciendo seed de aplicaciones falsas para la demo..."
python -m app.db.seed_fake_applications || echo "⚠️ seed_fake_applications ha fallado, continúo igualmente"

echo "🚀 Levantando backend FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
