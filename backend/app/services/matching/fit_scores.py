# backend/app/services/matching/fit_scores.py

from typing import Iterable, List, Optional
from difflib import SequenceMatcher
from collections import Counter


def _norm(s: Optional[str]) -> str:
    return (s or "").strip().lower()


def _norm_list(xs: Optional[Iterable[str]]) -> List[str]:
    if not xs:
        return []
    return sorted({_norm(x) for x in xs if _norm(x)})


def _similarity(a: str, b: str) -> float:
    """Similaridad 0–1 entre dos cadenas."""
    a_n, b_n = _norm(a), _norm(b)
    if not a_n or not b_n:
        return 0.0
    return SequenceMatcher(None, a_n, b_n).ratio()


def _match_ratio(required: List[str], candidate: List[str]) -> float:
    """
    Proporción de skills requeridas que el candidato cubre.
    Cuenta match exacto o fuzzy >= 0.8.
    """
    if not required:
        return 0.0

    cand_set = set(candidate)
    matched = 0

    for req in required:
        if req in cand_set:
            matched += 1
            continue
        if any(_similarity(req, c) >= 0.8 for c in cand_set):
            matched += 1

    return matched / len(required)


# ---------------- SKILLS ----------------

def compute_skills_fit(
    candidate_skills: List[str],
    job_tech_stack: List[str],
    job_soft_skills: List[str],
    job_languages: List[str],
) -> int:
    """
    Devuelve un score 0–100 de encaje en skills.
    """
    cand = _norm_list(candidate_skills)
    tech = _norm_list(job_tech_stack)
    soft = _norm_list(job_soft_skills)
    langs = _norm_list(job_languages)

    components = []

    if tech:
        components.append(("tech", _match_ratio(tech, cand)))
    if soft:
        components.append(("soft", _match_ratio(soft, cand)))
    if langs:
        components.append(("langs", _match_ratio(langs, cand)))

    if not components:
        # Si no tenemos info, devolvemos 50 para no penalizar.
        return 50

    base_weights = {"tech": 0.5, "soft": 0.3, "langs": 0.2}
    total_w = sum(base_weights[name] for name, _ in components)

    score = 0.0
    for name, ratio in components:
        w = base_weights[name] / total_w
        score += w * ratio * 100.0

    return int(round(score))


# ---------------- VALORES ----------------

def compute_values_fit(
    candidate_values: List[str],
    company_values: List[str],
    team_values_extra: Optional[List[str]] = None,
) -> int:
    """
    Jaccard suavizado entre valores del candidato y empresa/equipo.
    """
    cand_vals = set(_norm_list(candidate_values))
    comp_vals = set(_norm_list(company_values))

    if team_values_extra:
        comp_vals |= set(_norm_list(team_values_extra))

    if not cand_vals or not comp_vals:
        return 50  # neutro si no tenemos info

    inter = cand_vals & comp_vals
    union = cand_vals | comp_vals

    sim = len(inter) / len(union) if union else 0.0

    if len(inter) >= 3:
        sim = min(sim + 0.1, 1.0)  # pequeño bonus

    return int(round(sim * 100))


# ---------------- TEAM FIT ----------------

def _most_common_or_none(values: List[str]) -> Optional[str]:
    if not values:
        return None
    return Counter(_norm(v) for v in values if _norm(v)).most_common(1)[0][0]


def _map_autonomy(text: str) -> int:
    """
    Mapea texto de autonomía del equipo a escala 1–5 muy simple.
    """
    t = _norm(text)
    if not t:
        return 3
    if "muy alta" in t or "alta" in t:
        return 5
    if "media" in t or "moderada" in t:
        return 3
    if "baja" in t or "poca" in t:
        return 2
    return 3


def _score_autonomy(candidate_pref: Optional[int], team_autonomy_text: str) -> int:
    if not candidate_pref:
        return 50
    team_level = _map_autonomy(team_autonomy_text)
    diff = abs(candidate_pref - team_level)  # 0–4
    return max(20, 100 - diff * 20)  # 0→100, 4→20


def compute_team_fit(
    candidate_work_style: Optional[str],
    candidate_communication: Optional[str],
    candidate_autonomy_pref: Optional[int],  # 1–5
    candidate_values: List[str],
    team_work_style: Optional[str],
    team_communication: Optional[str],
    team_autonomy: Optional[str],
    team_members_values: List[str],
) -> int:
    """
    Calcula un 0–100 de encaje en equipo.
    No necesita el ORM directamente, solo textos agregados.
    """

    team_work_style_text = team_work_style or ""
    team_comm_text = team_communication or ""
    team_autonomy_text = team_autonomy or ""

    # 1) Estilo de trabajo
    if candidate_work_style and team_work_style_text:
        style_sim = _similarity(candidate_work_style, team_work_style_text)
        style_score = int(round(style_sim * 100))
    else:
        style_score = 50

    # 2) Comunicación
    if candidate_communication and team_comm_text:
        comm_sim = _similarity(candidate_communication, team_comm_text)
        comm_score = int(round(comm_sim * 100))
    else:
        comm_score = 50

    # 3) Autonomía
    autonomy_score = _score_autonomy(candidate_autonomy_pref, team_autonomy_text)

    # 4) Valores del equipo (reusamos compute_values_fit)
    values_score = compute_values_fit(candidate_values, [], team_members_values)

    team_fit = (
        0.3 * style_score
        + 0.3 * comm_score
        + 0.2 * autonomy_score
        + 0.2 * values_score
    )

    return int(round(team_fit))


# ---------------- GLOBAL ----------------

def compute_global_fit(skills_score: int, values_score: int, team_score: int) -> int:
    """
    Media simple de los tres encajes, 0–100.
    """
    return int(round((skills_score + values_score + team_score) / 3))
