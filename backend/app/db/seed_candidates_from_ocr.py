# backend/app/db/seed_candidates_from_ocr.py

import json
from pathlib import Path

from .session import SessionLocal
from app.models.users import User
from app.models.candidates import Candidate
from app.models.skills import CandidateSkill
from app.models.interviews import CandidateInterview

# 📂 Rutas a los JSON que ya tienes en services/ocr/data
BASE_DIR = Path(__file__).resolve().parents[1]  # backend/app
OCR_DATA_DIR = BASE_DIR / "services" / "ocr" / "data"

USERS_JSON = OCR_DATA_DIR / "usuarios_web_100_from_ocr.json"
CV_JSON = OCR_DATA_DIR / "cv_ocr_analizados_100.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def seed_candidates_from_ocr():
    """
    Crea/actualiza Users, Candidates, CandidateSkills y una CandidateInterview
    usando los datos de OCR de 100 CV.
    Idempotente: no duplica users ni skills.
    """
    session = SessionLocal()

    if not USERS_JSON.exists() or not CV_JSON.exists():
        print("[seed_candidates_from_ocr] ⚠️ JSONs no encontrados, saltando seeding.")
        print(f"  BUSCADO: {USERS_JSON}")
        print(f"  BUSCADO: {CV_JSON}")
        session.close()
        return

    users_data = load_json(USERS_JSON)
    cv_data = load_json(CV_JSON)

    # Índice por email para cruzar rápido
    cv_by_email = {cv["email"]: cv for cv in cv_data}

    try:
        for u in users_data:
            email = u["email"]
            cv = cv_by_email.get(email)
            if not cv:
                print(f"[seed_candidates_from_ocr] ⚠️ No hay CV para email {email}, saltando.")
                continue

            # 1) USER
            user = session.query(User).filter_by(email=email).first()
            if not user:
                user = User(
                    email=email,
                    # De momento usáis password_hash "dummy"
                    password_hash=u["password"],
                    role=u.get("role", "candidate"),
                )
                session.add(user)
                session.flush()

            # 2) CANDIDATE
            candidate = (
                session.query(Candidate)
                .filter_by(user_id=user.id)
                .first()
            )
            if not candidate:
                name = cv.get("name") or u.get("full_name")
                location = u.get("location") or cv.get("location")
                years_experience = u.get("years_experience", cv.get("years_experience", 0))
                contact_phone = cv.get("phone")
                contact_email = email
                summary = cv.get("document_parser", {}).get("raw_text", None)

                candidate = Candidate(
                    user_id=user.id,
                    name=name,
                    headline=None,
                    location=location,
                    summary=summary,
                    years_experience=years_experience,
                    contact_email=contact_email,
                    contact_phone=contact_phone,
                )
                session.add(candidate)
                session.flush()

            # 3) CANDIDATE INTERVIEW (usar el CV OCR como “entrevista base” si no tiene ninguna)
            if not candidate.interviews:
                doc_parser = cv.get("document_parser", {})
                raw_text = doc_parser.get("raw_text", "")
                clean_text = doc_parser.get("clean_text", "")
                metadata = doc_parser.get("metadata", {})

                answers_payload = {
                    "source": "cv_ocr",
                    "raw_text": raw_text,
                    "clean_text": clean_text,
                    "metadata": metadata,
                }

                interview = CandidateInterview(
                    candidate_id=candidate.id,
                    answers_json=json.dumps(answers_payload, ensure_ascii=False),
                    motivations=None,
                    values_detected=None,
                    soft_skills=None,
                    team_preferences=None,
                    psych_summary=None,
                )
                session.add(interview)

            # 4) CANDIDATE SKILLS
            skills_block = cv.get("skills", {})
            tech_skills = skills_block.get("technical", []) or []
            soft_skills = skills_block.get("soft", []) or []
            all_skills = tech_skills + soft_skills

            seen = set()
            unique_skills = []
            for s in all_skills:
                if s not in seen:
                    seen.add(s)
                    unique_skills.append(s)

            for skill_name in unique_skills:
                exists = (
                    session.query(CandidateSkill)
                    .filter_by(candidate_id=candidate.id, skill_name=skill_name)
                    .first()
                )
                if not exists:
                    session.add(
                        CandidateSkill(
                            candidate_id=candidate.id,
                            skill_name=skill_name,
                            level=None,
                            source="cv",  # viene del CV/OCR
                        )
                    )

        session.commit()
        print("[seed_candidates_from_ocr] ✅ Seeding de candidatos desde OCR completado.")
    except Exception as e:
        session.rollback()
        print(f"[seed_candidates_from_ocr] ❌ Error durante el seeding: {e}")
        raise
    finally:
        session.close()
