# backend/app/services/matching/matching_engine.py

from typing import List, Sequence, Optional, Dict

from sqlalchemy.orm import Session

# 👇 IMPORTS CORRECTOS
from app.models.candidates import Candidate
from app.models.jobs import Job, TeamProfile, TeamMember
from app.models.skills import CandidateSkill, JobSkill


# -------------------------
# Helpers básicos
# -------------------------


def _norm(s: str) -> str:
    """Normaliza una skill / token a minúsculas y sin espacios extra."""
    return s.lower().strip()


def _to_list(val):
    """Convierte None / str / list en lista."""
    if not val:
        return []
    if isinstance(val, list):
        return val
    return [val]


def _tokenize(text: str) -> List[str]:
    """Tokenización muy simple: split por espacios, filtrando tokens muy cortos."""
    if not text:
        return []
    return [w for w in text.lower().split() if len(w) > 3]


# -------------------------
# Builders de skills
# -------------------------


def build_candidate_skills_list(db: Session, candidate: Candidate) -> List[str]:
    """
    Construye la lista de skills del candidato a partir de la tabla candidate_skills.
    """
    rows: Sequence[CandidateSkill] = (
        db.query(CandidateSkill)
        .filter(CandidateSkill.candidate_id == candidate.id)
        .all()
    )
    names = [row.skill_name for row in rows if row.skill_name]
    normalized = {_norm(n) for n in names if n}
    return sorted(normalized)


def build_job_skills_lists(job: Job) -> Dict[str, List[str]]:
    """
    Construye las listas de skills para el job separadas en:
    - must_have: desde JobSkill.importance == 'must_have' o, si no hay, tech_stack.
    - nice_to_have: desde JobSkill.importance != 'must_have'.
    - extra: skills adicionales (soft_skills, languages, tech_stack sobrante).

    Devuelve un dict:
    {
        "must_have": [...],
        "nice_to_have": [...],
        "extra": [...],
    }
    """
    must: List[str] = []
    nice: List[str] = []
    extra: List[str] = []

    # 1) JobSkill desde relación job.skills
    for js in getattr(job, "skills", []) or []:
        if not js.skill_name:
            continue
        name = _norm(js.skill_name)
        if js.importance == "must_have":
            must.append(name)
        else:
            nice.append(name)

    # 2) Tech stack del scraping
    tech_stack = [_norm(s) for s in _to_list(getattr(job, "tech_stack", []))]
    # 3) Soft skills y idiomas como extra
    soft_skills = [_norm(s) for s in _to_list(getattr(job, "soft_skills", []))]
    languages = [_norm(s) for s in _to_list(getattr(job, "languages", []))]

    # Si no hay must en JobSkill, usamos tech_stack como must
    if not must and tech_stack:
        must = tech_stack
    else:
        extra.extend(tech_stack)

    extra.extend(soft_skills)
    extra.extend(languages)

    must_set = {_norm(s) for s in must if s}
    nice_set = {_norm(s) for s in nice if s}
    extra_set = {_norm(s) for s in extra if s}

    extra_set = extra_set - must_set - nice_set

    return {
        "must_have": sorted(must_set),
        "nice_to_have": sorted(nice_set),
        "extra": sorted(extra_set),
    }


# Alias de compatibilidad si en algún lado se usa el nombre singular
def build_job_skills_list(job: Job) -> Dict[str, List[str]]:
    return build_job_skills_lists(job)


# -------------------------
# Cálculo de encaje en skills
# -------------------------


def compute_skills_fit_from_lists(
    cand_skill_names: Sequence[str],
    must_have: Sequence[str],
    nice_to_have: Sequence[str],
) -> int:
    """
    Calcula el encaje en skills a partir de:
    - cand_skill_names: skills del candidato.
    - must_have: lista de skills imprescindibles.
    - nice_to_have: lista de skills valorables.
    """
    cand_set = {_norm(s) for s in cand_skill_names if s}
    must_set = {_norm(s) for s in must_have if s}
    nice_set = {_norm(s) for s in nice_to_have if s}

    if not must_set and not nice_set:
        return 50

    if must_set:
        must_covered = len(cand_set & must_set) / len(must_set)
    else:
        must_covered = 1.0

    if nice_set:
        nice_covered = len(cand_set & nice_set) / len(nice_set)
    else:
        nice_covered = 0.0

    score = 100 * (0.7 * must_covered + 0.3 * nice_covered)
    return int(round(max(0, min(score, 100))))


def compute_skills_fit(
    cand_skill_names: Sequence[str],
    job: Job,
) -> int:
    """
    Atajo que:
    1) Construye must/nice a partir de job.skills + job.tech_stack + soft_skills + languages.
    2) Llama a compute_skills_fit_from_lists(...).
    """
    lists = build_job_skills_lists(job)
    must_have = lists["must_have"]
    nice_to_have = lists["nice_to_have"]
    return compute_skills_fit_from_lists(cand_skill_names, must_have, nice_to_have)


# -------------------------
# Encaje en valores y equipo
# -------------------------


def compute_values_fit(candidate: Candidate, job: Job) -> Optional[int]:
    """
    Encaje en valores: aproximación con texto.
    - Texto del equipo (misión, estilo, comunicación, ideal_profile, valores miembros)
    - Texto del candidato (summary + headline)
    → Jaccard de tokens
    """
    team_profile: Optional[TeamProfile] = getattr(job, "team_profile", None)
    if not team_profile:
        return None

    team_text_parts: List[str] = [
        team_profile.team_mission or "",
        team_profile.team_work_style or "",
        team_profile.team_communication or "",
        team_profile.team_ideal_profile or "",
    ]

    members: Sequence[TeamMember] = getattr(team_profile, "members", []) or []
    for m in members:
        if m.values:
            team_text_parts.append(m.values)

    team_text = " ".join(team_text_parts).lower()
    if not team_text.strip():
        return None

    cand_text = " ".join(
        [
            getattr(candidate, "summary", "") or "",
            getattr(candidate, "headline", "") or "",
        ]
    ).lower()

    if not cand_text.strip():
        return 50

    team_tokens = set(_tokenize(team_text))
    cand_tokens = set(_tokenize(cand_text))

    if not team_tokens:
        return None

    inter = len(team_tokens & cand_tokens)
    union = len(team_tokens | cand_tokens)

    if union == 0:
        return 50

    jaccard = inter / union
    score = 50 + 50 * jaccard
    return int(round(max(0, min(score, 100))))


def compute_team_fit(candidate: Candidate, job: Job) -> Optional[int]:
    """
    Encaje en equipo:
    - Texto de estilo de trabajo, comunicación y autonomía del equipo.
    - Texto del candidato (summary + headline).
    """
    team_profile: Optional[TeamProfile] = getattr(job, "team_profile", None)
    if not team_profile:
        return None

    team_style_text = " ".join(
        [
            team_profile.team_work_style or "",
            team_profile.team_communication or "",
            team_profile.team_autonomy or "",
        ]
    ).lower()

    if not team_style_text.strip():
        return None

    cand_text = " ".join(
        [
            getattr(candidate, "summary", "") or "",
            getattr(candidate, "headline", "") or "",
        ]
    ).lower()

    if not cand_text.strip():
        return 50

    team_tokens = set(_tokenize(team_style_text))
    cand_tokens = set(_tokenize(cand_text))

    if not team_tokens:
        return None

    inter = len(team_tokens & cand_tokens)
    union = len(team_tokens | cand_tokens)
    if union == 0:
        return 50

    jaccard = inter / union
    score = 50 + 50 * jaccard
    return int(round(max(0, min(score, 100))))


# -------------------------
# Global fit
# -------------------------


def compute_global_fit(
    skills_fit: Optional[int],
    values_fit: Optional[int],
    team_fit: Optional[int],
) -> int:
    """
    Global = media ponderada de lo que tengamos disponible.

    - Skills: 60%
    - Valores: 20%
    - Team fit: 20%
    """
    parts: List[int] = []
    weights: List[float] = []

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
