from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
def login(email: str, password: str):
    #Dummy login
    return {
        "user_id": 1,
        "role": "candidate",
        "name": "Usuario Demo",
    }