from pydantic import BaseModel
from typing import Optional, Dict
import uuid


class InterventionRequest(BaseModel):
    student_id: uuid.UUID
    skill_code: str
    skill_name: str
    misconception_tag: Optional[str]
    grade_level: int


class InterventionResponse(BaseModel):
    title: str
    skill_code: str
    grade_level: int
    context_story: str
    learning_objectives: list
    steps: list
    reflection_questions: list
    standards_alignment: list
    language: str
    estimated_minutes: int
    generated_by: str
