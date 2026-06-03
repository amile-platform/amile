"""
Equity Analytics Service
Computes district-level equity dashboards, achievement gap metrics,
and at-risk student identification for policymaker reporting.
"""
from typing import Dict, List, Optional, Tuple
from datetime import date, timedelta
import statistics
import structlog

logger = structlog.get_logger()


class EquityService:
    """
    Core analytics engine for district equity dashboard.
    
    This is the PRIMARY national-importance component of AMILE:
    it translates individual student mastery data into actionable
    district- and state-level equity intelligence.
    """

    # Mastery threshold for "proficient"
    PROFICIENCY_THRESHOLD = 0.70

    # Gap threshold that triggers district alert
    CRITICAL_GAP_THRESHOLD = 0.20

    def compute_school_equity_snapshot(
        self,
        knowledge_states: List[Dict],
        student_profiles: List[Dict],
        snapshot_date: date = None,
    ) -> Dict:
        """
        Compute full equity snapshot for a school.
        
        Args:
            knowledge_states: List of {student_id, skill_id, ensemble_mastery, demographic_group}
            student_profiles:  List of {student_id, demographic_group, grade_level, ...}
            snapshot_date:     Date for this snapshot
        
        Returns:
            Equity snapshot dict matching EquityMetric model
        """
        snapshot_date = snapshot_date or date.today()
        
        if not knowledge_states:
            return self._empty_snapshot(snapshot_date)

        # Aggregate mastery per student
        student_mastery = self._aggregate_student_mastery(knowledge_states)

        # Split by demographic group
        groups = self._split_by_demographic(student_mastery, student_profiles)

        # Compute group averages
        overall_avg = self._group_avg(student_mastery.values())
        black_avg   = self._group_avg(groups.get("black", []))
        hispanic_avg= self._group_avg(groups.get("hispanic", []))
        white_avg   = self._group_avg(groups.get("white", []))
        low_inc_avg = self._group_avg(groups.get("low_income", []))
        iep_avg     = self._group_avg(groups.get("iep", []))
        ell_avg     = self._group_avg(groups.get("ell", []))

        # Achievement gap score: max gap between any underserved group vs highest group
        reference = max(filter(None, [white_avg, overall_avg]), default=overall_avg or 0.5)
        underserved = [x for x in [black_avg, hispanic_avg, low_inc_avg] if x is not None]
        gap_score = reference - min(underserved) if underserved else 0.0

        # At-risk count: students below 40% mastery average
        at_risk = sum(1 for m in student_mastery.values() if m < 0.40)

        # Skill breakdown: average mastery per skill domain
        skill_breakdown = self._compute_skill_breakdown(knowledge_states)

        return {
            "snapshot_date":         snapshot_date.isoformat(),
            "cohort_size":           len(student_mastery),
            "overall_avg_mastery":   overall_avg,
            "black_avg_mastery":     black_avg,
            "hispanic_avg_mastery":  hispanic_avg,
            "white_avg_mastery":     white_avg,
            "low_income_avg_mastery":low_inc_avg,
            "iep_avg_mastery":       iep_avg,
            "ell_avg_mastery":       ell_avg,
            "achievement_gap_score": round(gap_score, 4),
            "at_risk_count":         at_risk,
            "skill_breakdown":       skill_breakdown,
            "proficiency_rate":      self._proficiency_rate(student_mastery.values()),
            "alerts":                self._generate_alerts(gap_score, at_risk, len(student_mastery)),
        }

    def identify_at_risk_students(
        self,
        knowledge_states: List[Dict],
        threshold: float = 0.40,
        min_attempts: int = 3,
    ) -> List[Dict]:
        """
        Identify students at risk of falling behind BEFORE gaps manifest.
        Returns sorted list of at-risk students with intervention recommendations.
        """
        student_data: Dict[str, Dict] = {}
        for ks in knowledge_states:
            sid = str(ks["student_id"])
            if sid not in student_data:
                student_data[sid] = {"masteries": [], "attempts": 0}
            student_data[sid]["masteries"].append(ks["ensemble_mastery"])
            student_data[sid]["attempts"] += ks.get("attempts", 0)

        at_risk = []
        for sid, data in student_data.items():
            if data["attempts"] < min_attempts:
                continue
            avg_mastery = statistics.mean(data["masteries"])
            trajectory  = data.get("gap_trend_30d", 0)
            if avg_mastery < threshold or (avg_mastery < 0.55 and trajectory < -0.05):
                at_risk.append({
                    "student_id":         sid,
                    "avg_mastery":        round(avg_mastery, 3),
                    "risk_level":         "high" if avg_mastery < 0.30 else "medium",
                    "recommended_action": self._recommend_intervention(avg_mastery, trajectory),
                })

        return sorted(at_risk, key=lambda x: x["avg_mastery"])

    def compute_gap_trend(
        self,
        snapshots: List[Dict],
        days: int = 30
    ) -> float:
        """
        Compute trend in achievement gap score over recent snapshots.
        Positive = gap widening (bad). Negative = gap closing (good).
        """
        if len(snapshots) < 2:
            return 0.0
        recent = sorted(snapshots, key=lambda s: s["snapshot_date"])
        recent = [s for s in recent if self._days_ago(s["snapshot_date"]) <= days]
        if len(recent) < 2:
            return 0.0
        gaps = [s["achievement_gap_score"] for s in recent]
        # Linear trend: slope of gap over time
        n = len(gaps)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(gaps)
        num = sum((i - x_mean) * (g - y_mean) for i, g in enumerate(gaps))
        den = sum((i - x_mean) ** 2 for i in range(n))
        return round(num / den, 6) if den > 0 else 0.0

    def _aggregate_student_mastery(self, knowledge_states: List[Dict]) -> Dict[str, float]:
        """Average mastery across all skills per student."""
        student_skills: Dict[str, List[float]] = {}
        for ks in knowledge_states:
            sid = str(ks["student_id"])
            student_skills.setdefault(sid, []).append(ks["ensemble_mastery"])
        return {sid: statistics.mean(masteries) for sid, masteries in student_skills.items()}

    def _split_by_demographic(
        self, student_mastery: Dict, profiles: List[Dict]
    ) -> Dict[str, List[float]]:
        """Group mastery values by demographic category."""
        profile_map = {str(p["student_id"]): p for p in profiles}
        groups: Dict[str, List[float]] = {
            "black": [], "hispanic": [], "white": [], "asian": [],
            "low_income": [], "iep": [], "ell": []
        }
        for sid, mastery in student_mastery.items():
            profile = profile_map.get(sid, {})
            race    = profile.get("race_ethnicity", "").lower()
            if "black" in race or "african" in race:
                groups["black"].append(mastery)
            elif "hispanic" in race or "latino" in race:
                groups["hispanic"].append(mastery)
            elif "white" in race:
                groups["white"].append(mastery)
            elif "asian" in race:
                groups["asian"].append(mastery)
            if profile.get("free_reduced_lunch"):
                groups["low_income"].append(mastery)
            if profile.get("has_iep"):
                groups["iep"].append(mastery)
            if profile.get("is_ell"):
                groups["ell"].append(mastery)
        return groups

    def _group_avg(self, values) -> Optional[float]:
        vals = list(values)
        return round(statistics.mean(vals), 4) if vals else None

    def _proficiency_rate(self, masteries) -> float:
        ms = list(masteries)
        if not ms:
            return 0.0
        return round(sum(1 for m in ms if m >= self.PROFICIENCY_THRESHOLD) / len(ms), 4)

    def _compute_skill_breakdown(self, knowledge_states: List[Dict]) -> Dict:
        """Average mastery per skill domain for drill-down view."""
        skill_masteries: Dict[str, List[float]] = {}
        for ks in knowledge_states:
            domain = ks.get("skill_domain", "unknown")
            skill_masteries.setdefault(domain, []).append(ks["ensemble_mastery"])
        return {
            domain: round(statistics.mean(ms), 4)
            for domain, ms in skill_masteries.items()
        }

    def _generate_alerts(self, gap_score: float, at_risk: int, cohort: int) -> List[Dict]:
        alerts = []
        if gap_score >= self.CRITICAL_GAP_THRESHOLD:
            alerts.append({
                "level":   "critical",
                "message": f"Achievement gap of {gap_score:.0%} exceeds critical threshold. Immediate district review recommended.",
                "action":  "Schedule equity review meeting with district administrators.",
            })
        if cohort > 0 and (at_risk / cohort) > 0.25:
            alerts.append({
                "level":   "warning",
                "message": f"{at_risk} students ({at_risk/cohort:.0%}) are at risk of falling below proficiency.",
                "action":  "Deploy targeted small-group interventions for at-risk cohort.",
            })
        return alerts

    def _recommend_intervention(self, avg_mastery: float, trend: float) -> str:
        if avg_mastery < 0.30:
            return "Immediate one-on-one teacher conference + AI tutor daily sessions"
        if avg_mastery < 0.40:
            return "Small-group intervention 3x/week + project-based module assignment"
        if trend < -0.05:
            return "Monitor closely — declining trajectory. Assign targeted practice module."
        return "Assign adaptive practice module and schedule 1 check-in this week"

    def _empty_snapshot(self, snapshot_date: date) -> Dict:
        return {
            "snapshot_date": snapshot_date.isoformat(),
            "cohort_size": 0, "overall_avg_mastery": None,
            "achievement_gap_score": 0.0, "at_risk_count": 0,
            "skill_breakdown": {}, "alerts": [],
        }

    def _days_ago(self, date_str: str) -> int:
        try:
            d = date.fromisoformat(str(date_str))
            return (date.today() - d).days
        except Exception:
            return 9999
