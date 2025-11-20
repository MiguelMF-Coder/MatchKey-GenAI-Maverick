# backend/app/routers/matching.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.candidates import Candidate
from app.models.jobs import Job, TeamProfile, TeamMember
from app.models.skills import CandidateSkill, JobSkill

router = APIRouter()


# -------------------------
# Helpers de normalización
# -------------------------
def _norm(s: str) -> str:
    return s.lower().strip()


def _to_list(val):
    if not val:
        return []
    if isinstance(val, list):
        return val
    return [val]


# -------------------------
# Cálculos de encaje
# -------------------------
def compute_skills_fit(cand_skill_names, job: Job) -> int:
    """
    Calcula encaje en skills mezclando:
    - JobSkill.must_have
    - JobSkill.nice_to_have
    - job.tech_stack (del scraping)
    """
    cand_set = {_norm(s) for s in cand_skill_names if s}

    # JobSkill desde la tabla job_skills
    must = []
    nice = []

    for js in job.skills or []:
        name = _norm(js.skill_name)
        if js.importance == "must_have":
            must.append(name)
        else:
            nice.append(name)

    # Tech stack del scraping
    tech_stack = [_norm(s) for s in _to_list(job.tech_stack)]

    # Si no tenemos nada en job_skills, usamos tech_stack como must
    if not must and tech_stack:
        must = tech_stack

    must_set = set(must)
    nice_set = set(nice)

    if not must_set and not nice_set:
        # No tenemos info estructurada de skills → neutro
        return 50

    # Cobertura de must-have
    if must_set:
        must_covered = len(cand_set & must_set) / len(must_set)
    else:
        must_covered = 1.0  # si no hay must, se considera todo cubierto

    # Cobertura de nice-to-have
    if nice_set:
        nice_covered = len(cand_set & nice_set) / len(nice_set)
    else:
        nice_covered = 0.0

    score = 100 * (0.7 * must_covered + 0.3 * nice_covered)
    return int(round(max(0, min(score, 100))))


def compute_values_fit(candidate: Candidate, job: Job) -> int | None:
    """
    Encaje en valores: aproximación muy simple con texto.
    Si no hay datos de equipo, devolvemos None.
    """
    if not job.team_profile:
        return None

    # Texto del equipo (valores / estilo)
    team_text_parts = [
        job.team_profile.team_mission or "",
        job.team_profile.team_work_style or "",
        job.team_profile.team_communication or "",
        job.team_profile.team_ideal_profile or "",
    ]

    # Añadimos valores de miembros si existen
    for m in job.team_profile.members or []:
        if m.values:
            team_text_parts.append(m.values)

    team_text = " ".join(team_text_parts).lower()

    if not team_text.strip():
        return None

    # Texto del candidato
    cand_text = " ".join([
        candidate.summary or "",
        candidate.headline or "",
    ]).lower()

    if not cand_text.strip():
        # Sin info del candidato → neutro
        return 50

    # Tokens simples
    team_tokens = {w for w in team_text.split() if len(w) > 3}
    cand_tokens = {w for w in cand_text.split() if len(w) > 3}

    if not team_tokens:
        return None

    inter = len(team_tokens & cand_tokens)
    union = len(team_tokens | cand_tokens)

    if union == 0:
        return 50

    jaccard = inter / union
    score = 50 + 50 * jaccard  # centrado en 50, sube si hay overlap
    return int(round(max(0, min(score, 100))))


def compute_team_fit(candidate: Candidate, job: Job) -> int | None:
    """
    Encaje en equipo: muy simple, basado en similitud de palabras clave
    entre 'team_work_style' y el summary/headline del candidato.
    """
    if not job.team_profile:
        return None

    team_style = " ".join([
        job.team_profile.team_work_style or "",
        job.team_profile.team_communication or "",
        job.team_profile.team_autonomy or "",
    ]).lower()

    if not team_style.strip():
        return None

    cand_text = " ".join([
        candidate.summary or "",
        candidate.headline or "",
    ]).lower()

    if not cand_text.strip():
        return 50

    team_tokens = {w for w in team_style.split() if len(w) > 3}
    cand_tokens = {w for w in cand_text.split() if len(w) > 3}

    if not team_tokens:
        return None

    inter = len(team_tokens & cand_tokens)
    union = len(team_tokens | cand_tokens)

    if union == 0:
        return 50

    jaccard = inter / union
    score = 50 + 50 * jaccard
    return int(round(max(0, min(score, 100))))


def compute_global_fit(skills_fit: int | None,
                       values_fit: int | None,
                       team_fit: int | None) -> int:
    """
    Global = media ponderada de lo que tengamos disponible.
    """
    parts = []
    weights = []

    if skills_fit is not None:
        parts.append(skills_fit)
        weights.append(0.6)

    if values_fit is not None:
        parts.append(values_fit)
        weights.append(0.2)

    if team_fit is not None:
        parts.append(team_fit)
        weights.append(0.2)

    if not parts:
        return 50

    if len(parts) == 1:
        return int(parts[0])

    w_sum = sum(weights)
    weighted = sum(p * w for p, w in zip(parts, weights)) / w_sum
    return int(round(max(0, min(weighted, 100))))


# -------------------------
# Endpoint principal
# -------------------------
@router.get("/candidates/{candidate_id}/job/{job_id}/scores")
def get_match_scores(candidate_id: int, job_id: int, db: Session = Depends(get_db)):
    # ----- Candidato -----
    candidate: Candidate | None = (
        db.query(Candidate).filter_by(id=candidate_id).first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Skills del candidato (tabla candidate_skills)
    cand_skill_rows = (
        db.query(CandidateSkill)
        .filter_by(candidate_id=candidate.id)
        .all()
    )

    cand_skills = [cs.skill_name for cs in cand_skill_rows if cs.skill_name]

    # ----- Job -----
    job: Job | None = db.query(Job).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Cálculo de scores
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
