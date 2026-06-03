from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import date


class EquitySnapshotResponse(BaseModel):
    snapshot_date: str
    cohort_size: int
    overall_avg_mastery: Optional[float]
    black_avg_mastery: Optional[float]
    hispanic_avg_mastery: Optional[float]
    white_avg_mastery: Optional[float]
    low_income_avg_mastery: Optional[float]
    iep_avg_mastery: Optional[float]
    ell_avg_mastery: Optional[float]
    achievement_gap_score: float
    at_risk_count: int
    skill_breakdown: Dict
    proficiency_rate: Optional[float]
    alerts: List[Dict]


class AtRiskStudentResponse(BaseModel):
    student_id: str
    avg_mastery: float
    risk_level: str
    recommended_action: str
