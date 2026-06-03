"""Assessment, AssessmentItem, and StudentResponse models"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, DateTime, Float, Integer, ForeignKey, JSON, Text, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class ItemType(str, PyEnum):
    MCQ         = "multiple_choice"
    FREE_RESP   = "free_response"
    MULTIMODAL  = "multimodal"
    PROJECT     = "project_based"


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[uuid.UUID]          = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str]             = mapped_column(String(255), nullable=False)
    description: Mapped[str]       = mapped_column(Text, nullable=True)
    grade_level: Mapped[int]       = mapped_column(Integer, nullable=False)
    standard_codes: Mapped[list]   = mapped_column(JSON, default=list)
    created_by: Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_adaptive: Mapped[bool]      = mapped_column(Boolean, default=True)
    time_limit_mins: Mapped[int]   = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime]   = mapped_column(DateTime, default=datetime.utcnow)

    items: Mapped[list]     = relationship("AssessmentItem", back_populates="assessment")
    responses: Mapped[list] = relationship("StudentResponse", back_populates="assessment")


class AssessmentItem(Base):
    __tablename__ = "assessment_items"

    id: Mapped[uuid.UUID]          = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id: Mapped[uuid.UUID]= mapped_column(UUID(as_uuid=True), ForeignKey("assessments.id"))
    skill_id: Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), ForeignKey("math_skills.id"))
    item_type: Mapped[ItemType]    = mapped_column(Enum(ItemType), nullable=False)
    content: Mapped[dict]          = mapped_column(JSON, nullable=False)
    correct_answer: Mapped[dict]   = mapped_column(JSON, nullable=False)
    difficulty: Mapped[float]      = mapped_column(Float, default=0.5)
    discrimination: Mapped[float]  = mapped_column(Float, default=1.0)
    misconception_map: Mapped[dict]= mapped_column(JSON, default=dict)
    order_index: Mapped[int]       = mapped_column(Integer, default=0)

    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="items")
    skill: Mapped["MathSkill"]       = relationship("MathSkill")


class StudentResponse(Base):
    __tablename__ = "student_responses"

    id: Mapped[uuid.UUID]             = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID]     = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"))
    assessment_id: Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), ForeignKey("assessments.id"))
    item_id: Mapped[uuid.UUID]        = mapped_column(UUID(as_uuid=True), ForeignKey("assessment_items.id"))
    skill_id: Mapped[uuid.UUID]       = mapped_column(UUID(as_uuid=True), ForeignKey("math_skills.id"))
    response_data: Mapped[dict]       = mapped_column(JSON, nullable=False)
    is_correct: Mapped[bool]          = mapped_column(Boolean, nullable=False)
    partial_credit: Mapped[float]     = mapped_column(Float, default=0.0)
    time_spent_secs: Mapped[int]      = mapped_column(Integer, default=0)
    hint_count: Mapped[int]           = mapped_column(Integer, default=0)
    misconception_detected: Mapped[str]= mapped_column(String(100), nullable=True)
    dkt_mastery_before: Mapped[float] = mapped_column(Float, nullable=True)
    dkt_mastery_after: Mapped[float]  = mapped_column(Float, nullable=True)
    responded_at: Mapped[datetime]    = mapped_column(DateTime, default=datetime.utcnow)

    student: Mapped["Student"]         = relationship("Student", back_populates="responses")
    assessment: Mapped["Assessment"]   = relationship("Assessment", back_populates="responses")
    item: Mapped["AssessmentItem"]     = relationship("AssessmentItem")
