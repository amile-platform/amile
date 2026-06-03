"""Analytics routes — equity dashboard, at-risk, district reporting"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.db.session import get_db
from app.schemas.analytics import EquitySnapshotResponse, AtRiskStudentResponse
from app.services.analytics.equity_service import EquityService
from app.models.knowledge_state import KnowledgeState
from app.models.equity import EquityMetric
from typing import List
import structlog

logger = structlog.get_logger()
router = APIRouter()
equity_service = EquityService()


@router.get("/school/{school_id}/equity-snapshot", response_model=EquitySnapshotResponse)
async def get_equity_snapshot(school_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Generate real-time equity snapshot for a school.
    Powers the district equity dashboard.
    """
    from app.models.student import Student, StudentProfile
    
    # Get all knowledge states for students in this school
    result = await db.execute(
        select(KnowledgeState, StudentProfile)
        .join(Student, KnowledgeState.student_id == Student.id)
        .join(StudentProfile, Student.id == StudentProfile.student_id)
        .where(Student.school_id == school_id)
    )
    rows = result.all()

    knowledge_states = [
        {
            "student_id": str(ks.student_id),
            "skill_id": str(ks.skill_id),
            "ensemble_mastery": ks.ensemble_mastery,
            "attempts": ks.attempts,
        }
        for ks, _ in rows
    ]
    student_profiles = [
        {
            "student_id": str(profile.student_id),
            "free_reduced_lunch": profile.socioeconomic_tier is not None and profile.socioeconomic_tier <= 2,
            "has_iep": bool(profile.iep_accommodations),
            "is_ell": profile.primary_language != "English",
        }
        for _, profile in rows
    ]

    return equity_service.compute_school_equity_snapshot(knowledge_states, student_profiles)


@router.get("/school/{school_id}/at-risk", response_model=List[AtRiskStudentResponse])
async def get_at_risk_students(school_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Identify at-risk students before gaps manifest — proactive intervention."""
    from app.models.student import Student
    result = await db.execute(
        select(KnowledgeState)
        .join(Student, KnowledgeState.student_id == Student.id)
        .where(Student.school_id == school_id)
    )
    knowledge_states = [
        {"student_id": str(ks.student_id), "ensemble_mastery": ks.ensemble_mastery, "attempts": ks.attempts}
        for ks in result.scalars().all()
    ]
    return equity_service.identify_at_risk_students(knowledge_states)


@router.get("/district/{district_id}/summary")
async def get_district_summary(district_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """District-level summary for policymaker dashboard."""
    from app.models.school import School
    result = await db.execute(select(School).where(School.district_id == district_id))
    schools = result.scalars().all()
    return {
        "district_id": str(district_id),
        "school_count": len(schools),
        "schools": [{"id": str(s.id), "name": s.name, "city": s.city} for s in schools],
        "message": "Drill into individual school endpoints for equity snapshots.",
    }
