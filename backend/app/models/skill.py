"""Math skill taxonomy — Common Core + TEKS aligned"""
import uuid
from sqlalchemy import String, Integer, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class SkillDomain(Base):
    __tablename__ = "skill_domains"

    id: Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str]          = mapped_column(String(100), nullable=False)
    grade_band: Mapped[str]    = mapped_column(String(20), nullable=False)
    standard: Mapped[str]      = mapped_column(String(20), default="CCSS")
    description: Mapped[str]   = mapped_column(Text, nullable=True)

    skills: Mapped[list] = relationship("MathSkill", back_populates="domain")


class MathSkill(Base):
    __tablename__ = "math_skills"

    id: Mapped[uuid.UUID]          = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id: Mapped[uuid.UUID]   = mapped_column(UUID(as_uuid=True), ForeignKey("skill_domains.id"))
    parent_skill_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("math_skills.id"), nullable=True)
    code: Mapped[str]              = mapped_column(String(30), unique=True, nullable=False)
    name: Mapped[str]              = mapped_column(String(200), nullable=False)
    description: Mapped[str]       = mapped_column(Text, nullable=True)
    grade_level: Mapped[int]       = mapped_column(Integer, nullable=False)
    difficulty_weight: Mapped[int] = mapped_column(Integer, default=1)
    prerequisite_codes: Mapped[list]= mapped_column(JSON, default=list)
    misconception_tags: Mapped[list]= mapped_column(JSON, default=list)

    domain: Mapped["SkillDomain"]      = relationship("SkillDomain", back_populates="skills")
    sub_skills: Mapped[list]           = relationship("MathSkill", remote_side=[id])
    knowledge_states: Mapped[list]     = relationship("KnowledgeState", back_populates="skill")
