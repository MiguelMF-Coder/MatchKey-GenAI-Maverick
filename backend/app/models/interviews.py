# backend/app/models/interviews.py
from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class CandidateInterview(Base, TimestampMixin):
    """
    Resultado de una 'Llamada IA' del HR Copilot.
    """
    __tablename__ = "candidate_interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)

    answers_json = Column(Text, nullable=True)        # preguntas y respuestas crudas
    motivations = Column(Text, nullable=True)
    values_detected = Column(Text, nullable=True)     # JSON (lista de valores)
    soft_skills = Column(Text, nullable=True)         # JSON (lista de soft skills)
    team_preferences = Column(Text, nullable=True)
    psych_summary = Column(Text, nullable=True)

    candidate = relationship("Candidate", back_populates="interviews")

    def __repr__(self) -> str:
        return f"<CandidateInterview id={self.id} candidate_id={self.candidate_id}>"
