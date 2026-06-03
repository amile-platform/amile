"""
AMILE MVP — Standalone runnable prototype
Self-contained FastAPI app with in-memory data store.
No database required — demonstrates core DKT + equity dashboard.

Run: uvicorn app.main:app --reload --port 8000
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import numpy as np
import uuid
from datetime import datetime, date
import statistics

app = FastAPI(
    title="AMILE MVP",
    description="Adaptive Mathematics Intelligence & Learning Ecosystem — MVP Demo",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory data store ──────────────────────────────────────────────────────
STUDENTS: Dict[str, dict] = {}
KNOWLEDGE_STATES: Dict[str, Dict[str, float]] = {}   # {student_id: {skill_code: mastery}}
INTERACTIONS: Dict[str, List[dict]] = {}              # {student_id: [events]}

# ── Seed skills (Common Core aligned) ────────────────────────────────────────
MATH_SKILLS = {
    "CC.6.EE.1": {"name": "Exponent Expressions",       "grade": 6, "difficulty": 0.45},
    "CC.7.NS.1": {"name": "Rational Number Operations",  "grade": 7, "difficulty": 0.55},
    "CC.7.RP.1": {"name": "Unit Rates & Proportions",   "grade": 7, "difficulty": 0.40},
    "CC.8.EE.7": {"name": "Linear Equations",           "grade": 8, "difficulty": 0.60},
    "CC.8.F.1":  {"name": "Functions & Relations",      "grade": 8, "difficulty": 0.55},
    "CC.HSA.1":  {"name": "Polynomial Operations",      "grade": 9, "difficulty": 0.65},
    "CC.HSA.2":  {"name": "Solving Quadratics",         "grade": 10,"difficulty": 0.72},
    "CC.HSF.1":  {"name": "Linear Functions & Slope",   "grade": 9, "difficulty": 0.50},
    "CC.HSF.2":  {"name": "Exponential Functions",      "grade": 10,"difficulty": 0.68},
    "CC.HSS.1":  {"name": "Statistical Analysis",       "grade": 11,"difficulty": 0.60},
}

# ── Seed demo school data ─────────────────────────────────────────────────────
DEMO_SCHOOLS = {
    "school_001": {"name": "Unity Academy", "city": "Columbus, OH", "title_one": True},
    "school_002": {"name": "Lincoln STEM HS", "city": "Cleveland, OH", "title_one": True},
}

DEMO_STUDENTS = []
for i in range(30):
    sid = f"student_{i:03d}"
    STUDENTS[sid] = {
        "id": sid,
        "name": f"Student {i+1}",
        "grade": 9 + (i % 4),
        "school_id": "school_001" if i < 20 else "school_002",
        "demographic": ["black", "hispanic", "white", "asian"][i % 4],
        "low_income": i % 3 != 0,
    }
    # Initialize knowledge states with realistic distributions
    KNOWLEDGE_STATES[sid] = {
        code: float(np.clip(np.random.beta(
            2 if STUDENTS[sid]["demographic"] in ["black","hispanic"] else 3,
            4 if STUDENTS[sid]["demographic"] in ["black","hispanic"] else 3
        ), 0.05, 0.95))
        for code in MATH_SKILLS
    }
    DEMO_STUDENTS.append(sid)


# ── Schemas ───────────────────────────────────────────────────────────────────
class SubmitAnswerRequest(BaseModel):
    student_id: str
    skill_code: str
    is_correct: bool
    response_time_secs: int = 30
    hint_used: bool = False


class StudentCreate(BaseModel):
    name: str
    grade: int
    school_id: str = "school_001"
    demographic: str = "unspecified"
    low_income: bool = False


# ── DKT heuristic (no TF dependency for MVP) ─────────────────────────────────
def dkt_update(current: float, is_correct: bool, difficulty: float) -> float:
    alpha = 0.3
    learn = 0.18 if is_correct else -0.10
    adjust = (1 - difficulty) * 0.05 if is_correct else 0
    new = current + learn + adjust
    # Apply exponential smoothing
    new = alpha * new + (1 - alpha) * current
    return float(np.clip(new + learn * 0.5, 0.01, 0.99))


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "healthy", "platform": "AMILE MVP", "version": "0.1.0"}


@app.get("/skills")
def list_skills():
    return {"skills": [{"code": k, **v} for k, v in MATH_SKILLS.items()]}


@app.post("/students")
def create_student(payload: StudentCreate):
    sid = f"student_{uuid.uuid4().hex[:6]}"
    STUDENTS[sid] = {"id": sid, **payload.model_dump()}
    KNOWLEDGE_STATES[sid] = {code: 0.15 for code in MATH_SKILLS}
    INTERACTIONS[sid] = []
    return {"student_id": sid, "message": "Student created"}


@app.get("/students/{student_id}/knowledge-map")
def get_knowledge_map(student_id: str):
    if student_id not in KNOWLEDGE_STATES:
        raise HTTPException(404, "Student not found")
    return {
        "student_id": student_id,
        "knowledge_map": [
            {
                "skill_code":  code,
                "skill_name":  MATH_SKILLS[code]["name"],
                "grade":       MATH_SKILLS[code]["grade"],
                "mastery":     round(mastery, 3),
                "proficient":  mastery >= 0.70,
                "status": "mastered" if mastery >= 0.85 else ("proficient" if mastery >= 0.70 else ("developing" if mastery >= 0.40 else "at_risk")),
            }
            for code, mastery in KNOWLEDGE_STATES[student_id].items()
        ],
        "overall_mastery": round(statistics.mean(KNOWLEDGE_STATES[student_id].values()), 3),
    }


@app.post("/submit-answer")
def submit_answer(payload: SubmitAnswerRequest):
    if payload.student_id not in KNOWLEDGE_STATES:
        raise HTTPException(404, "Student not found")
    if payload.skill_code not in MATH_SKILLS:
        raise HTTPException(404, "Skill not found")

    skill     = MATH_SKILLS[payload.skill_code]
    current   = KNOWLEDGE_STATES[payload.student_id][payload.skill_code]
    new       = dkt_update(current, payload.is_correct, skill["difficulty"])

    KNOWLEDGE_STATES[payload.student_id][payload.skill_code] = new
    INTERACTIONS.setdefault(payload.student_id, []).append({
        "skill_code": payload.skill_code,
        "is_correct": payload.is_correct,
        "mastery_after": new,
        "timestamp": datetime.utcnow().isoformat(),
    })

    misconception = None
    if not payload.is_correct and payload.skill_code in ["CC.8.EE.7", "CC.HSA.1"]:
        misconception = {
            "tag": "variable_isolation_sign_error",
            "description": "Possible sign error when moving terms across the equals sign.",
            "teacher_alert": "3+ students show this pattern — small-group intervention recommended.",
        }

    return {
        "is_correct":     payload.is_correct,
        "mastery_before": round(current, 3),
        "mastery_after":  round(new, 3),
        "skill_name":     skill["name"],
        "misconception":  misconception,
        "encouragement":  "Great work!" if payload.is_correct else "Keep going — every attempt counts!",
    }


@app.get("/schools/{school_id}/equity-dashboard")
def get_equity_dashboard(school_id: str):
    if school_id not in DEMO_SCHOOLS:
        raise HTTPException(404, "School not found")

    school_students = [
        (sid, STUDENTS[sid]) for sid in STUDENTS
        if STUDENTS[sid].get("school_id") == school_id
    ]
    if not school_students:
        raise HTTPException(404, "No students found for school")

    groups: Dict[str, List[float]] = {"black": [], "hispanic": [], "white": [], "asian": [], "low_income": []}
    all_masteries = []

    for sid, profile in school_students:
        avg = statistics.mean(KNOWLEDGE_STATES[sid].values())
        all_masteries.append(avg)
        demo = profile.get("demographic", "")
        if demo in groups:
            groups[demo].append(avg)
        if profile.get("low_income"):
            groups["low_income"].append(avg)

    def avg(lst): return round(statistics.mean(lst), 3) if lst else None

    overall     = avg(all_masteries)
    black_avg   = avg(groups["black"])
    hisp_avg    = avg(groups["hispanic"])
    white_avg   = avg(groups["white"])
    low_inc_avg = avg(groups["low_income"])

    reference   = max(filter(None, [white_avg, overall or 0.5]), default=0.5)
    underserved = [x for x in [black_avg, hisp_avg, low_inc_avg] if x]
    gap         = round(reference - min(underserved), 3) if underserved else 0.0
    at_risk     = sum(1 for m in all_masteries if m < 0.40)
    proficiency = round(sum(1 for m in all_masteries if m >= 0.70) / len(all_masteries), 3)

    alerts = []
    if gap >= 0.20:
        alerts.append({"level": "critical", "message": f"Achievement gap of {gap:.0%} requires immediate attention."})
    if at_risk > 0:
        alerts.append({"level": "warning", "message": f"{at_risk} students at risk of falling below proficiency."})

    skill_breakdown = {}
    for code, skill in MATH_SKILLS.items():
        masteries = [KNOWLEDGE_STATES[sid][code] for sid, _ in school_students]
        skill_breakdown[code] = {"skill_name": skill["name"], "avg_mastery": round(statistics.mean(masteries), 3)}

    return {
        "school_id":         school_id,
        "school_name":       DEMO_SCHOOLS[school_id]["name"],
        "snapshot_date":     date.today().isoformat(),
        "cohort_size":       len(school_students),
        "overall_avg":       overall,
        "proficiency_rate":  proficiency,
        "by_demographic": {
            "black":      black_avg,
            "hispanic":   hisp_avg,
            "white":      white_avg,
            "asian":      avg(groups["asian"]),
            "low_income": low_inc_avg,
        },
        "achievement_gap_score": gap,
        "at_risk_count":   at_risk,
        "skill_breakdown": skill_breakdown,
        "alerts":          alerts,
    }


@app.get("/schools/{school_id}/at-risk")
def get_at_risk(school_id: str):
    school_students = [(sid, STUDENTS[sid]) for sid in STUDENTS if STUDENTS[sid].get("school_id") == school_id]
    at_risk = []
    for sid, profile in school_students:
        avg = statistics.mean(KNOWLEDGE_STATES[sid].values())
        if avg < 0.45:
            at_risk.append({
                "student_id":   sid,
                "name":         profile["name"],
                "avg_mastery":  round(avg, 3),
                "risk_level":   "high" if avg < 0.30 else "medium",
                "recommendation": "Assign AI tutor sessions daily + notify teacher" if avg < 0.30 else "Weekly check-in + adaptive module",
                "weakest_skills": sorted(
                    [{"skill": MATH_SKILLS[c]["name"], "mastery": round(m, 3)}
                     for c, m in KNOWLEDGE_STATES[sid].items()],
                    key=lambda x: x["mastery"]
                )[:3],
            })
    return {"school_id": school_id, "at_risk_students": sorted(at_risk, key=lambda x: x["avg_mastery"])}


@app.get("/demo/stats")
def demo_stats():
    all_m = [statistics.mean(KNOWLEDGE_STATES[sid].values()) for sid in STUDENTS]
    return {
        "total_students": len(STUDENTS),
        "total_schools":  len(DEMO_SCHOOLS),
        "total_skills":   len(MATH_SKILLS),
        "avg_mastery":    round(statistics.mean(all_m), 3),
        "proficiency_rate": round(sum(1 for m in all_m if m >= 0.7) / len(all_m), 3),
        "at_risk_count":  sum(1 for m in all_m if m < 0.4),
    }
