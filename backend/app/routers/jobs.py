from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def create_job():
    return {"job_id": 1, "title": "Data Analyst Demo"}

@router.get("/")
def list_jobs():
    return [
        {"job_id": 1, "title": "Data Analyst Demo"},
        {"job_id": 2, "title": "ML Engineer Demo"},
    ]

@router.post("/{job_id}/extract_skills")
def extract_skills(job_id: int):
    # Luego llamará a skills_extractor de Pablo M
    return {
        "job_id": job_id,
        "must_have": ["python", "sql"],
        "nice_to_have": ["docker", "airflow"]
    }

@router.get("/{job_id}/match_candidates")
def match_candidates(job_id: int):
    # Luego se conectará con matching_engine
    return {
        "job_id": job_id,
        "matches": [
            {
                "candidate_id": 1,
                "name": "Miguel Demo",
                "score_global": 0.87,
                "skills_match": 0.9,
                "values_match": 0.8,
                "team_fit": 0.85,
                "interview_summary": "Perfil proactivo orientado al aprendizaje."
            }
        ]
    }

@router.get("/{job_id}/co_teaching")
def co_teaching(job_id: int):
    # Luego se conectará con co_teaching_agent
    return {
        "job_id": job_id,
        "pairs": [
            {
                "candidates": [1, 2],
                "coverage_must": 1.0,
                "coverage_nice": 0.8,
                "comment": "A domina Docker, B domina Airflow."
            }
        ]
    }
