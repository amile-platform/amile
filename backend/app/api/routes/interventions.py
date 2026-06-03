"""Intervention generation routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.intervention import InterventionRequest, InterventionResponse
from app.services.ai.intervention_generator import InterventionGenerator
from app.models.student import Student, StudentProfile
from sqlalchemy import select
import structlog

logger = structlog.get_logger()
router = APIRouter()
generator = InterventionGenerator()


@router.post("/generate", response_model=InterventionResponse)
async def generate_intervention(payload: InterventionRequest, db: AsyncSession = Depends(get_db)):
    """Generate a personalized AI intervention module for a student."""
    result = await db.execute(
        select(StudentProfile).join(Student, StudentProfile.student_id == Student.id)
        .where(Student.id == payload.student_id)
    )
    profile = result.scalar_one_or_none()
    student_profile = {
        "reading_level_grade": profile.reading_level_grade if profile else payload.grade_level,
        "primary_language":    profile.primary_language if profile else "English",
        "learning_preferences": profile.learning_preferences if profile else {},
    } if profile else {}

    module = generator.generate(
        skill_code=payload.skill_code,
        skill_name=payload.skill_name,
        misconception_tag=payload.misconception_tag,
        student_profile=student_profile,
        grade_level=payload.grade_level,
    )
    return module
