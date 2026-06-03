"""Intervention models — AI-generated and teacher-assigned"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, DateTime, Float, ForeignKey, JSON, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class InterventionType(str, PyEnum):
    PROJECT_MODULE   = "project_based_module"
    SMALL_GROUP      = "small_group_instruction"
    AI_TUTOR_SESSION = "ai_tutor_session"
    PEER_COLLABORATION = "peer_collaboration"
    TEACHER_CONFERENCE = "teacher_conference"


class Intervention(Base):
    __tablename__ = "interventions"

    id: Mapped[uuid.UUID]             = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str]                = mapped_column(String(255), nullable=False)
    intervention_type: Mapped[InterventionType] = mapped_column(Enum(InterventionType))
    target_skills: Mapped[list]       = mapped_column(JSON, default=list)
    target_misconceptions: Mapped[list]= mapped_column(JSON, default=list)
    content: Mapped[dict]             = mapped_column(JSON, nullable=False)
    cultural_context: Mapped[str]     = mapped_column(String(100), nullable=True)
    language: Mapped[str]             = mapped_column(String(20), default="en")
    reading_level: Mapped[float]      = mapped_column(Float, nullable=True)
    generated_by_ai: Mapped[bool]     = mapped_column(Float, default=True)
    llm_prompt_used: Mapped[str]      = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow)

    assignments: Mapped[list] = relationship("InterventionAssignment", back_populates="intervention")


class InterventionAssignment(Base):
    __tablename__ = "intervention_assignments"

    id: Mapped[uuid.UUID]               = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    intervention_id: Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), ForeignKey("interventions.id"))
    student_id: Mapped[uuid.UUID]       = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"))
    assigned_by: Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    status: Mapped[str]                 = mapped_column(String(30), default="assigned")
    mastery_before: Mapped[float]       = mapped_column(Float, nullable=True)
    mastery_after: Mapped[float]        = mapped_column(Float, nullable=True)
    assigned_at: Mapped[datetime]       = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime]      = mapped_column(DateTime, nullable=True)

    intervention: Mapped["Intervention"] = relationship("Intervention", back_populates="assignments")
