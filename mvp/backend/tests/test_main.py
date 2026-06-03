"""MVP API tests"""
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_skills():
    r = client.get("/skills")
    assert r.status_code == 200
    assert len(r.json()["skills"]) > 0

def test_equity_dashboard():
    r = client.get("/schools/school_001/equity-dashboard")
    assert r.status_code == 200
    data = r.json()
    assert "achievement_gap_score" in data
    assert "at_risk_count" in data

def test_at_risk():
    r = client.get("/schools/school_001/at-risk")
    assert r.status_code == 200

def test_submit_answer():
    r = client.post("/submit-answer", json={
        "student_id": "student_000",
        "skill_code": "CC.8.EE.7",
        "is_correct": True,
        "response_time_secs": 25,
        "hint_used": False
    })
    assert r.status_code == 200
    assert "mastery_after" in r.json()

def test_demo_stats():
    r = client.get("/demo/stats")
    assert r.status_code == 200
    assert r.json()["total_students"] > 0
