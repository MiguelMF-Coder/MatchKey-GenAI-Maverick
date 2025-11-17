# backend/app/models/companies.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    name = Column(String(255), nullable=False)
    industry = Column(String(255), nullable=True)
    size = Column(String(50), nullable=True)  # "small" | "medium" | "large" | etc.
    location = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    user = relationship("User", back_populates="company")
    culture = relationship(
        "CompanyCulture",
        back_populates="company",
        uselist=False,
        cascade="all, delete-orphan",
    )
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Company id={self.id} name={self.name}>"


class CompanyCulture(Base, TimestampMixin):
    __tablename__ = "company_culture"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)

    values = Column(Text, nullable=True)  # JSON string (lista de valores)
    culture_description = Column(Text, nullable=True)
    leadership_style = Column(String(255), nullable=True)
    work_mode = Column(String(50), nullable=True)  # remote / hybrid / onsite / unspecified
    perks = Column(Text, nullable=True)  # JSON string
    team_fit_summary = Column(Text, nullable=True)

    company = relationship("Company", back_populates="culture")

    def __repr__(self) -> str:
        return f"<CompanyCulture company_id={self.company_id}>"
