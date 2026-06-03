"""EquityMetric model — district-level equity dashboard data"""
import uuid
from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Float, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class EquityMetric(Base):
    """
    Aggregated equity metrics per school per snapshot period.
    Powers the district equity dashboard — the primary national-importance output.
    """
    __tablename__ = "equity_metrics"

    id: Mapped[uuid.UUID]           = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    school_id: Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), ForeignKey("schools.id"))
    snapshot_date: Mapped[date]     = mapped_column(Date, nullable=False, index=True)
    grade_level: Mapped[int]        = mapped_column(Integer, nullable=True)
    cohort_size: Mapped[int]        = mapped_column(Integer, nullable=False)

    # Mastery by demographic
    overall_avg_mastery: Mapped[float]      = mapped_column(Float, nullable=True)
    black_avg_mastery: Mapped[float]        = mapped_column(Float, nullable=True)
    hispanic_avg_mastery: Mapped[float]     = mapped_column(Float, nullable=True)
    white_avg_mastery: Mapped[float]        = mapped_column(Float, nullable=True)
    low_income_avg_mastery: Mapped[float]   = mapped_column(Float, nullable=True)
    iep_avg_mastery: Mapped[float]          = mapped_column(Float, nullable=True)
    ell_avg_mastery: Mapped[float]          = mapped_column(Float, nullable=True)

    # Gap metrics
    achievement_gap_score: Mapped[float]    = mapped_column(Float, nullable=True)
    gap_trend_30d: Mapped[float]            = mapped_column(Float, nullable=True)
    gap_trend_90d: Mapped[float]            = mapped_column(Float, nullable=True)
    predicted_gap_90d: Mapped[float]        = mapped_column(Float, nullable=True)

    # At-risk signals
    at_risk_count: Mapped[int]              = mapped_column(Integer, default=0)
    intervention_rate: Mapped[float]        = mapped_column(Float, nullable=True)
    skill_breakdown: Mapped[dict]           = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime]            = mapped_column(DateTime, default=datetime.utcnow)

    school: Mapped["School"] = relationship("School", back_populates="equity_metrics")
