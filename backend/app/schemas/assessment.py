from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid


class AssessmentCreate(BaseModel):
    title: str
    description: Optional[str]
    grade_level: int
    standard_codes: List[str]
    is_adaptive: bool = True
    time_limit_mins: Optional[int]


class AssessmentResponse(BaseModel):
    id: uuid.UUID
    title: str
    grade_level: int
    is_adaptive: bool
    class Config:
        from_attributes = True


class SubmitResponseRequest(BaseModel):
    student_id: uuid.UUID
    assessment_id: uuid.UUID
    item_id: uuid.UUID
    skill_id: uuid.UUID
    response_data: Dict
    time_spent_secs: int
    hint_count: int = 0
