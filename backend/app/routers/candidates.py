from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.users import User
from app.models.candidates import Candidate
from app.models.skills import CandidateSkill
from app.models.jobs import Job
from app.models.interviews import CandidateInterview

router = APIRouter(prefix="/candidates", tags=["candidates"])


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
# Esquemas Pydantic
# -----------------------------
class CandidateCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class CandidateProfileUpdate(BaseModel):
    name: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    years_experience: Optional[int] = None


class CandidateProfileResponse(BaseModel):
    id: int
    user_id: int
    email: EmailStr
    name: Optional[str]
    headline: Optional[str]
    location: Optional[str]
    summary: Optional[str]
    years_experience: Optional[int] = None
    num_skills: int
    has_hr_interview: bool

    class Config:
        orm_mode = True


class SkillItem(BaseModel):
    skill_name: str
    level: Optional[str] = None
    source: Optional[str] = None


class CVParseResult(BaseModel):
    candidate_id: int
    all_skills: List[str]
    must_have: List[str]
    nice_to_have: List[str]
    raw_text: Optional[str] = None
    clean_text: Optional[str] = None


class RecommendedJobScores(BaseModel):
    global_score: float
    skills_match: float
    values_match: float
    team_fit: float


class RecommendedJobItem(BaseModel):
    job_id: int
    title: str
    company_name: Optional[str] = None
    location: Optional[str] = None

    # Datos extendidos del Job
    description: Optional[str] = None
    category: Optional[str] = None
    contract_type: Optional[str] = None
    contract_time: Optional[str] = None
    job_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    experience_required: Optional[str] = None
    education_required: Optional[str] = None
    area: Optional[Any] = None  # puede ser lista/JSON
    tech_stack: Optional[List[str]] = None
    soft_skills: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    benefits: Optional[List[str]] = None

    scores: RecommendedJobScores


class RecommendedJobsResponse(BaseModel):
    jobs: List[RecommendedJobItem]


class GapsSkillsSection(BaseModel):
    strong: List[str] = []
    medium: List[str] = []
    missing: List[str] = []


class CourseRecommendation(BaseModel):
    title: str
    provider: Optional[str] = None
    url: Optional[str] = None
    target_skills: List[str] = []


class GapsRecommendations(BaseModel):
    courses: List[CourseRecommendation] = []
    actions: List[str] = []


class GapsResponse(BaseModel):
    candidate_id: int
    job_id: int
    scores: RecommendedJobScores
    skills: GapsSkillsSection
    recommendations: GapsRecommendations


# -------------------------------------------------
# 1) POST /candidates/create
#    Crea user + candidate (si no existen) o los reutiliza
# -------------------------------------------------
@router.post("/create", response_model=CandidateProfileResponse)
def create_candidate(payload: CandidateCreate, db: Session = Depends(get_db)):
    # ¿Existe ya el usuario?
    user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if user is None:
        user = User(
            email=payload.email,
            role="candidate",  # IMPORTANTE: rol candidate
        )
        db.add(user)
        db.flush()  # para obtener user.id

    # ¿Existe ya el candidate?
    candidate = (
        db.query(Candidate)
        .filter(Candidate.user_id == user.id)
        .first()
    )

    if candidate is None:
        candidate = Candidate(
            user_id=user.id,
            name=payload.name,
        )
        db.add(candidate)
        db.flush()

    db.commit()
    db.refresh(candidate)
    db.refresh(user)

    # Contar skills e IA
    num_skills = (
        db.query(CandidateSkill)
        .filter(CandidateSkill.candidate_id == candidate.id)
        .count()
    )
    has_hr_interview = (
        db.query(CandidateInterview)
        .filter(CandidateInterview.candidate_id == candidate.id)
        .first()
        is not None
    )

    return CandidateProfileResponse(
        id=candidate.id,
        user_id=user.id,
        email=user.email,
        name=candidate.name,
        headline=getattr(candidate, "headline", None),
        location=getattr(candidate, "location", None),
        summary=getattr(candidate, "summary", None),
        years_experience=getattr(candidate, "years_experience", None),
        num_skills=num_skills,
        has_hr_interview=has_hr_interview,
    )


# -------------------------------------------------
# 2) GET /candidates/{id}/profile
# -------------------------------------------------
@router.get("/{candidate_id}/profile", response_model=CandidateProfileResponse)
def get_candidate_profile(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    user = db.query(User).filter(User.id == candidate.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found for candidate")

    num_skills = (
        db.query(CandidateSkill)
        .filter(CandidateSkill.candidate_id == candidate.id)
        .count()
    )
    has_hr_interview = (
        db.query(CandidateInterview)
        .filter(CandidateInterview.candidate_id == candidate.id)
        .first()
        is not None
    )

    return CandidateProfileResponse(
        id=candidate.id,
        user_id=user.id,
        email=user.email,
        name=candidate.name,
        headline=getattr(candidate, "headline", None),
        location=getattr(candidate, "location", None),
        summary=getattr(candidate, "summary", None),
        years_experience=getattr(candidate, "years_experience", None),
        num_skills=num_skills,
        has_hr_interview=has_hr_interview,
    )


# -------------------------------------------------
# 3) PUT /candidates/{id}/profile
# -------------------------------------------------
@router.put("/{candidate_id}/profile", response_model=CandidateProfileResponse)
def update_candidate_profile(
    candidate_id: int,
    payload: CandidateProfileUpdate,
    db: Session = Depends(get_db),
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Actualizamos solo campos enviados
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(candidate, field, value)

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    user = db.query(User).filter(User.id == candidate.user_id).first()

    num_skills = (
        db.query(CandidateSkill)
        .filter(CandidateSkill.candidate_id == candidate.id)
        .count()
    )
    has_hr_interview = (
        db.query(CandidateInterview)
        .filter(CandidateInterview.candidate_id == candidate.id)
        .first()
        is not None
    )

    return CandidateProfileResponse(
        id=candidate.id,
        user_id=user.id,
        email=user.email,
        name=candidate.name,
        headline=getattr(candidate, "headline", None),
        location=getattr(candidate, "location", None),
        summary=getattr(candidate, "summary", None),
        years_experience=getattr(candidate, "years_experience", None),
        num_skills=num_skills,
        has_hr_interview=has_hr_interview,
    )


# -------------------------------------------------
# 4) POST /candidates/{id}/profile?parse_cv=true
#    Placeholder listo para integrar Document Parser + Skills Extractor
# -------------------------------------------------
@router.post("/{candidate_id}/profile", response_model=CVParseResult)
async def upload_and_parse_cv(
    candidate_id: int,
    parse_cv: bool = Query(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if not parse_cv:
        raise HTTPException(
            status_code=400,
            detail="Set parse_cv=true to trigger CV parsing",
        )

    content_bytes = await file.read()
    raw_text = f"Archivo recibido: {file.filename} ({len(content_bytes)} bytes)"

    all_skills: List[str] = []
    must_have: List[str] = []
    nice_to_have: List[str] = []

    db.query(CandidateSkill).filter(CandidateSkill.candidate_id == candidate.id).delete()

    for skill_name in all_skills:
        skill = CandidateSkill(
            candidate_id=candidate.id,
            skill_name=skill_name,
            level="unknown",
            source="cv_parser",
        )
        db.add(skill)

    db.commit()

    return CVParseResult(
        candidate_id=candidate.id,
        all_skills=all_skills,
        must_have=must_have,
        nice_to_have=nice_to_have,
        raw_text=raw_text,
        clean_text=raw_text.lower(),
    )


# -------------------------------------------------
# 5) GET /candidates/{id}/recommended_jobs
#    Versión mínima para que el frontend funcione.
#    Más adelante se conectará al Matching Engine real.
# -------------------------------------------------
@router.get("/{candidate_id}/recommended_jobs", response_model=RecommendedJobsResponse)
def get_recommended_jobs(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    jobs = db.query(Job).all()

    recommended: List[RecommendedJobItem] = []

    for job in jobs:
        scores = RecommendedJobScores(
            global_score=75.0,
            skills_match=80.0,
            values_match=70.0,
            team_fit=65.0,
        )

        company_name = None
        if hasattr(job, "company") and job.company is not None:
            company_name = getattr(job.company, "name", None)

        # experience_required puede ser int o texto → lo normalizamos a str
        exp_req = job.experience_required
        if exp_req is not None and not isinstance(exp_req, str):
            exp_req = str(exp_req)

        item = RecommendedJobItem(
            job_id=job.id,
            title=job.title,
            company_name=company_name,
            location=getattr(job, "location", None),

            description=getattr(job, "jd_text", None),
            category=getattr(job, "category", None),
            contract_type=getattr(job, "contract_type", None),
            contract_time=getattr(job, "contract_time", None),
            job_type=getattr(job, "job_type", None),
            salary_min=getattr(job, "salary_min", None),
            salary_max=getattr(job, "salary_max", None),
            experience_required=exp_req,
            education_required=getattr(job, "education_required", None),
            area=getattr(job, "area", None),
            tech_stack=getattr(job, "tech_stack", None),
            soft_skills=getattr(job, "soft_skills", None),
            languages=getattr(job, "languages", None),
            benefits=getattr(job, "benefits", None),

            scores=scores,
        )
        recommended.append(item)

    return RecommendedJobsResponse(jobs=recommended)


# -------------------------------------------------
# 6) GET /candidates/{id}/job/{job}/gaps
#    Stub preparado para integrar lógica de gaps + cursos.
# -------------------------------------------------
@router.get("/{candidate_id}/job/{job_id}/gaps", response_model=GapsResponse)
def get_gaps_for_job(
    candidate_id: int,
    job_id: int,
    db: Session = Depends(get_db),
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    scores = RecommendedJobScores(
        global_score=75.0,
        skills_match=80.0,
        values_match=70.0,
        team_fit=65.0,
    )

    skills_section = GapsSkillsSection(
        strong=["Trabajo en equipo"],
        medium=["Python"],
        missing=["Docker"],
    )

    recommendations = GapsRecommendations(
        courses=[
            CourseRecommendation(
                title="Curso de Docker para principiantes",
                provider="Plataforma X",
                url="https://example.com/docker",
                target_skills=["Docker"],
            )
        ],
        actions=[
            "Refuerza tus conocimientos de Python con proyectos personales.",
            "Practica explicar tus decisiones técnicas a negocio.",
        ],
    )

    return GapsResponse(
        candidate_id=candidate.id,
        job_id=job.id,
        scores=scores,
        skills=skills_section,
        recommendations=recommendations,
    )
