"""Knowledge Tracing routes — DKT/BKT mastery endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.db.session import get_db
from app.schemas.student import KnowledgeStateResponse
from app.schemas.assessment import SubmitResponseRequest
from app.services.ai.dkt_service import DKTService
from app.services.ai.bkt_service import BKTService
from app.services.ai.misconception_detector import MisconceptionDetector
from app.models.knowledge_state import KnowledgeState, LearningEvent
from app.models.assessment import StudentResponse, AssessmentItem
import structlog

logger = structlog.get_logger()
router = APIRouter()

dkt_service  = DKTService()
bkt_service  = BKTService()
misconception_detector = MisconceptionDetector()


@router.post("/submit-response")
async def submit_response(
    payload: SubmitResponseRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Core endpoint: process a student's response.
    1. Scores the response
    2. Detects misconceptions
    3. Updates DKT + BKT knowledge state
    4. Emits LearningEvent for Kafka stream
    5. Returns updated mastery + any misconception alert
    """
    # Fetch assessment item
    item_result = await db.execute(
        select(AssessmentItem).where(AssessmentItem.id == payload.item_id)
    )
    item = item_result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Assessment item not found")

    # Score the response
    is_correct = payload.response_data.get("answer") == item.correct_answer.get("value")

    # Detect misconception
    misconception_tag, confidence = misconception_detector.detect_from_response(
        item_content=item.content,
        student_answer=payload.response_data,
        correct_answer=item.correct_answer,
        skill_code=str(payload.skill_id),
    )

    # Get or create knowledge state
    ks_result = await db.execute(
        select(KnowledgeState).where(
            KnowledgeState.student_id == payload.student_id,
            KnowledgeState.skill_id == payload.skill_id,
        )
    )
    ks = ks_result.scalar_one_or_none()
    if not ks:
        ks = KnowledgeState(student_id=payload.student_id, skill_id=payload.skill_id)
        db.add(ks)

    # Update DKT mastery
    new_dkt, dkt_delta = dkt_service.update_after_response(
        ks.dkt_mastery, is_correct, item.difficulty
    )
    # Update BKT mastery
    new_bkt, _ = bkt_service.update(
        ks.bkt_mastery, is_correct, str(payload.skill_id), item.difficulty
    )

    # Ensemble: 60% DKT + 40% BKT
    new_ensemble = 0.6 * new_dkt + 0.4 * new_bkt

    ks.dkt_mastery      = new_dkt
    ks.bkt_mastery      = new_bkt
    ks.ensemble_mastery = new_ensemble
    ks.attempts         = (ks.attempts or 0) + 1
    if is_correct:
        ks.correct_attempts = (ks.correct_attempts or 0) + 1
    if misconception_tag:
        misconceptions = dict(ks.misconceptions or {})
        misconceptions[misconception_tag] = round(confidence, 3)
        ks.misconceptions = misconceptions

    # Save student response
    response = StudentResponse(
        student_id=payload.student_id,
        assessment_id=payload.assessment_id,
        item_id=payload.item_id,
        skill_id=payload.skill_id,
        response_data=payload.response_data,
        is_correct=is_correct,
        time_spent_secs=payload.time_spent_secs,
        hint_count=payload.hint_count,
        misconception_detected=misconception_tag,
        dkt_mastery_before=ks.dkt_mastery,
        dkt_mastery_after=new_dkt,
    )
    db.add(response)

    # Log learning event
    event = LearningEvent(
        student_id=payload.student_id,
        skill_id=payload.skill_id,
        event_type="assessment_response",
        correct=1.0 if is_correct else 0.0,
        response_time_ms=payload.time_spent_secs * 1000,
        hint_requested=float(payload.hint_count > 0),
        context={"assessment_id": str(payload.assessment_id), "item_type": item.item_type.value},
    )
    db.add(event)
    await db.flush()

    return {
        "is_correct":          is_correct,
        "mastery_before":      round(ks.dkt_mastery, 3),
        "mastery_after":       round(new_ensemble, 3),
        "mastery_delta":       round(dkt_delta, 3),
        "misconception":       misconception_detector.get_explanation(misconception_tag) if misconception_tag else None,
        "encouragement":       _encouragement_message(new_ensemble, is_correct),
    }


@router.get("/student/{student_id}/knowledge-map", response_model=List[KnowledgeStateResponse])
async def get_knowledge_map(student_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Return full knowledge state map for a student — powers student dashboard."""
    from app.models.skill import MathSkill
    result = await db.execute(
        select(KnowledgeState, MathSkill)
        .join(MathSkill, KnowledgeState.skill_id == MathSkill.id)
        .where(KnowledgeState.student_id == student_id)
        .order_by(MathSkill.grade_level, MathSkill.name)
    )
    rows = result.all()
    return [
        {
            **{k: v for k, v in vars(ks).items() if not k.startswith("_")},
            "skill_code": skill.code,
            "skill_name": skill.name,
        }
        for ks, skill in rows
    ]


def _encouragement_message(mastery: float, is_correct: bool) -> str:
    if is_correct and mastery >= 0.80:
        return "Excellent! You've mastered this skill. Ready for the next challenge!"
    if is_correct:
        return "Great work! Keep practicing to build your mastery."
    if mastery >= 0.50:
        return "You're making progress! Review the hint and try the next one."
    return "Don't give up — every attempt builds your understanding. Use the hint!"
