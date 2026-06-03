"""Student and StudentProfile models"""
import uuid
from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Integer, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base
from enum import Enum as PyEnum


class GradeLevel(str, PyEnum):
    G9 = "9"; G10 = "10"; G11 = "11"; G12 = "12"


class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID]          = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID]     = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    school_id: Mapped[uuid.UUID]   = mapped_column(UUID(as_uuid=True), ForeignKey("schools.id"), nullable=False)
    student_id_local: Mapped[str]  = mapped_column(String(50), nullable=True)
    grade_level: Mapped[GradeLevel]= mapped_column(Enum(GradeLevel), nullable=False)
    date_enrolled: Mapped[date]    = mapped_column(Date, default=date.today)

    profile: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="student", uselist=False)
    knowledge_states: Mapped[list]    = relationship("KnowledgeState", back_populates="student")
    responses: Mapped[list]           = relationship("StudentResponse", back_populates="student")


class StudentProfile(Base):
    """Extended FERPA-protected student profile for adaptive learning"""
    __tablename__ = "student_profiles"

    id: Mapped[uuid.UUID]              = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    reading_level_grade: Mapped[float] = mapped_column(Float, nullable=True)
    primary_language: Mapped[str]      = mapped_column(String(50), default="English")
    learning_preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    iep_accommodations: Mapped[dict]   = mapped_column(JSON, default=dict)
    socioeconomic_tier: Mapped[int]    = mapped_column(Integer, nullable=True)
    prior_math_score: Mapped[float]    = mapped_column(Float, nullable=True)
    updated_at: Mapped[datetime]       = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student: Mapped["Student"] = relationship("Student", back_populates="profile")
