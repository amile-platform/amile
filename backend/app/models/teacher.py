"""Teacher model"""
import uuid
from datetime import date
from sqlalchemy import String, Date, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[uuid.UUID]         = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    school_id: Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), ForeignKey("schools.id"))
    employee_id: Mapped[str]      = mapped_column(String(50), nullable=True)
    subjects: Mapped[list]        = mapped_column(JSON, default=list)
    grade_levels: Mapped[list]    = mapped_column(JSON, default=list)
    date_joined: Mapped[date]     = mapped_column(Date, default=date.today)
