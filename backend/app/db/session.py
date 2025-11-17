# backend/app/db/session.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base  # ajusta el import según tu estructura real

# Puedes leer la URL de la BBDD de una variable de entorno
# En Docker, normalmente pondrás algo tipo:
# postgresql+psycopg2://user:password@db:5432/matchkey

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://matchkey_user:matchkey_password@db:5432/matchkey"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,  # pon True si quieres ver las queries en consola
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
