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
from app.services.notifications.email_service import send_selection_email

from app.services.matching.matching_engine import (
    compute_skills_fit,
    compute_values_fit,
    compute_team_fit,
    compute_global_fit,
    build_candidate_skills_list,
    build_job_skills_list,
)

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
class CandidateSummary(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: str
    headline: Optional[str] = None
    location: Optional[str] = None
    years_experience: Optional[float] = None

class MatchingScores(BaseModel):
    skills_fit: float
    values_fit: float
    team_fit: float
    global_fit: float

class JobApplicationWithMatchingResponse(BaseModel):
    application_id: int
    candidate: CandidateSummary
    status: Optional[str] = None
    created_at: Optional[str] = None  # o datetime si ya lo usas así
    scores: MatchingScores

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


class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    contract_type: Optional[str] = None
    salary_range: Optional[str] = None
    seniority: Optional[str] = None
    is_remote_friendly: Optional[bool] = None
    jd_text: Optional[str] = None
    status: Optional[str] = None


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


@router.get("/{job_id}/applications")
def list_job_applications(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    applications = (
        db.query(Application)
        .filter(Application.job_id == job_id)
        .all()
    )

    # Juntamos info de Candidate para mostrar en frontend
    result = []
    for app in applications:
        cand = (
            db.query(Candidate)
            .filter(Candidate.id == app.candidate_id)
            .first()
        )
        if not cand:
            continue

        user = db.query(User).filter(User.id == cand.user_id).first() if cand.user_id else None

        result.append(
            {
                "application_id": app.id,
                "candidate_id": cand.id,
                "candidate_name": cand.name,
                "candidate_email": user.email if user else None,
                # Si tienes campo cv_url o similar en Candidate, añádelo aquí:
                # "cv_url": cand.cv_url,
                "applied_at": getattr(app, "created_at", None),
                "status": getattr(app, "status", None),
            }
        )

    return {
        "job_id": job.id,
        "job_title": job.title,
        "company_id": job.company_id,
        "applications": result,
    }


@router.post("/{job_id}/applications/{application_id}/select")
def select_application(job_id: int, application_id: int, db: Session = Depends(get_db)):
    app = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.job_id == job_id,
        )
        .first()
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    job = db.query(Job).filter(Job.id == job_id).first()
    candidate = db.query(Candidate).filter(Candidate.id == app.candidate_id).first()
    company = db.query(Company).filter(Company.id == job.company_id).first()

    if not candidate or not company:
        raise HTTPException(status_code=400, detail="Invalid candidate or company")

    user = db.query(User).filter(User.id == candidate.user_id).first() if candidate.user_id else None
    candidate_email = getattr(candidate, "email", None) or (user.email if user else None)

    # Actualizamos status si existe el campo
    if hasattr(app, "status"):
        app.status = "selected"
    db.add(app)
    db.commit()

    # Enviar email (puede ser real o stub según configuración)
    if candidate_email:
        send_selection_email(
            candidate_email=candidate_email,
            candidate_name=candidate.name,
            job_title=job.title,
            company_name=company.name,
        )

    return {
        "message": "Candidate selected and email sent (if email service is configured).",
        "application_id": app.id,
        "candidate_id": candidate.id,
        "job_id": job.id,
    }


# -------------------------------------------------
# 6) PUT /jobs/{job_id}
#    Actualizar datos de una vacante existente
# -------------------------------------------------
@router.put("/{job_id}", response_model=JobDetailResponse)
def update_job(job_id: int, payload: JobUpdate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    db.add(job)
    db.commit()
    db.refresh(job)

    # Recuperar skills actuales
    job_skills = db.query(JobSkill).filter(JobSkill.job_id == job.id).all()
    must_have = [s.skill_name for s in job_skills if s.importance == "must_have"]
    nice_to_have = [s.skill_name for s in job_skills if s.importance == "nice_to_have"]
    all_skills = list(dict.fromkeys(must_have + nice_to_have))

    # Recuperar team_profile y miembros
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
# 7) DELETE /jobs/{job_id}
#    Eliminar una vacante y datos relacionados
# -------------------------------------------------
@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Borrar Applications
    db.query(Application).filter(Application.job_id == job_id).delete()

    # Borrar JobSkills
    db.query(JobSkill).filter(JobSkill.job_id == job_id).delete()

    # Borrar TeamProfiles y TeamMembers asociados
    team_profiles = db.query(TeamProfile).filter(TeamProfile.job_id == job_id).all()
    for tp in team_profiles:
        db.query(TeamMember).filter(TeamMember.team_profile_id == tp.id).delete()
    db.query(TeamProfile).filter(TeamProfile.job_id == job_id).delete()

    # Borrar CoTeachingPairs
    db.query(CoTeachingPair).filter(CoTeachingPair.job_id == job_id).delete()

    # Borrar el Job
    db.delete(job)
    db.commit()

    return {
        "status": "ok",
        "message": "Job and related data deleted successfully.",
        "job_id": job_id,
    }

@router.get(
    "/jobs/{job_id}/applications_with_matching",
    response_model=List[JobApplicationWithMatchingResponse],
)
def get_job_applications_with_matching(job_id: int, db: Session = Depends(get_db)):
    # 1) Aseguramos que existe el job
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # 2) Cargamos las applications de esa vacante
    applications = (
        db.query(Application)
        .filter(Application.job_id == job_id)
        .order_by(Application.created_at.desc())
        .all()
    )

    results: List[JobApplicationWithMatchingResponse] = []

    for app_obj in applications:
        candidate = (
            db.query(Candidate)
            .filter(Candidate.id == app_obj.candidate_id)
            .first()
        )
        if not candidate:
            # Si por algún motivo hay una aplicación huérfana, la saltamos
            continue

        user = db.query(User).filter(User.id == candidate.user_id).first()
        email = user.email if user else ""

        # 3) Construir listas de skills para candidate y job usando la misma lógica que el matching real
        candidate_skills = build_candidate_skills_list(db, candidate)
        job_skills = build_job_skills_list(db, job)

        # 4) Calcular scores reales
        skills_fit = compute_skills_fit(candidate_skills, job_skills)
        values_fit = compute_values_fit(candidate, job)
        team_fit = compute_team_fit(candidate, job)
        global_fit = compute_global_fit(skills_fit, values_fit, team_fit)

        candidate_summary = CandidateSummary(
            id=candidate.id,
            full_name=candidate.full_name,
            email=email,
            headline=getattr(candidate, "headline", None),
            location=getattr(candidate, "location", None),
            years_experience=getattr(candidate, "years_experience", None),
        )

        scores = MatchingScores(
            skills_fit=skills_fit,
            values_fit=values_fit,
            team_fit=team_fit,
            global_fit=global_fit,
        )

        results.append(
            JobApplicationWithMatchingResponse(
                application_id=app_obj.id,
                candidate=candidate_summary,
                status=getattr(app_obj, "status", None),
                created_at=app_obj.created_at.isoformat() if app_obj.created_at else None,
                scores=scores,
            )
        )

    return results