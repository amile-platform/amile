from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
import uuid


class StudentCreate(BaseModel):
    user_id: uuid.UUID
    school_id: uuid.UUID
    grade_level: str
    student_id_local: Optional[str] = None


class StudentResponse(BaseModel):
    id: uuid.UUID
    grade_level: str
    school_id: uuid.UUID
    class Config:
        from_attributes = True


class KnowledgeStateResponse(BaseModel):
    skill_id: uuid.UUID
    skill_code: str
    skill_name: str
    dkt_mastery: float
    bkt_mastery: float
    ensemble_mastery: float
    attempts: int
    misconceptions: Dict
    predicted_mastery_7d: Optional[float]
    predicted_mastery_30d: Optional[float]
    updated_at: datetime
    class Config:
        from_attributes = True
