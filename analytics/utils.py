"""
analytics/utils.py — Helpers compartidos de la capa analítica del TFG.

Reglas (ver CLAUDE.md):
- Capa OFFLINE: NO importa nada de backend/ ni frontend/.
- Reproducible y trazable: rutas resueltas de forma robusta desde la raíz del repo.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


# --------------------------------------------------------------------------
# Rutas del repositorio
# --------------------------------------------------------------------------
# Este archivo vive en <repo>/analytics/utils.py → la raíz es el padre de analytics/
REPO_ROOT = Path(__file__).resolve().parents[1]

# Fuentes de datos de PRODUCCIÓN (la fuente de verdad son los JSON del scraping/OCR,
# NO la base de datos: las 236 vacantes se seedean directo desde jobs_final.json y
# nunca rellenan la tabla job_skills).
SRC = {
    "jobs": REPO_ROOT / "backend/app/services/scraping/jobs/data/jobs_final.json",
    "companies": REPO_ROOT / "backend/app/services/scraping/companies/data/companies_final.json",
    "courses": REPO_ROOT / "backend/app/services/scraping/courses/data/courses.json",
    "cv_ocr": REPO_ROOT / "backend/app/services/ocr/data/cv_ocr_analizados_100.json",
    "users_ocr": REPO_ROOT / "backend/app/services/ocr/data/usuarios_web_100_from_ocr.json",
    "skills_dictionary": REPO_ROOT / "backend/app/services/skills/skills_dictionary.json",
}

# Carpetas de salida de la capa analítica
DATA_DIR = REPO_ROOT / "data"
MATCHKEY_DIR = DATA_DIR / "matchkey"   # exports planos de producción
ESCO_DIR = DATA_DIR / "esco"           # datos ESCO + mapeos
CLEAN_DIR = DATA_DIR / "clean"         # datasets limpios post-ingeniería del dato
FIGURES_DIR = REPO_ROOT / "notebooks" / "figures"  # PNGs para la memoria


# --------------------------------------------------------------------------
# I/O
# --------------------------------------------------------------------------
def load_json(path: str | Path) -> Any:
    """Carga un JSON en UTF-8."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_dir(path: str | Path) -> Path:
    """Crea el directorio (y padres) si no existe. Devuelve el Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_csv(df, path: str | Path) -> Path:
    """
    Guarda un DataFrame como CSV con encoding utf-8-sig (compatible con Excel,
    importante porque el alumno revisará los CSV a mano para el TFG).
    """
    path = Path(path)
    ensure_dir(path.parent)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


# --------------------------------------------------------------------------
# Normalización de campos
# --------------------------------------------------------------------------
def parse_pylist(value: Any) -> list:
    """
    Algunos campos del scraping (p.ej. `area`) vienen como STRING que representa
    una lista Python: "['España', 'Navarra', 'Pamplona']".
    Esta función lo convierte a lista real de forma segura.
    - Si ya es lista, la devuelve tal cual.
    - Si es None/"" o no parseable, devuelve [].
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return []
        try:
            parsed = ast.literal_eval(s)
            if isinstance(parsed, list):
                return parsed
            return [parsed]
        except (ValueError, SyntaxError):
            return [s]
    return [value]


def as_list(value: Any) -> list:
    """Normaliza a lista: None→[], escalar→[escalar], lista→lista (sin Nones/vacíos)."""
    if value is None:
        return []
    items = value if isinstance(value, list) else [value]
    out = []
    for x in items:
        if x is None:
            continue
        if isinstance(x, str) and not x.strip():
            continue
        out.append(x)
    return out


def to_int_or_none(value: Any):
    """Convierte a int si se puede; si no, None. Tolera '', '3 años', '3.0'."""
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int,)):
        return value
    if isinstance(value, float):
        return int(value)
    s = str(value).strip()
    if not s:
        return None
    # extraer primer entero que aparezca (p.ej. "mínimo 3 años" → 3)
    import re
    m = re.search(r"-?\d+", s.replace(",", "."))
    return int(m.group(0)) if m else None


def to_float_or_none(value: Any):
    """Convierte a float si se puede; si no, None."""
    if value is None:
        return None
    try:
        s = str(value).strip()
        return float(s) if s else None
    except (ValueError, TypeError):
        return None


def normalize_skill(s: Any) -> str:
    """Normaliza una skill para comparaciones: strip + lower (sin tocar acentos)."""
    return str(s).strip().lower() if s is not None else ""
