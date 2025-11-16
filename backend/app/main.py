from fastapi import FastAPI
from .routers import auth, candidates, companies, jobs, copilot, matching

app = FastAPI(title="MatchKey Backend")

@app.get("/")
def root():
    return {"message": "MatchKey Backend is running"}

# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
app.include_router(companies.router, prefix="/companies", tags=["companies"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(copilot.router, prefix="/copilot", tags=["copilot"])
app.include_router(matching.router, prefix="/matching", tags=["matching"])
