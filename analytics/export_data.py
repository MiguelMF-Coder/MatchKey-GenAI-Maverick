"""
analytics/export_data.py — Export de datos de PRODUCCIÓN a CSVs planos.

Objetivo (Fase 1 del TFG): tener los datos de MatchKey en CSV plano, auditables y
reproducibles, como base para la ingeniería del dato y los modelos.

FUENTE DE VERDAD = los JSON del scraping/OCR (NO la base de datos), porque:
  - Las 236 vacantes se seedean directo desde jobs_final.json y NUNCA rellenan la
    tabla job_skills (esa tabla solo se llena con skills dummy cuando una empresa
    crea un job por la web). Las skills reales de cada vacante viven en los arrays
    del JSON: skills_must / skills_nice / tech_stack / soft_skills / languages.
  - candidate_skills SÍ es real y proviene del OCR de CVs (cv_ocr_analizados_100.json).

IDs estables asignados aquí (documentado para trazabilidad):
  - job_id      = índice de fila en jobs_final.json (0..235); clave natural: redirect_url
  - company_id  = índice de fila en companies_final.json (0..81); clave natural: company
  - candidate_id= campo 'candidate_id' del OCR (1..100)
  - course_id   = índice de fila en courses.json

Uso:
    .venv\\Scripts\\python.exe analytics\\export_data.py

Salidas en data/matchkey/:
    candidates.csv, candidate_skills.csv, candidate_education.csv,
    candidate_languages.csv, vacantes.csv, job_skills.csv,
    courses.csv, companies.csv, _export_summary.csv
"""

from __future__ import annotations

import pandas as pd

from utils import (
    SRC,
    MATCHKEY_DIR,
    load_json,
    save_csv,
    parse_pylist,
    as_list,
    to_int_or_none,
    to_float_or_none,
)


# --------------------------------------------------------------------------
# 1) CANDIDATOS (desde el OCR de CVs)
# --------------------------------------------------------------------------
def export_candidates() -> dict[str, pd.DataFrame]:
    cvs = load_json(SRC["cv_ocr"])

    cand_rows, skill_rows, edu_rows, lang_rows = [], [], [], []

    for cv in cvs:
        cid = cv.get("candidate_id")

        skills = cv.get("skills", {}) or {}
        tech = as_list(skills.get("technical"))
        soft = as_list(skills.get("soft"))
        education = cv.get("education", []) or []
        languages = cv.get("languages", []) or []

        cand_rows.append({
            "candidate_id": cid,
            "name": cv.get("name"),
            "email": cv.get("email"),
            "phone": cv.get("phone"),
            "location": cv.get("location"),
            "years_experience": to_int_or_none(cv.get("years_experience")),
            "current_role": cv.get("current_role"),
            "desired_role": cv.get("desired_role"),
            "n_skills_technical": len(tech),
            "n_skills_soft": len(soft),
            "n_education": len(education),
            "n_languages": len(languages),
        })

        # candidate_skills (formato largo) — fuente REAL de skills de candidato
        for s in tech:
            skill_rows.append({"candidate_id": cid, "skill": s, "skill_type": "technical"})
        for s in soft:
            skill_rows.append({"candidate_id": cid, "skill": s, "skill_type": "soft"})

        for e in education:
            edu_rows.append({
                "candidate_id": cid,
                "degree": e.get("degree"),
                "university": e.get("university"),
                "start_year": to_int_or_none(e.get("start_year")),
                "end_year": to_int_or_none(e.get("end_year")),
            })

        for lg in languages:
            lang_rows.append({
                "candidate_id": cid,
                "language": lg.get("language"),
                "level": lg.get("level"),
            })

    return {
        "candidates": pd.DataFrame(cand_rows),
        "candidate_skills": pd.DataFrame(skill_rows),
        "candidate_education": pd.DataFrame(edu_rows),
        "candidate_languages": pd.DataFrame(lang_rows),
    }


# --------------------------------------------------------------------------
# 2) VACANTES (desde jobs_final.json)
# --------------------------------------------------------------------------
def export_jobs() -> dict[str, pd.DataFrame]:
    jobs = load_json(SRC["jobs"])

    job_rows, jobskill_rows = [], []

    # Mapeo importancia → campo del JSON. category 'must'/'nice' son la clasificación
    # LLM (silver-standard); tech/soft/language/benefit son listas auxiliares del LLM.
    list_fields = {
        "must": "skills_must",
        "nice": "skills_nice",
        "tech": "tech_stack",
        "soft": "soft_skill",  # placeholder, se sobreescribe abajo
    }

    for jid, job in enumerate(jobs):
        area_list = parse_pylist(job.get("area"))

        skills_must = as_list(job.get("skills_must"))
        skills_nice = as_list(job.get("skills_nice"))
        tech_stack = as_list(job.get("tech_stack"))
        soft_skills = as_list(job.get("soft_skills"))
        languages = as_list(job.get("languages"))
        benefits = as_list(job.get("benefits"))

        job_rows.append({
            "job_id": jid,
            "title": job.get("title"),
            "company": job.get("company"),
            "location": job.get("location"),
            "area": " > ".join(str(a) for a in area_list),  # jerarquía geográfica legible
            "category_jobs": job.get("category_jobs"),       # Adzuna (70% 'Unknown')
            "category_llm": job.get("category_llm"),         # SILVER-STANDARD (target Modelo 3)
            "contract_type": job.get("contract_type"),
            "contract_time": job.get("contract_time"),
            "job_type": job.get("job_type"),
            "seniority": job.get("seniority"),
            "salary_min": to_float_or_none(job.get("salary_min")),
            "salary_max": to_float_or_none(job.get("salary_max")),
            "salary_is_predicted": job.get("salary_is_predicted"),
            "experience_required": job.get("experience_required"),
            "experience_required_num": to_int_or_none(job.get("experience_required")),
            "education_required": job.get("education_required"),
            "n_skills_must": len(skills_must),
            "n_skills_nice": len(skills_nice),
            "n_tech_stack": len(tech_stack),
            "n_soft_skills": len(soft_skills),
            "n_languages": len(languages),
            "n_benefits": len(benefits),
            "description_full": job.get("description_full"),
            "redirect_url": job.get("redirect_url"),
        })

        # job_skills (formato largo) — fuente REAL de skills de vacante
        for s in skills_must:
            jobskill_rows.append({"job_id": jid, "skill": s, "importance": "must"})
        for s in skills_nice:
            jobskill_rows.append({"job_id": jid, "skill": s, "importance": "nice"})
        for s in tech_stack:
            jobskill_rows.append({"job_id": jid, "skill": s, "importance": "tech_stack"})
        for s in soft_skills:
            jobskill_rows.append({"job_id": jid, "skill": s, "importance": "soft_skill"})
        for s in languages:
            jobskill_rows.append({"job_id": jid, "skill": s, "importance": "language"})
        for s in benefits:
            jobskill_rows.append({"job_id": jid, "skill": s, "importance": "benefit"})

    return {
        "vacantes": pd.DataFrame(job_rows),
        "job_skills": pd.DataFrame(jobskill_rows),
    }


# --------------------------------------------------------------------------
# 3) CURSOS (desde courses.json) — se omite el campo 'content' (pesado, ~11MB)
# --------------------------------------------------------------------------
def export_courses() -> pd.DataFrame:
    courses = load_json(SRC["courses"])
    rows = []
    for cidx, c in enumerate(courses):
        content = c.get("content") or ""
        rows.append({
            "course_id": cidx,
            "name": c.get("name"),
            "category": c.get("category"),
            "language": c.get("language"),
            "skills": c.get("skills"),  # string CSV de skills (tal cual el catálogo)
            "what_you_learn": c.get("what_you_learn"),
            "url": c.get("url"),
            "content_length": len(content),  # se guarda longitud, no el texto completo
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# 4) EMPRESAS (desde companies_final.json) — se omite 'clean_text' (pesado)
# --------------------------------------------------------------------------
def export_companies() -> pd.DataFrame:
    companies = load_json(SRC["companies"])
    rows = []
    for coid, comp in enumerate(companies):
        values = as_list(comp.get("values"))
        clean_text = comp.get("clean_text") or ""
        rows.append({
            "company_id": coid,
            "company": comp.get("company"),
            "url_about_us": comp.get("url_about_us"),
            "n_values": len(values),
            "values": " | ".join(str(v) for v in values),
            "culture_summary": comp.get("culture_summary"),
            "clean_text_length": len(clean_text),
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# Orquestación
# --------------------------------------------------------------------------
def main() -> None:
    tables: dict[str, pd.DataFrame] = {}
    tables.update(export_candidates())
    tables.update(export_jobs())
    tables["courses"] = export_courses()
    tables["companies"] = export_companies()

    summary_rows = []
    for name, df in tables.items():
        path = save_csv(df, MATCHKEY_DIR / f"{name}.csv")
        summary_rows.append({"tabla": name, "filas": len(df), "columnas": df.shape[1], "archivo": path.name})
        print(f"  [OK] {name:22s} {len(df):6d} filas x {df.shape[1]:2d} cols  -> {path}")

    summary = pd.DataFrame(summary_rows)
    save_csv(summary, MATCHKEY_DIR / "_export_summary.csv")

    print("\nResumen del export:")
    print(summary.to_string(index=False))
    print(f"\nTodo en: {MATCHKEY_DIR}")


if __name__ == "__main__":
    main()
