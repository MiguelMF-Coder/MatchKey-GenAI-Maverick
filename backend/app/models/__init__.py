# backend/app/models/__init__.py

from .base import Base

# Importa los módulos de modelos para que SQLAlchemy los registre en Base.metadata
from . import users
from . import candidates
from . import companies
from . import skills
from . import jobs
from . import interviews
