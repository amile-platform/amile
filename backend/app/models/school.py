"""School and District models"""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class District(Base):
    __tablename__ = "districts"

    id: Mapped[uuid.UUID]       = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str]           = mapped_column(String(255), nullable=False)
    state: Mapped[str]          = mapped_column(String(2), nullable=False)
    nces_id: Mapped[str]        = mapped_column(String(50), nullable=True, unique=True)
    total_students: Mapped[int] = mapped_column(Integer, default=0)
    title_one: Mapped[bool]     = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime]= mapped_column(DateTime, default=datetime.utcnow)

    schools: Mapped[list] = relationship("School", back_populates="district")


class School(Base):
    __tablename__ = "schools"

    id: Mapped[uuid.UUID]          = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    district_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("districts.id"), nullable=False)
    name: Mapped[str]              = mapped_column(String(255), nullable=False)
    state: Mapped[str]             = mapped_column(String(2), nullable=False)
    city: Mapped[str]              = mapped_column(String(100), nullable=False)
    nces_id: Mapped[str]           = mapped_column(String(50), nullable=True, unique=True)
    total_students: Mapped[int]    = mapped_column(Integer, default=0)
    free_lunch_pct: Mapped[float]  = mapped_column(Float, nullable=True)
    title_one: Mapped[bool]        = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime]   = mapped_column(DateTime, default=datetime.utcnow)

    district: Mapped["District"]  = relationship("District", back_populates="schools")
    students: Mapped[list]        = relationship("Student", back_populates="school")
    equity_metrics: Mapped[list]  = relationship("EquityMetric", back_populates="school")
