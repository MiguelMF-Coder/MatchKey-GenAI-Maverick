from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db.session import SessionLocal
from app.models.users import User
from app.models.candidates import Candidate
from app.models.companies import Company

router = APIRouter(prefix="/auth", tags=["auth"])


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
# Password hashing (bcrypt)
# -----------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _normalize_password(pwd: str) -> str:
    """
    Bcrypt solo admite hasta 72 bytes.
    Para evitar errores raros, truncamos la contraseña a 72 chars.
    """
    if pwd is None:
        return ""
    return pwd[:72]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password = _normalize_password(plain_password)
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    password = _normalize_password(password)
    return pwd_context.hash(password)


# -----------------------------
# Esquemas Pydantic
# -----------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: Literal["candidate", "company"]


class LoginResponse(BaseModel):
    user_id: int
    email: EmailStr
    role: Literal["candidate", "company"]
    candidate_id: Optional[int] = None
    company_id: Optional[int] = None


# -------------------------------------------------
# POST /auth/login
#  - Si el usuario NO existe → lo crea con ese rol + contraseña
#  - Si existe → comprueba contraseña y rol
#  - Asegura que existe Candidate o Company asociado
# -------------------------------------------------
@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # Buscar usuario por email
    user = db.query(User).filter(User.email == payload.email).first()

    # -----------------------
    # Caso 1: usuario nuevo → registramos sobre la marcha
    # -----------------------
    if user is None:
        user = User(
            email=payload.email,
            role=payload.role,
            password_hash=get_password_hash(payload.password),
        )
        db.add(user)
        db.flush()  # para tener user.id

        candidate_id: Optional[int] = None
        company_id: Optional[int] = None

        if payload.role == "candidate":
            candidate = Candidate(
                user_id=user.id,
                name=None,  # name es nullable en el modelo, no pasa nada
            )
            db.add(candidate)
            db.flush()
            candidate_id = candidate.id

        elif payload.role == "company":
            # Usamos el prefijo del email como nombre temporal de empresa
            default_name = payload.email.split("@")[0]
            company = Company(
                user_id=user.id,
                name=default_name,
            )
            db.add(company)
            db.flush()
            company_id = company.id

        db.commit()
        db.refresh(user)

        return LoginResponse(
            user_id=user.id,
            email=user.email,
            role=user.role,
            candidate_id=candidate_id,
            company_id=company_id,
        )

    # -----------------------
    # Caso 2: usuario ya existe → comprobamos
    # -----------------------

    # Rol coherente
    if user.role != payload.role:
        raise HTTPException(
            status_code=400,
            detail=f"El usuario existe pero tiene rol '{user.role}', no '{payload.role}'.",
        )

    # Contraseña:
    # - si no tiene password_hash (usuarios antiguos) → la seteamos ahora
    # - si tiene → verificamos
    if not user.password_hash:
        user.password_hash = get_password_hash(payload.password)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        if not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # Aseguramos candidate/company
    candidate_id: Optional[int] = None
    company_id: Optional[int] = None

    if user.role == "candidate":
        candidate = db.query(Candidate).filter(Candidate.user_id == user.id).first()
        if candidate is None:
            candidate = Candidate(user_id=user.id, name=None)
            db.add(candidate)
            db.flush()
            db.commit()
            db.refresh(candidate)
        candidate_id = candidate.id

    elif user.role == "company":
        company = db.query(Company).filter(Company.user_id == user.id).first()
        if company is None:
            default_name = user.email.split("@")[0]
            company = Company(user_id=user.id, name=default_name)
            db.add(company)
            db.flush()
            db.commit()
            db.refresh(company)
        company_id = company.id

    return LoginResponse(
        user_id=user.id,
        email=user.email,
        role=user.role,
        candidate_id=candidate_id,
        company_id=company_id,
    )
