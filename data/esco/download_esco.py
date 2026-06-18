"""
data/esco/download_esco.py — Cosecha de la taxonomía ESCO vía API oficial.

Genera (en esta misma carpeta):
    skills_en.csv        ~13.485 competencias  (uri, preferredLabel, altLabels, description, skillType?, status)
    occupations_en.csv   ~2.942 ocupaciones    (uri, preferredLabel, altLabels, description, isco_code, status)
    _esco_meta.json      metadatos de la cosecha (fecha, conteos, endpoint)

Fuente: ESCO API — Comisión Europea (https://ec.europa.eu/esco/api).
  - Endpoint /search paginado por `type` (skill | occupation), `language=en`, `full=true`.
  - La API sirve la última versión publicada de ESCO (ver _esco_meta.json tras ejecutar).

Por qué la API y no el bundle CSV del portal:
  - Reproducible desde el repo sin pasos manuales ni tokens de sesión.
  - `full=true` incluye alternativeLabel (altLabels) y description, que mejoran el
    recall del mapeo MatchKey -> ESCO.

Uso (con el venv del proyecto):
    .venv\\Scripts\\python.exe data\\esco\\download_esco.py

Nota: ~165 peticiones HTTP, varios minutos. Es idempotente: re-ejecutar regenera los CSV.
"""

from __future__ import annotations

import csv
import json
import ssl
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

# Evita UnicodeEncodeError en consolas Windows (cp1252) al imprimir progreso.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

API = "https://ec.europa.eu/esco/api/search"
LANG = "en"
LIMIT = 100
OUT_DIR = Path(__file__).resolve().parent
CTX = ssl.create_default_context()


def _get(url: str, retries: int = 6) -> dict:
    """GET con reintentos y backoff (la API de ESCO da 500 transitorios)."""
    waits = [3, 6, 12, 25, 40, 40]
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            last_err = e
            wait = waits[min(attempt, len(waits) - 1)]
            print(f"    [retry {attempt + 1}/{retries}] {type(e).__name__}: {e} -> espero {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"Fallo tras {retries} intentos: {last_err}")


def _results(payload: dict) -> list:
    return payload.get("_embedded", {}).get("results") or payload.get("results") or []


def _en_label(concept: dict) -> str:
    """Label en inglés: usa `title` (ya localizado por language=en); fallback a preferredLabel."""
    title = concept.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    pref = concept.get("preferredLabel") or {}
    if isinstance(pref, str):
        return pref.strip()
    return (pref.get("en") or pref.get("en-us") or "").strip()


def _en_alt_labels(concept: dict) -> str:
    alt = concept.get("alternativeLabel") or {}
    if isinstance(alt, dict):
        labels = alt.get("en") or alt.get("en-us") or []
    elif isinstance(alt, list):
        labels = alt
    else:
        labels = []
    return " | ".join(str(x).strip() for x in labels if str(x).strip())


def _en_description(concept: dict) -> str:
    desc = concept.get("description") or {}
    if not isinstance(desc, dict):
        return str(desc) if desc else ""
    node = desc.get("en") or desc.get("en-us") or {}
    if isinstance(node, dict):
        return (node.get("literal") or "").strip()
    return str(node).strip()


def _row_from_concept(c: dict, concept_type: str) -> dict:
    row = {
        "concept_uri": c.get("uri"),
        "preferred_label": _en_label(c),
        "alt_labels": _en_alt_labels(c),
        "description": _en_description(c),
        "status": c.get("status"),
    }
    if concept_type == "occupation":
        row["isco_code"] = c.get("code")
    return row


def _page_url(concept_type: str, page: int) -> str:
    # full=false: respuesta mínima (~200 KB/pág) y MUCHO más fiable. full=true (~1.4 MB/pág,
    # todos los idiomas) provoca HTTP 500 del servidor de ESCO bajo ráfaga. Sin altLabels;
    # el mapeo lo compensa con inclusión de tokens + fuzzy TF-IDF (ver analytics/esco_mapper.py).
    return f"{API}?language={LANG}&type={concept_type}&limit={LIMIT}&offset={page}&full=false"


def harvest(concept_type: str) -> list[dict]:
    """
    Pagina /search por tipo y devuelve filas normalizadas.

    OJO: en la API de ESCO el parámetro `offset` es el NÚMERO DE PÁGINA (no de registro):
    el `next` de offset=0 apunta a offset=1.

    Robustez: iteración determinista por nº de página usando `total` (no dependemos de la
    página vacía como señal de fin), y si una página falla definitivamente se registra y se
    reintenta al final, en vez de abortar toda la cosecha.
    """
    import math

    first = _get(_page_url(concept_type, 0))
    total = first.get("total", 0)
    max_page = math.ceil(total / LIMIT) if total else 0
    print(f"  {concept_type}: total={total} ({max_page} páginas)")

    rows: list[dict] = [_row_from_concept(c, concept_type) for c in _results(first)]
    failed: list[int] = []

    for page in range(1, max_page):
        try:
            payload = _get(_page_url(concept_type, page))
            rows.extend(_row_from_concept(c, concept_type) for c in _results(payload))
        except Exception as e:  # noqa: BLE001
            print(f"  [WARN] página {page} falló: {e} -> se reintentará al final")
            failed.append(page)
        if page % 10 == 0:
            print(f"    {concept_type} ~{len(rows)}/{total} (page {page}/{max_page}) ...")
        time.sleep(0.2)  # cortesía con la API

    # Segunda pasada para páginas fallidas
    if failed:
        print(f"  {concept_type}: reintentando {len(failed)} páginas fallidas: {failed}")
        still_failed = []
        for page in failed:
            try:
                payload = _get(_page_url(concept_type, page))
                rows.extend(_row_from_concept(c, concept_type) for c in _results(payload))
            except Exception as e:  # noqa: BLE001
                still_failed.append(page)
                print(f"  [WARN] página {page} no recuperada: {e}")
        if still_failed:
            print(f"  [WARN] {concept_type}: páginas perdidas {still_failed} "
                  f"(~{len(still_failed) * LIMIT} conceptos no cosechados)")

    print(f"  {concept_type}: cosechadas {len(rows)}/{total} filas")
    return rows


def write_csv(rows: list[dict], fieldnames: list[str], path: Path) -> None:
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})
    print(f"  [OK] {path.name}: {len(rows)} filas -> {path}")


def main() -> None:
    print("Cosechando ESCO desde la API oficial...")
    skills = harvest("skill")
    write_csv(
        skills,
        ["concept_uri", "preferred_label", "alt_labels", "description", "status"],
        OUT_DIR / "skills_en.csv",
    )

    occupations = harvest("occupation")
    write_csv(
        occupations,
        ["concept_uri", "preferred_label", "alt_labels", "description", "isco_code", "status"],
        OUT_DIR / "occupations_en.csv",
    )

    meta = {
        "harvested_on": date.today().isoformat(),
        "source": "ESCO API (https://ec.europa.eu/esco/api/search)",
        "language": LANG,
        "method": "search endpoint, full=false, limit=100, paginado por offset (offset=nº de página)",
        "note": "La API sirve la ultima version publicada de ESCO.",
        "n_skills": len(skills),
        "n_occupations": len(occupations),
    }
    (OUT_DIR / "_esco_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nCosecha completada.")
    print(json.dumps(meta, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
