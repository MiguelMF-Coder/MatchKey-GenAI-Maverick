# backend/app/db/seed_team_profiles.py

import random
from sqlalchemy.orm import Session

from app.models.jobs import Job
from app.models.companies import Company
from app.models.jobs import TeamProfile, TeamMember


# --------- PLANTILLAS DE EQUIPOS ---------

TEAM_TEMPLATES = {
    "data": {
        "team_name": "Data & Analytics",
        "team_mission": "Transformar datos en conocimiento accionable para el negocio.",
        "team_work_style": "Colaborativo, orientado a hipótesis y validación rápida.",
        "team_communication": "Clara, basada en métricas y documentación.",
        "team_autonomy": "Alta autonomía, ownership individual por proyecto.",
        "team_ideal_profile": "Personas analíticas, curiosas y orientadas a impacto.",
        "members": [
            ("Data Analyst", "Mid"),
            ("Data Scientist", "Senior"),
            ("Data Engineer", "Mid"),
            ("BI Analyst", "Junior"),
        ],
        "keywords": ["data", "analytics", "analyst", "bi", "machine learning"],
    },
    "tech": {
        "team_name": "Engineering",
        "team_mission": "Construir y mantener sistemas escalables y robustos.",
        "team_work_style": "Enfoque en calidad, buenas prácticas y entregas continuas.",
        "team_communication": "Directa, orientada a soluciones técnicas.",
        "team_autonomy": "Muy alta: ownership por servicio/módulo.",
        "team_ideal_profile": "Personas estructuradas, resolutivas y con rigor técnico.",
        "members": [
            ("Backend Engineer", "Mid"),
            ("Frontend Engineer", "Mid"),
            ("Fullstack Engineer", "Senior"),
            ("DevOps Engineer", "Senior"),
        ],
        "keywords": ["software", "developer", "backend", "frontend", "engineer", "fullstack"],
    },
    "business": {
        "team_name": "Business & Strategy",
        "team_mission": "Guiar decisiones estratégicas y conectar negocio con producto.",
        "team_work_style": "Trabajo transversal, alto contacto con stakeholders.",
        "team_communication": "Alta comunicación, foco en claridad y alineamiento.",
        "team_autonomy": "Moderada, decisiones compartidas.",
        "team_ideal_profile": "Personas comunicativas y orientadas a negocio.",
        "members": [
            ("Business Analyst", "Junior"),
            ("Product Owner", "Mid"),
            ("Product Manager", "Mid"),
            ("Strategy Consultant", "Senior"),
        ],
        "keywords": ["product", "business", "strategy", "growth", "marketing"],
    },
    "operations": {
        "team_name": "Operations",
        "team_mission": "Asegurar procesos eficientes y servicio sin interrupciones.",
        "team_work_style": "Procesos claros, documentación y estabilidad.",
        "team_communication": "Formal y orientada a procedimientos.",
        "team_autonomy": "Baja a moderada, foco en cumplimiento de procesos.",
        "team_ideal_profile": "Personas ordenadas, fiables y orientadas a procesos.",
        "members": [
            ("Operations Specialist", "Mid"),
            ("Customer Success", "Junior"),
            ("Project Coordinator", "Mid"),
        ],
        "keywords": [],
    },
}


# --------- ATRIBUTOS DE MIEMBROS ---------

WORK_STYLES = [
    "Colaborativo",
    "Independiente",
    "Analítico",
    "Creativo",
    "Orientado a resultados",
]

COMMUNICATION_STYLES = [
    "Directo",
    "Empático",
    "Estructurado",
    "Informal",
]

COLLAB_STYLES = [
    "Trabajo en pareja",
    "Trabajo en squad",
    "Trabajo individual con revisiones",
]

VALUES = [
    "Responsabilidad",
    "Calidad",
    "Transparencia",
    "Innovación",
    "Trabajo en equipo",
]


# --------- DETECTAR TIPO DE EQUIPO SEGÚN JOB ---------

def _guess_team_type(job):
    text = f"{job.title} {job.category} {job.area}".lower()
    for t_type, info in TEAM_TEMPLATES.items():
        if any(kw in text for kw in info["keywords"]):
            return t_type
    return "operations"


# --------- SEED PRINCIPAL ---------

def seed_team_profiles(db: Session):
    existing = db.query(TeamProfile).count()
    if existing > 0:
        print(f"[seed_team_profiles] Ya existen {existing} equipos. Skipping.")
        return

    companies = db.query(Company).all()

    for company in companies:
        company_jobs = db.query(Job).filter(Job.company_id == company.id).all()
        if not company_jobs:
            continue

        # Detectamos qué tipos necesita esta empresa
        detected_types = { _guess_team_type(job) for job in company_jobs }

        for t_type in detected_types:
            template = TEAM_TEMPLATES[t_type]

            profile = TeamProfile(
                company_id=company.id,
                team_name=f"{template['team_name']} - {company.name}",
                team_mission=template["team_mission"],
                team_work_style=template["team_work_style"],
                team_communication=template["team_communication"],
                team_autonomy=template["team_autonomy"],
                team_ideal_profile=template["team_ideal_profile"],
            )
            db.add(profile)
            db.flush()  # necesitamos el ID

            # Crear miembros
            for role, seniority in random.sample(template["members"], k=min(3, len(template["members"]))):
                member = TeamMember(
                    team_profile_id=profile.id,
                    role=role,
                    seniority=seniority,
                    work_style=random.choice(WORK_STYLES),
                    communication_style=random.choice(COMMUNICATION_STYLES),
                    collaboration_style=random.choice(COLLAB_STYLES),
                    values=random.sample(VALUES, k=2),
                )
                db.add(member)

            # Asignar jobs compatibles a este equipo
            for job in company_jobs:
                if _guess_team_type(job) == t_type:
                    job.team_profile_id = profile.id
                    db.add(job)

    db.commit()
    print("[seed_team_profiles] Equipos + miembros creados con éxito.")
