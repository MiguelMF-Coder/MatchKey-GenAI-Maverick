from typing import List, Set
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.candidates import Candidate
from app.models.jobs import Job
from app.models.skills import CandidateSkill, JobSkill
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/matching", tags=["matching"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _normalize_skill(s: str) -> str:
    return s.strip().lower()


def compute_skills_fit(cand_skills: List[str],
                       job_must: Set[str],
                       job_nice: Set[str]) -> int:
    """
    Encaje en skills (0–100) basado en:
    - porcentaje de must_have cubiertos
    - porcentaje de nice_to_have cubiertos
    Fórmula:
      score = 100 * (0.7 * must_ratio + 0.3 * nice_ratio)
    """
    cand_set = {_normalize_skill(s) for s in cand_skills if s}

    must_total = len(job_must)
    nice_total = len(job_nice)

    # Si no tenemos skills en la vacante, devolvemos algo neutro
    if must_total == 0 and nice_total == 0:
        return 50

    must_match = len(cand_set & job_must)
    nice_match = len(cand_set & job_nice)

    must_ratio = must_match / must_total if must_total else 1.0
    nice_ratio = nice_match / nice_total if nice_total else 0.0

    score = 100 * (0.7 * must_ratio + 0.3 * nice_ratio)
    return int(round(max(0, min(score, 100))))


def compute_values_fit(candidate: Candidate, job: Job) -> int:
    """
    Encaje en valores (0–100).
    Dado el esquema actual, no tenemos valores del candidato explícitos en la tabla,
    pero sí sabemos:
    - si ha hecho entrevistas (HR Copilot) → candidate.interviews
    - si el job tiene team_profile con miembros y valores de equipo
    Usamos eso para dar un score razonable, basado en la información disponible.
    """
    has_interview = bool(candidate.interviews)

    has_team_values = False
    if job.team_profile and job.team_profile.members:
        for m in job.team_profile.members:
            if m.values:
                has_team_values = True
                break

    if has_interview and has_team_values:
        base = 70
    elif has_interview or has_team_values:
        base = 60
    else:
        base = 50

    return base


def compute_team_fit(candidate: Candidate, job: Job) -> int:
    """
    Encaje en equipo (0–100).
    Usamos:
    - existencia de TeamProfile
    - nº de miembros del equipo
    - si el candidato tiene entrevista (HR Copilot) para ajustar un poco.
    Es un modelo sencillo pero basado en datos reales de tu esquema.
    """
    tp = job.team_profile
    if not tp or not tp.members:
        # No tenemos info del equipo → valor neutro
        base = 55
    else:
        n_members = len(tp.members)
        if n_members <= 2:
            base = 60
        elif 3 <= n_members <= 7:
            base = 70
        else:
            base = 65

    if candidate.interviews:
        base += 5  # ligera mejora si tenemos info de IA

    return min(base, 100)


def compute_global_fit(skills_fit: int, values_fit: int, team_fit: int) -> int:
    """
    Encaje global = media simple de los tres.
    """
    return int(round((skills_fit + values_fit + team_fit) / 3))


@router.get("/candidates/{candidate_id}/job/{job_id}/scores")
def get_match_scores(candidate_id: int, job_id: int, db: Session = Depends(get_db)):
    # ---------- CANDIDATO ----------
    candidate: Candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id)
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Skills del candidato desde CandidateSkill.skill_name (relación real)
    cand_skills = [cs.skill_name for cs in candidate.skills]

    # ---------- JOB ----------
    job: Job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Skills de la vacante desde JobSkill (must / nice)
    job_must: Set[str] = set()
    job_nice: Set[str] = set()

    for js in job.skills:
        skill_norm = _normalize_skill(js.skill_name)
        if js.importance == "must_have":
            job_must.add(skill_norm)
        else:
            job_nice.add(skill_norm)

    # Extra: añadimos tech_stack / soft_skills / languages como "nice_to_have"
    extra_fields = [job.tech_stack, job.soft_skills, job.languages]
    for field in extra_fields:
        if not field:
            continue
        if isinstance(field, list):
            for s in field:
                job_nice.add(_normalize_skill(str(s)))
        elif isinstance(field, str):
            job_nice.add(_normalize_skill(field))

    # ---------- ALGORTIMOS DE ENCAJE ----------
    skills_fit = compute_skills_fit(cand_skills, job_must, job_nice)
    values_fit = compute_values_fit(candidate, job)
    team_fit = compute_team_fit(candidate, job)
    global_fit = compute_global_fit(skills_fit, values_fit, team_fit)

    return {
        "skills_fit": skills_fit,
        "values_fit": values_fit,
        "team_fit": team_fit,
        "global_fit": global_fit,
    }
