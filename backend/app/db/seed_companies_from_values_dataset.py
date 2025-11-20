# backend/app/db/seed_companies_from_values_dataset.py

import json
from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.companies import Company, CompanyCulture


# Cambia esta ruta según la ubicación REAL del archivo
VALUES_JSON = Path(
    "app/services/scraping/companies/data/companies_final.json"
)


def load_values_dataset(path: Path) -> List[dict]:
    if not path.exists():
        raise FileNotFoundError(f"No se encuentra {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_or_create_company(db: Session, name: str, url: Optional[str]) -> Company:
    company = (
        db.query(Company)
        .filter(Company.name.ilike(name))
        .first()
    )
    if company:
        if url and not company.website:
            company.website = url
        return company

    company = Company(name=name, website=url)
    db.add(company)
    db.flush()
    return company


def upsert_company_culture(
    db: Session,
    company: Company,
    values_list: Optional[List[str]],
    culture_summary: Optional[str]
):
    culture = (
        db.query(CompanyCulture)
        .filter(CompanyCulture.company_id == company.id)
        .first()
    )

    values_text = json.dumps(values_list, ensure_ascii=False) if values_list else None

    if culture:
        if values_text:
            culture.values = values_text
        if culture_summary:
            culture.culture_description = culture_summary
        if culture.work_mode is None:
            culture.work_mode = "unspecified"
        return culture

    culture = CompanyCulture(
        company_id=company.id,
        values=values_text,
        culture_description=culture_summary,
        leadership_style=None,
        work_mode="unspecified",
        perks=None,
        team_fit_summary=None
    )
    db.add(culture)
    return culture


def seed_companies_from_values_dataset():
    data = load_values_dataset(VALUES_JSON)
    db = SessionLocal()

    try:
        for item in data:
            name = (item.get("company") or "").strip()
            if not name:
                continue

            url = item.get("url_about_us")
            values_list = item.get("values")
            summary = item.get("culture_summary")

            company = get_or_create_company(db, name, url)
            upsert_company_culture(db, company, values_list, summary)

        db.commit()
        print("✅ Seed de empresas/cultura completado")
    except Exception as e:
        db.rollback()
        print(f"❌ Error en seed companies: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_companies_from_values_dataset()
