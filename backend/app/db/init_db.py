# backend/app/db/init_db.py

from app.db.session import engine, SessionLocal
from app.models import Base  # viene de models/__init__.py

from sqlalchemy.orm import Session

# Seeds existentes
from app.db.seed_jobs_from_scraping import seed_jobs_from_scraping
from app.db.seed_companies_from_values_dataset import seed_companies_from_values_dataset
from app.db.seed_candidates_from_ocr import seed_candidates_from_ocr
from app.db.seed_fake_applications import seed_fake_applications
from app.db.seed_teams_and_members import seed_team_profiles

# Modelos
from app.models.users import User
from app.models.companies import Company


def init_db():
    print("Creando las tablas en la base de datos (si no existen)...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas.")

    # Ejecutar seeds
    print("🔄 Ejecutando seeds de datos...")
    seed_jobs_from_scraping()
    seed_companies_from_values_dataset()
    seed_candidates_from_ocr()
    seed_fake_applications()
    print("✅ Seeds ejecutados.")

    # Crear usuario demo de Accenture
    print("🔄 Creando usuario demo de Accenture (si no existe)...")
    create_accenture_demo_user()
    print("✅ Usuario demo de Accenture listo.")


def create_accenture_demo_user() -> None:
    """
    Crea (si no existe) un usuario de empresa demo para Accenture
    y lo vincula a la Company 'Accenture' que viene del scraping.
    Se intenta ser robusto con los nombres de campos (hashed_password/password,
    user.company_id / company.user_id, etc.).
    """
    db: Session = SessionLocal()

    DEMO_EMAIL = "accenture.demo@matchkey.ai"
    DEMO_PASSWORD = "accenture123"

    try:
        # 1) Buscar la empresa Accenture (por nombre)
        company = (
            db.query(Company)
            .filter(Company.name.ilike("%Accenture%"))
            .first()
        )

        if not company:
            # Si por lo que sea no existe en el scraping, la creamos mínima
            company = Company(
                name="Accenture",
                description="Empresa global de servicios profesionales.",
            )
            db.add(company)
            db.flush()  # para tener company.id

        # 2) Buscar usuario por email
        user = db.query(User).filter(User.email == DEMO_EMAIL).first()

        if not user:
            # Resolver nombre del campo de contraseña (hashed_password o password)
            user_kwargs = {
                "email": DEMO_EMAIL,
                "role": "company",
            }

            if hasattr(User, "hashed_password"):
                user_kwargs["hashed_password"] = DEMO_PASSWORD
            elif hasattr(User, "password"):
                user_kwargs["password"] = DEMO_PASSWORD

            # Resolver relación user <-> company según tu modelo
            if hasattr(User, "company_id"):
                user_kwargs["company_id"] = company.id

            user = User(**user_kwargs)
            db.add(user)
            db.flush()  # para tener user.id

            # Caso alternativo: si la relación está en Company (company.user_id)
            if hasattr(company, "user_id") and getattr(company, "user_id") is None:
                company.user_id = user.id

        else:
            # Si ya existe, aseguramos vínculo con Accenture
            if hasattr(User, "company_id") and getattr(user, "company_id", None) is None:
                user.company_id = company.id
            if hasattr(company, "user_id") and getattr(company, "user_id", None) is None:
                company.user_id = user.id

        db.commit()

    except Exception as e:
        db.rollback()
        print(f"⚠️ Error creando usuario demo de Accenture: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("✅ Base de datos inicializada.")
