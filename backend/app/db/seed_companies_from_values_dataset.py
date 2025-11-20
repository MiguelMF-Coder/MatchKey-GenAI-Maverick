# backend/app/db/seed_companies_from_values_dataset.py

import json
from pathlib import Path
from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.companies import Company, CompanyCulture


# Ruta al JSON generado por companies_values_scraper.py
VALUES_JSON = (
    Path(__file__)
    .resolve()
    .parent.parent  # backend/app
    / "services"
    / "scraping"
    / "values_dataset.json"
)


def load_values_dataset(path: Path) -> List[dict]:
    if not path.exists():
        raise FileNotFoundError(f"No se encuentra {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_or_create_company(db: Session, name: str, url: Optional[str]) -> Company:
    """
    Busca una Company por nombre (case insensitive).
    Si no existe, la crea.
    """
    company = (
        db.query(Company)
        .filter(Company.name.ilike(name))  # type: ignore[attr-defined]
        .first()
    )
    if company:
        # si no tiene web y ahora sí, actualizamos
        if url and not company.website:
            company.website = url
        return company

    company = Company(
        name=name,
        website=url,
        # otros campos opcionales (industry, size, location, description)
        # quedan a None por ahora
    )
    db.add(company)
    db.flush()  # para tener company.id
    return company


def build_culture_description(
    mission: Optional[str],
    vision: Optional[str],
    culture_summary: Optional[str],
) -> Optional[str]:
    """
    Combina mission, vision y culture_summary en un único texto.
    """
    parts: List[str] = []
    if mission:
        parts.append(f"Mission: {mission}")
    if vision:
        parts.append(f"Vision: {vision}")
    if culture_summary:
        parts.append(f"Culture: {culture_summary}")

    if not parts:
        return None
    return "\n\n".join(parts)


def upsert_company_culture(
    db: Session,
    company: Company,
    mission: Optional[str],
    vision: Optional[str],
    values_list: Optional[List[str]],
    culture_summary: Optional[str],
) -> CompanyCulture:
    """
    Crea o actualiza la fila de CompanyCulture para esa empresa.
    """
    culture = (
        db.query(CompanyCulture)
        .filter(CompanyCulture.company_id == company.id)  # type: ignore[attr-defined]
        .first()
    )

    # values se guarda como JSON string
    values_text: Optional[str] = None
    if values_list:
        try:
            values_text = json.dumps(values_list, ensure_ascii=False)
        except Exception:
            # fallback por si viene algo raro
            values_text = ", ".join(str(v) for v in values_list)

    culture_description = build_culture_description(mission, vision, culture_summary)

    if culture:
        if values_text:
            culture.values = values_text
        if culture_description:
            culture.culture_description = culture_description
        # De momento no inferimos estos campos, los dejamos como están
        if culture.work_mode is None:
            culture.work_mode = "unspecified"
        return culture

    culture = CompanyCulture(
        company_id=company.id,
        values=values_text,
        culture_description=culture_description,
        leadership_style=None,
        work_mode="unspecified",
        perks=None,
        team_fit_summary=None,
    )
    db.add(culture)
    return culture


def seed_companies_from_values_dataset() -> None:
    data = load_values_dataset(VALUES_JSON)
    db = SessionLocal()

    try:
        for item in data:
            name = (item.get("company") or "").strip()
            if not name:
                continue

            url = item.get("url")
            mission = item.get("mission")
            vision = item.get("vision")
            values_list = item.get("values")
            culture_summary = item.get("culture_summary")

            company = get_or_create_company(db, name, url)
            upsert_company_culture(
                db,
                company,
                mission=mission,
                vision=vision,
                values_list=values_list,
                culture_summary=culture_summary,
            )

        db.commit()
        print("✅ Seed de empresas/cultura completado")
    except Exception as e:
        db.rollback()
        print(f"❌ Error en el seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_companies_from_values_dataset()
