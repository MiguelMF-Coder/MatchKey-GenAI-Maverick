from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.users import User
from app.models.companies import Company, CompanyCulture
from app.models.jobs import Job

router = APIRouter(prefix="/companies", tags=["companies"])


# -----------------------------
# Dependencia de DB
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Pydantic Schemas
# -----------------------------
class CompanyCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class CompanyProfileUpdate(BaseModel):
    # Datos básicos
    name: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None

    # Valores y cultura
    values: Optional[List[str]] = None
    culture_description: Optional[str] = None
    leadership_style: Optional[str] = None
    work_mode: Optional[str] = None
    perks: Optional[List[str]] = None
    team_fit_summary: Optional[str] = None


class JobBasicItem(BaseModel):
    job_id: int
    title: str
    location: Optional[str]
    department: Optional[str]

    class Config:
        orm_mode = True


class CompanyProfileResponse(BaseModel):
    id: int
    user_id: int
    email: EmailStr

    # Básico
    name: Optional[str]
    industry: Optional[str]
    size: Optional[str]
    location: Optional[str]
    website: Optional[str]
    description: Optional[str]

    # Cultura
    values: List[str] = []
    culture_description: Optional[str] = None
    leadership_style: Optional[str] = None
    work_mode: Optional[str] = None
    perks: List[str] = []
    team_fit_summary: Optional[str] = None

    # Vacantes asociadas
    jobs: List[JobBasicItem] = []

    class Config:
        orm_mode = True


# -------------------------------------------------
# 1) POST /companies/create
#    Crea user + company (si no existen)
# -------------------------------------------------
@router.post("/create", response_model=CompanyProfileResponse)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):

    # Buscar usuario por email
    user = db.query(User).filter(User.email == payload.email).first()

    if user is None:
        user = User(
            email=payload.email,
            role="company",
        )
        db.add(user)
        db.flush()  # obtener id

    # Buscar o crear empresa
    company = db.query(Company).filter(Company.user_id == user.id).first()
    if company is None:
        company = Company(
            user_id=user.id,
            name=payload.name,
        )
        db.add(company)
        db.flush()

    # Crear cultura si no existe
    culture = (
        db.query(CompanyCulture)
        .filter(CompanyCulture.company_id == company.id)
        .first()
    )

    if culture is None:
        culture = CompanyCulture(
            company_id=company.id,
            values=[],
            perks=[],
        )
        db.add(culture)

    db.commit()
    db.refresh(company)
    db.refresh(user)
    db.refresh(culture)

    return CompanyProfileResponse(
        id=company.id,
        user_id=user.id,
        email=user.email,
        name=company.name,
        industry=company.industry,
        size=company.size,
        location=company.location,
        website=company.website,
        description=company.description,
        values=culture.values or [],
        culture_description=culture.culture_description,
        leadership_style=culture.leadership_style,
        work_mode=culture.work_mode,
        perks=culture.perks or [],
        team_fit_summary=culture.team_fit_summary,
        jobs=[],
    )


# -------------------------------------------------
# 2) GET /companies/{id}/profile
# -------------------------------------------------
@router.get("/{company_id}/profile", response_model=CompanyProfileResponse)
def get_company_profile(company_id: int, db: Session = Depends(get_db)):

    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    user = db.query(User).filter(User.id == company.user_id).first()

    culture = (
        db.query(CompanyCulture)
        .filter(CompanyCulture.company_id == company.id)
        .first()
    )

    jobs = (
        db.query(Job)
        .filter(Job.company_id == company.id)
        .all()
    )

    job_items = [
        JobBasicItem(
            job_id=j.id,
            title=j.title,
            location=j.location,
            department=j.department,
        )
        for j in jobs
    ]

    return CompanyProfileResponse(
        id=company.id,
        user_id=user.id,
        email=user.email,
        name=company.name,
        industry=company.industry,
        size=company.size,
        location=company.location,
        website=company.website,
        description=company.description,
        values=culture.values if culture else [],
        culture_description=culture.culture_description if culture else None,
        leadership_style=culture.leadership_style if culture else None,
        work_mode=culture.work_mode if culture else None,
        perks=culture.perks if culture else [],
        team_fit_summary=culture.team_fit_summary if culture else None,
        jobs=job_items,
    )


# -------------------------------------------------
# 3) PUT /companies/{id}/profile
# -------------------------------------------------
@router.put("/{company_id}/profile", response_model=CompanyProfileResponse)
def update_company_profile(
    company_id: int,
    payload: CompanyProfileUpdate,
    db: Session = Depends(get_db),
):

    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    culture = (
        db.query(CompanyCulture)
        .filter(CompanyCulture.company_id == company.id)
        .first()
    )
    if culture is None:
        culture = CompanyCulture(company_id=company.id, values=[], perks=[])
        db.add(culture)
        db.flush()

    # Actualizar campos básicos
    for field, value in payload.dict(exclude_unset=True).items():
        if field in [
            "name", "industry", "size", "location",
            "website", "description"
        ]:
            setattr(company, field, value)

    # Actualizar cultura/valores
    culture_fields = [
        "values", "culture_description", "leadership_style",
        "work_mode", "perks", "team_fit_summary",
    ]

    for field in culture_fields:
        if field in payload.dict(exclude_unset=True):
            setattr(culture, field, payload.dict()[field])

    db.add(company)
    db.add(culture)
    db.commit()
    db.refresh(company)
    db.refresh(culture)

    # Traemos sus vacantes
    jobs = db.query(Job).filter(Job.company_id == company.id).all()
    job_items = [
        JobBasicItem(
            job_id=j.id,
            title=j.title,
            location=j.location,
            department=j.department,
        )
        for j in jobs
    ]

    return CompanyProfileResponse(
        id=company.id,
        user_id=company.user_id,
        email=db.query(User).filter(User.id == company.user_id).first().email,
        name=company.name,
        industry=company.industry,
        size=company.size,
        location=company.location,
        website=company.website,
        description=company.description,
        values=culture.values or [],
        culture_description=culture.culture_description,
        leadership_style=culture.leadership_style,
        work_mode=culture.work_mode,
        perks=culture.perks or [],
        team_fit_summary=culture.team_fit_summary,
        jobs=job_items,
    )
