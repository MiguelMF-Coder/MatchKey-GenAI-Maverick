# backend/app/models/candidates.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Candidate(Base, TimestampMixin):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    name = Column(String(255), nullable=True)
    headline = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    years_experience = Column(Integer, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)

    user = relationship("User", back_populates="candidate")
    skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")
    interviews = relationship("CandidateInterview", back_populates="candidate", cascade="all, delete-orphan")
    # cvs = relationship("CV", back_populates="candidate", cascade="all, delete-orphan")

    applications = relationship("Application", back_populates="candidate")
    recommendations = relationship("JobRecommendation", back_populates="candidate")
    co_teaching_pairs_a = relationship(
        "CoTeachingPair",
        foreign_keys="CoTeachingPair.candidate_a_id",
        back_populates="candidate_a",
    )
    co_teaching_pairs_b = relationship(
        "CoTeachingPair",
        foreign_keys="CoTeachingPair.candidate_b_id",
        back_populates="candidate_b",
    )

    def __repr__(self) -> str:
        return f"<Candidate id={self.id} name={self.name}>"
