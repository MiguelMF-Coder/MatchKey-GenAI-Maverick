# backend/app/db/init_db.py

from app.db.session import engine
from app.models import Base  # viene de models/__init__.py, que a su vez importa los modelos


def init_db():
    print("Creando las tablas en la base de datos (si no existen)...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas.")


if __name__ == "__main__":
    init_db()
    print("✅ Base de datos inicializada.")