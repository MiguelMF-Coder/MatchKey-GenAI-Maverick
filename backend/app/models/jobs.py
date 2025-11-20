# backend/app/models/jobs.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, Boolean, JSON
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin



class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)

    # Basic job info
    title = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="open")  # open/closed/draft
    jd_text = Column(Text, nullable=True)
    
    # Job classification
    area = Column(JSON, nullable=True)
    category = Column(String(255), nullable=True)
    job_type = Column(String(100), nullable=True)
    
    # Contract details
    contract_type = Column(String(100), nullable=True)
    contract_time = Column(String(100), nullable=True)
    seniority = Column(String(50), nullable=True)
    is_remote_friendly = Column(Integer, nullable=True)  # 0/1
    
    # Salary information
    salary_range = Column(String(100), nullable=True)  # Legacy field
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_is_predicted = Column(Boolean, default=False)
    
    # Requirements (using Text for longer content)
    experience_required = Column(Text, nullable=True)
    education_required = Column(Text, nullable=True)

    # Skills and attributes (JSON fields)
    tech_stack = Column(JSON, nullable=True)
    soft_skills = Column(JSON, nullable=True)
    languages = Column(JSON, nullable=True)
    benefits = Column(JSON, nullable=True)

    company = relationship("Company", back_populates="jobs")
    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    team_profile = relationship(
        "TeamProfile",
        back_populates="job",
        uselist=False,
        cascade="all, delete-orphan",
    )
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    recommendations = relationship("JobRecommendation", back_populates="job", cascade="all, delete-orphan")
    co_teaching_pairs = relationship("CoTeachingPair", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Job id={self.id} title={self.title}>"


class TeamProfile(Base, TimestampMixin):
    __tablename__ = "team_profiles"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)

    team_name = Column(String(255), nullable=True)
    team_mission = Column(Text, nullable=True)
    team_work_style = Column(Text, nullable=True)
    team_communication = Column(Text, nullable=True)
    team_autonomy = Column(Text, nullable=True)
    team_ideal_profile = Column(Text, nullable=True)

    job = relationship("Job", back_populates="team_profile")
    members = relationship("TeamMember", back_populates="team_profile", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<TeamProfile job_id={self.job_id}>"


class TeamMember(Base, TimestampMixin):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_profile_id = Column(Integer, ForeignKey("team_profiles.id", ondelete="CASCADE"), nullable=False)

    role = Column(String(255), nullable=True)
    seniority = Column(String(50), nullable=True)
    work_style = Column(String(255), nullable=True)
    communication_style = Column(String(255), nullable=True)
    values = Column(Text, nullable=True)  # JSON string lista de valores
    collaboration_style = Column(Text, nullable=True)

    team_profile = relationship("TeamProfile", back_populates="members")

    def __repr__(self) -> str:
        return f"<TeamMember id={self.id} team_profile_id={self.team_profile_id}>"


class Application(Base, TimestampMixin):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)

    status = Column(String(50), nullable=False, default="applied")  # applied/shortlisted/rejected/hired/etc.

    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")

    def __repr__(self) -> str:
        return f"<Application candidate_id={self.candidate_id} job_id={self.job_id}>"


class JobRecommendation(Base, TimestampMixin):
    __tablename__ = "job_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)

    scores_json = Column(Text, nullable=True)  # global, skills, values, team_fit
    seen = Column(Integer, nullable=True)      # 0/1
    clicked = Column(Integer, nullable=True)   # 0/1

    candidate = relationship("Candidate", back_populates="recommendations")
    job = relationship("Job", back_populates="recommendations")

    def __repr__(self) -> str:
        return f"<JobRecommendation candidate_id={self.candidate_id} job_id={self.job_id}>"


class CoTeachingPair(Base, TimestampMixin):
    __tablename__ = "co_teaching_pairs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)

    candidate_a_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    candidate_b_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)

    pair_coverage = Column(Integer, nullable=True)
    pair_risk = Column(Integer, nullable=True)
    global_score = Column(Integer, nullable=True)
    complementarities = Column(Text, nullable=True)  # JSON o texto

    job = relationship("Job", back_populates="co_teaching_pairs")
    candidate_a = relationship("Candidate", foreign_keys=[candidate_a_id], back_populates="co_teaching_pairs_a")
    candidate_b = relationship("Candidate", foreign_keys=[candidate_b_id], back_populates="co_teaching_pairs_b")

    def __repr__(self) -> str:
        return f"<CoTeachingPair job_id={self.job_id} a={self.candidate_a_id} b={self.candidate_b_id}>"
