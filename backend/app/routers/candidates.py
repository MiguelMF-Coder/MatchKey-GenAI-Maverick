from fastapi import APIRouter

router = APIRouter()

@router.get("/{candidate_id}")
def get_candidate(candidate_id: int):
    return {"candidate_id": candidate_id, "name": "Candidato Demo"}

@router.post("/{candidate_id}/upload_cv")
def upload_cv(candidate_id: int):
    # Aquí luego Pablo M enchufa OCR + skills
    return {
        "candidate_id": candidate_id,
        "skills": ["python", "sql"],
        "background": {"degree": "Grado Demo", "university": "UFV"}
    }

@router.get("/{candidate_id}/recommended_jobs")
def recommended_jobs(candidate_id: int):
    # Luego se usará matching_engine
    return {
        "candidate_id": candidate_id,
        "recommended_jobs": [
            {"job_id": 1, "title": "Data Analyst", "score_global": 0.82},
            {"job_id": 2, "title": "ML Engineer", "score_global": 0.76},
        ],
    }

@router.get("/{candidate_id}/job/{job_id}/gaps")
def job_gaps(candidate_id: int, job_id: int):
    # Luego se usará tutor_agent + cursos de Pablo
    return {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "current_score": 0.68,
        "potential_score": 0.84,
        "gaps": [
            {"skill": "docker", "status": "missing", "course": "Curso Docker Básico"},
            {"skill": "airflow", "status": "missing", "course": "Curso Airflow Intro"},
        ],
    }
