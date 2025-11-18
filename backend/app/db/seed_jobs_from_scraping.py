# backend/app/db/seed_jobs_from_scraping.py

import json
import os
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.companies import Company
from app.models.jobs import Job


# Ruta del JSON dentro del contenedor
JOBS_JSON_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "services",
    "scraping",
    "jobs",
    "data",
    "jobs_final.json",
)


def _norm_str(value: Optional[str]) -> Optional[str]:
    """Normaliza strings: quita espacios y convierte vacío a None."""
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def _to_float(value) -> Optional[float]:
    """Convierte a float si se puede, si no devuelve None."""
    if value is None:
        return None
    try:
        v = str(value).strip()
        if not v:
            return None
        return float(v)
    except Exception:
        return None


def get_or_create_company(db: Session, name: Optional[str]) -> Optional[Company]:
    """
    Devuelve una Company por nombre o la crea si no existe.
    Si el nombre es None o vacío, devuelve None (no creamos empresa fantasma).
    """
    name = _norm_str(name)
    if not name:
        return None

    existing = db.query(Company).filter(Company.name == name).first()
    if existing:
        return existing

    company = Company(
        name=name,
        industry=None,
        size=None,
        location=None,
        website=None,
        description=None,
    )
    db.add(company)
    db.flush()  # para tener company.id
    return company


def get_existing_job(db: Session, title: str, company: Company, location: Optional[str]) -> Optional[Job]:
    """
    Busca un Job por (title, company_id, location).
    Si no hay company, devuelve None directamente (no buscamos).
    """
    if company is None:
        return None

    query = db.query(Job).filter(
        Job.title == title,
        Job.company_id == company.id,
    )
    if location:
        query = query.filter(Job.location == location)

    return query.first()


def load_jobs_json() -> list:
    if not os.path.exists(JOBS_JSON_PATH):
        raise FileNotFoundError(f"No se encontró jobs_final.json en: {JOBS_JSON_PATH}")

    with open(JOBS_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("El JSON de jobs debe ser una lista de ofertas")

    return data


def seed_jobs() -> Tuple[int, int]:
    """
    Lee jobs_final.json y hace:
    - create/update de Company
    - create/update de Job
    Devuelve (nuevos, actualizados).
    """

    data = load_jobs_json()
    print(f"🔎 Cargando {len(data)} ofertas desde jobs_final.json")

    db: Session = SessionLocal()
    created = 0
    updated = 0

    try:
        for item in data:
            # --- Campos base que sabemos que existen en el JSON ---
            title = _norm_str(item.get("title_jobs") or item.get("title"))
            company_name = _norm_str(item.get("company_jobs") or item.get("company"))
            location = _norm_str(item.get("location_jobs") or item.get("location"))
            description = _norm_str(item.get("description_full") or item.get("description"))

            # Si no hay título o empresa, no podemos trabajar con esta oferta
            if not title or not company_name:
                print(f"⚠️ Saltando oferta incompleta (sin título o sin empresa): title={title} company={company_name} location={location}")
                continue

            # --- Empresa ---
            company = get_or_create_company(db, company_name)

            # Si por algún motivo no conseguimos empresa, saltamos
            if company is None:
                print(f"⚠️ Saltando oferta sin empresa válida: title={title} location={location}")
                continue

            # --- ¿Existe ya el Job? ---
            job = get_existing_job(db, title, company, location)

            is_new = False
            if job is None:
                job = Job(
                    title=title,
                    location=location,
                    company_id=company.id,  # 🔒 NUNCA None
                )
                db.add(job)
                is_new = True

            # --- Rellenamos / actualizamos campos extra ---
            job.jd_text = description
            job.category = _norm_str(item.get("category"))

            # Seniority y tipo de contrato
            job.seniority = _norm_str(item.get("seniority"))
            job.contract_time = _norm_str(item.get("contract_time"))
            job.contract_type = _norm_str(item.get("contract_type"))

            # Salario
            job.salary_min = _to_float(item.get("salary_min"))
            job.salary_max = _to_float(item.get("salary_max"))
            salary_is_pred = item.get("salary_is_predicted")
            job.salary_is_predicted = bool(salary_is_pred) if salary_is_pred is not None else False

            # Requisitos experiencia/educación
            job.experience_required = _norm_str(item.get("experience_required"))
            job.education_required = _norm_str(item.get("education_required"))

            # Tipo de puesto
            job.job_type = _norm_str(item.get("job_type"))

            # Campos JSON-ish (los dejamos tal cual vienen; el modelo los define como JSON)
            job.area = item.get("area")
            job.tech_stack = item.get("tech_stack")
            job.soft_skills = item.get("soft_skills")
            job.languages = item.get("languages")
            job.benefits = item.get("benefits")

            if is_new:
                created += 1
            else:
                updated += 1

        db.commit()
        print(f"✅ Seed/actualización completado: {created} jobs creados, {updated} actualizados.")
        return created, updated

    except Exception as e:
        db.rollback()
        print(f"❌ Error durante el seed de jobs: {repr(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_jobs()
