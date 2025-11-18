from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importa los routers
from app.routers import auth, candidates, companies, jobs, copilot, matching

app = FastAPI(
    title="MatchKey API",
    version="0.1.0",
)

# CORS (útil si algún día llamáis desde fuera de Docker / otro dominio)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción se puede cerrar
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluimos routers tal cual, SIN prefijos extra
app.include_router(auth.router)        # /auth/...
app.include_router(candidates.router)  # /candidates/...
app.include_router(companies.router)   # /companies/...
app.include_router(jobs.router)        # /jobs/...
app.include_router(copilot.router)     # /copilot/...
app.include_router(matching.router)    # /matching/...


@app.get("/health")
def health_check():
    return {"status": "ok"}
