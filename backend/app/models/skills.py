# backend/app/models/skills.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class CandidateSkill(Base, TimestampMixin):
    __tablename__ = "candidate_skills"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)

    skill_name = Column(String(255), nullable=False, index=True)
    level = Column(String(50), nullable=True)  # "beginner" / "intermediate" / "advanced" o 1–5
    source = Column(String(50), nullable=True)  # "cv" | "manual" | "hr_copilot" | etc.

    candidate = relationship("Candidate", back_populates="skills")

    def __repr__(self) -> str:
        return f"<CandidateSkill candidate_id={self.candidate_id} skill={self.skill_name}>"


class JobSkill(Base, TimestampMixin):
    __tablename__ = "job_skills"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)

    skill_name = Column(String(255), nullable=False, index=True)
    importance = Column(String(50), nullable=False)  # "must_have" | "nice_to_have"
    weight = Column(Integer, nullable=True)  # 0–100, opcional
    source = Column(String(50), nullable=True)  # "auto_extracted" | "manual"

    job = relationship("Job", back_populates="skills")

    def __repr__(self) -> str:
        return f"<JobSkill job_id={self.job_id} skill={self.skill_name} importance={self.importance}>"
