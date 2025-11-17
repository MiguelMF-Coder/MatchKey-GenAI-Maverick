# backend/app/models/users.py
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # de momento dummy
    role = Column(String(50), nullable=False)  # "candidate" | "company"
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    candidate = relationship("Candidate", back_populates="user", uselist=False)
    company = relationship("Company", back_populates="user", uselist=False)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
