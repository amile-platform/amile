"""KnowledgeState and LearningEvent models — core of DKT/BKT pipeline"""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class KnowledgeState(Base):
    """
    Current estimated mastery of each math skill per student.
    Updated in real-time after every StudentResponse via DKT inference.
    """
    __tablename__ = "knowledge_states"

    id: Mapped[uuid.UUID]          = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"))
    skill_id: Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), ForeignKey("math_skills.id"))
    dkt_mastery: Mapped[float]     = mapped_column(Float, default=0.0)   # 0.0 – 1.0
    bkt_mastery: Mapped[float]     = mapped_column(Float, default=0.0)
    ensemble_mastery: Mapped[float]= mapped_column(Float, default=0.0)   # weighted average
    attempts: Mapped[int]          = mapped_column(Float, default=0)
    correct_attempts: Mapped[int]  = mapped_column(Float, default=0)
    misconceptions: Mapped[dict]   = mapped_column(JSON, default=dict)   # {tag: confidence}
    predicted_mastery_7d: Mapped[float]  = mapped_column(Float, nullable=True)
    predicted_mastery_30d: Mapped[float] = mapped_column(Float, nullable=True)
    updated_at: Mapped[datetime]   = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student: Mapped["Student"]   = relationship("Student", back_populates="knowledge_states")
    skill: Mapped["MathSkill"]   = relationship("MathSkill", back_populates="knowledge_states")


class LearningEvent(Base):
    """
    Immutable log of every interaction — feeds DKT training pipeline.
    Kafka consumer writes here from real-time stream.
    """
    __tablename__ = "learning_events"

    id: Mapped[uuid.UUID]          = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"), index=True)
    skill_id: Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), ForeignKey("math_skills.id"), index=True)
    event_type: Mapped[str]        = mapped_column(String(50), nullable=False)
    correct: Mapped[float]         = mapped_column(Float, nullable=False)  # 0 or 1
    response_time_ms: Mapped[float]= mapped_column(Float, nullable=True)
    hint_requested: Mapped[float]  = mapped_column(Float, default=0)
    context: Mapped[dict]          = mapped_column(JSON, default=dict)
    occurred_at: Mapped[datetime]  = mapped_column(DateTime, default=datetime.utcnow, index=True)
