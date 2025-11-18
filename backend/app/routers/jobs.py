from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.jobs import Job, TeamProfile, TeamMember, CoTeachingPair, Application
from app.models.companies import Company
from app.models.candidates import Candidate
from app.models.skills import CandidateSkill, JobSkill
from app.models.users import User


# TODO (cuando toque):
# from app.services.ocr.document_parser import run as parse_document
# from app.services.skills.skills_extractor import run as extract_skills
# from app.services.matching.matching_engine import run as run_matching_engine
# from app.services.matching.co_teaching import run as run_co_teaching

router = APIRouter(prefix="/jobs", tags=["jobs"])


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
class TeamMemberCreate(BaseModel):
    role: Optional[str] = None
    seniority: Optional[str] = None
    work_style: Optional[str] = None
    communication_style: Optional[str] = None
    values: Optional[List[str]] = None
    collaboration_style: Optional[str] = None


class TeamProfileCreate(BaseModel):
    team_name: Optional[str] = None
    team_mission: Optional[str] = None
    team_work_style: Optional[str] = None
    team_communication: Optional[str] = None
    team_autonomy: Optional[str] = None
    team_ideal_profile: Optional[str] = None
    members: List[TeamMemberCreate] = []


class JobCreate(BaseModel):
    company_id: int

    # Datos básicos de la vacante
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    contract_type: Optional[str] = None
    salary_range: Optional[str] = None
    seniority: Optional[str] = None
    is_remote_friendly: Optional[bool] = None

    # JD en texto plano (por ahora)
    jd_text: Optional[str] = None

    # Equipo
    team_profile: Optional[TeamProfileCreate] = None

    # Auto extracción de skills (stub)
    auto_extract_skills: bool = True


class JobSkillItem(BaseModel):
    skill_name: str
    importance: str  # "must_have" o "nice_to_have"
    weight: Optional[float] = None
    source: Optional[str] = None


class TeamMemberItem(BaseModel):
    id: int
    role: Optional[str] = None
    seniority: Optional[str] = None
    work_style: Optional[str] = None
    communication_style: Optional[str] = None
    values: List[str] = []
    collaboration_style: Optional[str] = None

    class Config:
        orm_mode = True


class TeamProfileItem(BaseModel):
    id: int
    team_name: Optional[str] = None
    team_mission: Optional[str] = None
    team_work_style: Optional[str] = None
    team_communication: Optional[str] = None
    team_autonomy: Optional[str] = None
    team_ideal_profile: Optional[str] = None
    members: List[TeamMemberItem] = []

    class Config:
        orm_mode = True


class JobDetailResponse(BaseModel):
    id: int
    company_id: int
    title: str
    department: Optional[str]
    location: Optional[str]
    contract_type: Optional[str]
    salary_range: Optional[str]
    seniority: Optional[str]
    is_remote_friendly: Optional[bool]
    jd_text: Optional[str]

    must_have: List[str] = []
    nice_to_have: List[str] = []
    all_skills: List[str] = []

    team_profile: Optional[TeamProfileItem] = None

    class Config:
        orm_mode = True


# --- Matching / analytics schemas ---
class MatchScores(BaseModel):
    global_score: float
    skills_match: float
    values_match: float
    team_fit: float


class CandidateMatchItem(BaseModel):
    candidate_id: int
    name: Optional[str] = None
    email: Optional[str] = None
    scores: MatchScores

    # Campo libre para debug del frontend (puede ser JSON completo)
    # En este stub lo dejamos como None.
    raw_match_data: Optional[dict] = None


class MatchCandidatesResponse(BaseModel):
    job_id: int
    candidates: List[CandidateMatchItem]


# --- Co-Teaching schemas ---
class CoTeachingCandidateMini(BaseModel):
    candidate_id: int
    name: Optional[str] = None
    email: Optional[str] = None


class CoTeachingPairItem(BaseModel):
    pair_id: Optional[int] = None
    job_id: int
    candidate_a: CoTeachingCandidateMini
    candidate_b: CoTeachingCandidateMini
    pair_coverage: float
    pair_risk: float
    global_score: float
    complementarities: List[str] = []


class CoTeachingResponse(BaseModel):
    job_id: int
    pairs: List[CoTeachingPairItem]


# --- Apply schema ---
class ApplyPayload(BaseModel):
    candidate_id: int


# -------------------------------------------------
# 1) POST /jobs/create
#    Crea la vacante + team_profile + team_members + skills (dummy)
# -------------------------------------------------
@router.post("/create", response_model=JobDetailResponse)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    # Verificar empresa
    company = db.query(Company).filter(Company.id == payload.company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    # Crear Job
    job = Job(
        company_id=payload.company_id,
        title=payload.title,
        department=payload.department,
        location=payload.location,
        contract_type=payload.contract_type,
        salary_range=payload.salary_range,
        seniority=payload.seniority,
        is_remote_friendly=payload.is_remote_friendly,
        jd_text=payload.jd_text,
        status="open",
    )
    db.add(job)
    db.flush()  # para obtener job.id

    # Crear TeamProfile + TeamMembers si se envían
    team_profile_obj = None
    if payload.team_profile is not None:
        tp = payload.team_profile
        team_profile_obj = TeamProfile(
            job_id=job.id,
            team_name=tp.team_name,
            team_mission=tp.team_mission,
            team_work_style=tp.team_work_style,
            team_communication=tp.team_communication,
            team_autonomy=tp.team_autonomy,
            team_ideal_profile=tp.team_ideal_profile,
        )
        db.add(team_profile_obj)
        db.flush()

        for member in tp.members:
            tm = TeamMember(
                team_profile_id=team_profile_obj.id,
                role=member.role,
                seniority=member.seniority,
                work_style=member.work_style,
                communication_style=member.communication_style,
                values=member.values or [],
                collaboration_style=member.collaboration_style,
            )
            db.add(tm)

    # Skills autoextraídas (stub)
    must_have: List[str] = []
    nice_to_have: List[str] = []
    all_skills: List[str] = []

    if payload.auto_extract_skills and payload.jd_text:
        # TODO: Integrar con Document Parser (si viene JD en fichero)
        #       e invocar Skills Extractor sobre el texto limpio.
        # De momento ponemos algunos skills dummy solo para probar el frontend:
        must_have = ["Python", "SQL"]
        nice_to_have = ["Docker", "Power BI"]
        all_skills = list(dict.fromkeys(must_have + nice_to_have))

    # Guardar JobSkill en DB
    for s in must_have:
        js = JobSkill(
            job_id=job.id,
            skill_name=s,
            importance="must_have",
            weight=1.0,
            source="auto_extracted" if payload.auto_extract_skills else "manual",
        )
        db.add(js)

    for s in nice_to_have:
        js = JobSkill(
            job_id=job.id,
            skill_name=s,
            importance="nice_to_have",
            weight=0.7,
            source="auto_extracted" if payload.auto_extract_skills else "manual",
        )
        db.add(js)

    db.commit()
    db.refresh(job)
    if team_profile_obj:
        db.refresh(team_profile_obj)

    # Preparar respuesta
    team_members_items: List[TeamMemberItem] = []
    if team_profile_obj:
        members_db = (
            db.query(TeamMember)
            .filter(TeamMember.team_profile_id == team_profile_obj.id)
            .all()
        )
        for m in members_db:
            team_members_items.append(
                TeamMemberItem(
                    id=m.id,
                    role=m.role,
                    seniority=m.seniority,
                    work_style=m.work_style,
                    communication_style=m.communication_style,
                    values=m.values or [],
                    collaboration_style=m.collaboration_style,
                )
            )

    team_profile_item: Optional[TeamProfileItem] = None
    if team_profile_obj:
        team_profile_item = TeamProfileItem(
            id=team_profile_obj.id,
            team_name=team_profile_obj.team_name,
            team_mission=team_profile_obj.team_mission,
            team_work_style=team_profile_obj.team_work_style,
            team_communication=team_profile_obj.team_communication,
            team_autonomy=team_profile_obj.team_autonomy,
            team_ideal_profile=team_profile_obj.team_ideal_profile,
            members=team_members_items,
        )

    return JobDetailResponse(
        id=job.id,
        company_id=job.company_id,
        title=job.title,
        department=job.department,
        location=job.location,
        contract_type=job.contract_type,
        salary_range=job.salary_range,
        seniority=job.seniority,
        is_remote_friendly=job.is_remote_friendly,
        jd_text=job.jd_text,
        must_have=must_have,
        nice_to_have=nice_to_have,
        all_skills=all_skills,
        team_profile=team_profile_item,
    )


# -------------------------------------------------
# 2) GET /jobs/{id}/extract_skills
#    Endpoint opcional para re-extraer skills a partir de jd_text
# -------------------------------------------------
@router.get("/{job_id}/extract_skills", response_model=JobDetailResponse)
def extract_skills_for_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    # Limpiar skills previas
    db.query(JobSkill).filter(JobSkill.job_id == job.id).delete()

    must_have: List[str] = []
    nice_to_have: List[str] = []
    all_skills: List[str] = []

    if job.jd_text:
        # TODO: igual que en create_job → conectar a Skills Extractor real.
        must_have = ["Python", "SQL"]
        nice_to_have = ["Docker", "Power BI"]
        all_skills = list(dict.fromkeys(must_have + nice_to_have))

    for s in must_have:
        js = JobSkill(
            job_id=job.id,
            skill_name=s,
            importance="must_have",
            weight=1.0,
            source="auto_extracted",
        )
        db.add(js)

    for s in nice_to_have:
        js = JobSkill(
            job_id=job.id,
            skill_name=s,
            importance="nice_to_have",
            weight=0.7,
            source="auto_extracted",
        )
        db.add(js)

    db.commit()
    db.refresh(job)

    team_profile_obj = (
        db.query(TeamProfile)
        .filter(TeamProfile.job_id == job.id)
        .first()
    )

    team_profile_item: Optional[TeamProfileItem] = None
    if team_profile_obj:
        members_db = (
            db.query(TeamMember)
            .filter(TeamMember.team_profile_id == team_profile_obj.id)
            .all()
        )
        members_items = [
            TeamMemberItem(
                id=m.id,
                role=m.role,
                seniority=m.seniority,
                work_style=m.work_style,
                communication_style=m.communication_style,
                values=m.values or [],
                collaboration_style=m.collaboration_style,
            )
            for m in members_db
        ]
        team_profile_item = TeamProfileItem(
            id=team_profile_obj.id,
            team_name=team_profile_obj.team_name,
            team_mission=team_profile_obj.team_mission,
            team_work_style=team_profile_obj.team_work_style,
            team_communication=team_profile_obj.team_communication,
            team_autonomy=team_profile_obj.team_autonomy,
            team_ideal_profile=team_profile_obj.team_ideal_profile,
            members=members_items,
        )

    return JobDetailResponse(
        id=job.id,
        company_id=job.company_id,
        title=job.title,
        department=job.department,
        location=job.location,
        contract_type=job.contract_type,
        salary_range=job.salary_range,
        seniority=job.seniority,
        is_remote_friendly=job.is_remote_friendly,
        jd_text=job.jd_text,
        must_have=must_have,
        nice_to_have=nice_to_have,
        all_skills=all_skills,
        team_profile=team_profile_item,
    )


# -------------------------------------------------
# 3) GET /jobs/{id}/match_candidates
#    Stub preparado para conectar con matching_engine.py
# -------------------------------------------------
@router.get("/{job_id}/match_candidates", response_model=MatchCandidatesResponse)
def match_candidates_for_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    candidates = db.query(Candidate).all()
    items: List[CandidateMatchItem] = []

    for cand in candidates:
        user = db.query(User).filter(User.id == cand.user_id).first()

        # TODO: aquí deberíamos llamar a matching_engine.run(candidate, job)
        scores = MatchScores(
            global_score=75.0,
            skills_match=80.0,
            values_match=70.0,
            team_fit=65.0,
        )

        item = CandidateMatchItem(
            candidate_id=cand.id,
            name=cand.name,
            email=user.email if user else None,
            scores=scores,
            raw_match_data=None,
        )
        items.append(item)

    # Ordenamos por mejor encaje global
    items.sort(key=lambda x: x.scores.global_score, reverse=True)

    return MatchCandidatesResponse(
        job_id=job.id,
        candidates=items,
    )


# -------------------------------------------------
# 4) GET /jobs/{id}/co_teaching
#    Stub preparado para conectar con co_teaching.py
# -------------------------------------------------
@router.get("/{job_id}/co_teaching", response_model=CoTeachingResponse)
def get_co_teaching_pairs(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    # TODO: integrar con run_co_teaching(job_id) para obtener parejas reales
    # De momento, generamos una pareja dummy si hay al menos 2 candidatos.
    candidates = db.query(Candidate).all()
    pairs: List[CoTeachingPairItem] = []

    if len(candidates) >= 2:
        a = candidates[0]
        b = candidates[1]

        user_a = db.query(User).filter(User.id == a.user_id).first()
        user_b = db.query(User).filter(User.id == b.user_id).first()

        pair = CoTeachingPairItem(
            pair_id=None,
            job_id=job.id,
            candidate_a=CoTeachingCandidateMini(
                candidate_id=a.id,
                name=a.name,
                email=user_a.email if user_a else None,
            ),
            candidate_b=CoTeachingCandidateMini(
                candidate_id=b.id,
                name=b.name,
                email=user_b.email if user_b else None,
            ),
            pair_coverage=85.0,
            pair_risk=20.0,
            global_score=82.0,
            complementarities=[
                "A aporta profundidad técnica.",
                "B aporta comunicación con negocio.",
            ],
        )
        pairs.append(pair)

    return CoTeachingResponse(
        job_id=job.id,
        pairs=pairs,
    )


# -------------------------------------------------
# 5) POST /jobs/{job_id}/apply
#    Candidato solicita una vacante (crea Application si no existe)
# -------------------------------------------------
@router.post("/{job_id}/apply")
def apply_to_job(job_id: int, payload: ApplyPayload, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    candidate = db.query(Candidate).filter(Candidate.id == payload.candidate_id).first()
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # ¿Ya existe la application?
    existing = (
        db.query(Application)
        .filter(
            Application.job_id == job_id,
            Application.candidate_id == payload.candidate_id,
        )
        .first()
    )
    if existing:
        return {
            "status": "ok",
            "message": "Ya habías solicitado esta vacante.",
            "application_id": existing.id,
        }

    application = Application(
        job_id=job_id,
        candidate_id=payload.candidate_id,
        status="applied",
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return {
        "status": "ok",
        "message": "Solicitud registrada correctamente.",
        "application_id": application.id,
    }
