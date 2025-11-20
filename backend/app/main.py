from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from app.routers import auth, candidates, companies, jobs, copilot, matching

# 🔥 Importamos los seeders
from app.db.init_db import init_db
from app.db.seed_jobs_from_scraping import seed_jobs_from_scraping
from app.db.seed_candidates_from_ocr import seed_candidates_from_ocr
from app.db.seed_fake_applications import seed_fake_applications



app = FastAPI(
    title="MatchKey API",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(candidates.router)
app.include_router(companies.router)
app.include_router(jobs.router)
# app.include_router(copilot.router)
app.include_router(matching.router)

# ------------------------------------------------------
# 🔥 EVENTO DE ARRANQUE DEL BACKEND (seed automático)
# ------------------------------------------------------
@app.on_event("startup")
def on_startup():
    # Crear tablas si no existen
    init_db()

    # Ingesta de vacantes
    seed_jobs_from_scraping()

    # Ingesta de candidatos desde el OCR
    seed_candidates_from_ocr()


@app.get("/health")
def health_check():
    return {"status": "ok"}
