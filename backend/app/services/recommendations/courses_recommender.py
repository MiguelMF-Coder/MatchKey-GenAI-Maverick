# backend/app/services/recommendations/courses_recommender.py

from pathlib import Path
import json
from typing import List, Dict, Any
from difflib import SequenceMatcher

# ----------------------------------------
# Rutas posibles del dataset
# ----------------------------------------
CANDIDATE_PATHS = [
    Path("app/services/scraping/courses_dataset.json"),
    Path("app/services/scraping/courses/data/courses.json"),
    Path("app/services/scraping/courses.json"),
]

# ----------------------------------------
# CACHE GLOBAL (RAM)
# ----------------------------------------
_COURSES_CACHE: List[Dict[str, Any]] = None


# ----------------------------------------
# Utilidades de normalización
# ----------------------------------------
def _normalize_text(text: str) -> str:
    return text.strip().lower()


def _split_skills_field(skills_field: str | None) -> List[str]:
    if not skills_field:
        return []
    parts = [s.strip() for s in skills_field.split(",") if s.strip()]
    return [_normalize_text(p) for p in parts]


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


# ----------------------------------------
# Carga + preprocesado con CACHE
# ----------------------------------------
def load_courses() -> List[Dict[str, Any]]:
    """
    Carga el dataset de cursos del scraping SOLO UNA VEZ.
    Preprocesa y normaliza skills en RAM para acelerar recomendación.
    """
    global _COURSES_CACHE

    if _COURSES_CACHE is not None:
        return _COURSES_CACHE

    # Buscar un archivo válido
    dataset_path = None
    for p in CANDIDATE_PATHS:
        if p.exists():
            dataset_path = p
            break

    if dataset_path is None:
        _COURSES_CACHE = []
        return _COURSES_CACHE

    try:
        with open(dataset_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except Exception:
        raw_data = []

    if not isinstance(raw_data, list):
        raw_data = []

    # Preprocesar: normalizar skills una sola vez
    for c in raw_data:
        sf = c.get("skills", "") or ""
        c["_skills_normalized"] = _split_skills_field(sf)

    _COURSES_CACHE = raw_data
    return _COURSES_CACHE


# ----------------------------------------
# Motor de recomendación optimizado
# ----------------------------------------
def recommend_courses_for_gaps(
    gaps: List[str],
    top_n: int = 10,
    min_similarity: float = 0.55,
) -> List[Dict[str, Any]]:
    """
    Dado un listado de gaps (skills que faltan), devuelve una lista
    de cursos recomendados ordenados por relevancia.

    Cada curso recomendado contiene:
    - title
    - provider
    - url
    - target_skills (skills para las que ayuda ese curso)
    """
    if not gaps:
        return []

    # Normalizamos gaps una sola vez
    gaps_norm = [_normalize_text(g) for g in gaps]

    courses = load_courses()
    scored: List[Dict[str, Any]] = []

    for course in courses:
        course_skills = course.get("_skills_normalized", [])

        matched_gap_skills: List[str] = []
        total_score = 0.0

        # Evaluar cada gap contra las skills normalizadas del curso
        for gap in gaps_norm:
            best_sim = 0.0

            for cskill in course_skills:
                sim = _similarity(gap, cskill)
                if sim > best_sim:
                    best_sim = sim

            # Si supera el umbral → el curso es relevante para ese gap
            if best_sim >= min_similarity:
                matched_gap_skills.append(gap)
                total_score += best_sim

        if matched_gap_skills:
            scored.append(
                {
                    "title": course.get("name", "Curso sin nombre"),
                    "provider": course.get("category", None),
                    "url": course.get("url", "#"),
                    "target_skills": matched_gap_skills,
                    "score": total_score,
                }
            )

    # Ordenar por score descendente
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Limpiar el output antes de devolverlo
    trimmed = [
        {
            "title": c["title"],
            "provider": c.get("provider"),
            "url": c["url"],
            "target_skills": c["target_skills"],
        }
        for c in scored[:top_n]
    ]

    return trimmed
