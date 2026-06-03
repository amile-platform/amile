"""User model — base for all platform users"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, DateTime, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class UserRole(str, PyEnum):
    STUDENT  = "student"
    TEACHER  = "teacher"
    ADMIN    = "admin"
    DISTRICT = "district"
    SUPER    = "superadmin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID]         = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str]            = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str]  = mapped_column(String(255), nullable=False)
    first_name: Mapped[str]       = mapped_column(String(100), nullable=False)
    last_name: Mapped[str]        = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole]        = mapped_column(Enum(UserRole), nullable=False)
    is_active: Mapped[bool]       = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool]     = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime]  = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime]  = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login: Mapped[datetime]  = mapped_column(DateTime, nullable=True)

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
