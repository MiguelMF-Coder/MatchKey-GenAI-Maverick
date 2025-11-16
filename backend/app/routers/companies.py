from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def create_company():
    # Más adelante se conectará a la BD
    return {"company_id": 1, "name": "Empresa Demo"}

@router.get("/{company_id}")
def get_company(company_id: int):
    return {"company_id": company_id, "name": "Empresa Demo", "values": ["innovación", "colaboración"]}
