# backend/app/routers/matching.py

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.candidates import Candidate
from app.models.jobs import Job
from app.services.matching.matching_engine import (
    build_candidate_skills_list,
    compute_skills_fit,
    compute_values_fit,
    compute_team_fit,
    compute_global_fit,
)

router = APIRouter(prefix="/matching", tags=["matching"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/candidates/{candidate_id}/job/{job_id}/scores")
def get_match_scores(
    candidate_id: int,
    job_id: int,
    db: Session = Depends(get_db),
):
    # ----- CANDIDATO -----
    candidate: Optional[Candidate] = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id)
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # ----- JOB -----
    job: Optional[Job] = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # ----- SKILLS DEL CANDIDATO -----
    cand_skills = build_candidate_skills_list(db, candidate)

    # ----- CÁLCULOS -----
    skills_fit = compute_skills_fit(cand_skills, job)
    values_fit = compute_values_fit(candidate, job)
    team_fit = compute_team_fit(candidate, job)
    global_fit = compute_global_fit(skills_fit, values_fit, team_fit)

    return {
        "skills_fit": skills_fit,
        "values_fit": values_fit,
        "team_fit": team_fit,
        "global_fit": global_fit,
    }
