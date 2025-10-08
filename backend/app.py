from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from typing import List

from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, conint, confloat

# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------
app = FastAPI(title="PredictWell API", version="0.1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Database helpers
# -----------------------------------------------------------------------------
DB_PATH = os.environ.get("PREDICTWELL_DB", "predictwell.db")


def init_db() -> None:
    """Create SQLite table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            route TEXT NOT NULL,
            payload TEXT NOT NULL,
            result TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def log_event(route: str, payload: str, result: str) -> None:
    """Log a JSON event for auditing and model training."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO events (ts, route, payload, result) VALUES (?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), route, payload, result),
    )
    conn.commit()
    conn.close()


# -----------------------------------------------------------------------------
# Health endpoints
# -----------------------------------------------------------------------------
@app.get("/")
def root() -> dict:
    return {"ok": True, "service": "PredictWell API", "health": "/healthz"}


@app.get("/healthz")
def healthz() -> dict:
    init_db()
    return {"status": "ok", "db": os.path.abspath(DB_PATH)}


# -----------------------------------------------------------------------------
# Eldercare model
# -----------------------------------------------------------------------------
class EldercareCheckIn(BaseModel):
    """Input schema for the Eldercare fall/cognition MVP."""

    age: conint(ge=50, le=120)
    recent_fall: bool = False
    instability_last_week: conint(ge=0, le=7) = 0
    meds_changed: bool = False
    sleep_quality: conint(ge=1, le=5) = 3
    gait_speed_m_s: confloat(ge=0, le=3) = 1.0
    word_recall_3_item: conint(ge=0, le=3) = 3
    depression_flags: conint(ge=0, le=5) = 0


class RiskResponse(BaseModel):
    """Standard risk-response payload for both AI endpoints."""

    risk_score: confloat(ge=0, le=100)
    risk_level: str
    flags: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)


@app.post("/api/eldercare/risk", response_model=RiskResponse)
def eldercare_risk(inp: EldercareCheckIn = Body(...)) -> RiskResponse:
    """Compute transparent rule-based fall/cognition risk."""
    score = 0.0
    flags: list[str] = []

    # --- rule weights ---
    score += (inp.age - 50) * 0.4  # age → +0.4 per year above 50
    if inp.recent_fall:
        score += 18
        flags.append("Recent fall")
    score += min(inp.instability_last_week * 3.0, 15)
    if inp.meds_changed:
        score += 8
        flags.append("Recent medication change")
    score += max(0, (3 - inp.sleep_quality)) * 2.5
    if inp.gait_speed_m_s < 0.8:
        score += 12
        flags.append("Slow gait (<0.8 m/s)")
    if inp.word_recall_3_item <= 1:
        score += 10
        flags.append("Low word recall")
    score += min(inp.depression_flags * 2.0, 8)

    # --- normalize & assign level ---
    score = round(max(0.0, min(100.0, score)), 1)
    if score >= 70:
        level = "high"
        next_steps = [
            "Notify caregiver today",
            "Schedule balance/gait screening",
            "Review recent medication changes with clinician",
        ]
    elif score >= 40:
        level = "moderate"
        next_steps = [
            "Do 5-minute balance drill (eyes open/closed, sturdy support)",
            "Increase hydration and sleep hygiene this week",
            "Recheck in 48–72 hours",
        ]
    else:
        level = "low"
        next_steps = [
            "Maintain routine activity",
            "Continue weekly check-ins",
            "Report any new dizziness or near-falls",
        ]

    result = RiskResponse(risk_score=score, risk_level=level, flags=flags, next_steps=next_steps)
    log_event("/api/eldercare/risk", inp.model_dump_json(), result.model_dump_json())
    return result


# -----------------------------------------------------------------------------
# Pitcher model
# -----------------------------------------------------------------------------
class PitcherInput(BaseModel):
    """Input schema for workload / mechanics MVP."""

    age: conint(ge=10, le=50)
    level: str = Field(pattern="^(youth|hs|college|pro)$")
    pitches_today: conint(ge=0, le=200)
    pitches_last3d: conint(ge=0, le=400)
    rest_days: conint(ge=0, le=7)
    elbow_pain_0_10: conint(ge=0, le=10) = 0
    shoulder_pain_0_10: conint(ge=0, le=10) = 0
    velo_drop_mph: confloat(ge=-10, le=20) = 0
    mechanics_flags: conint(ge=0, le=5) = 0


LEVEL_CAPS = {
    "youth": {"daily": 75, "rest_ok": 2, "three_day": 120},
    "hs": {"daily": 95, "rest_ok": 1, "three_day": 160},
    "college": {"daily": 110, "rest_ok": 1, "three_day": 220},
    "pro": {"daily": 120, "rest_ok": 1, "three_day": 260},
}


@app.post("/api/athletics/pitcher/risk", response_model=RiskResponse)
def pitcher_risk(inp: PitcherInput = Body(...)) -> RiskResponse:
    """Compute workload/mechanics risk for pitchers."""
    caps = LEVEL_CAPS[inp.level]
    score = 0.0
    flags: list[str] = []

    # workload
    if inp.pitches_today > caps["daily"]:
        over = inp.pitches_today - caps["daily"]
        score += min(25, over * 0.6)
        flags.append("Over daily pitch cap")
    if inp.pitches_last3d > caps["three_day"]:
        over3 = inp.pitches_last3d - caps["three_day"]
        score += min(20, over3 * 0.3)
        flags.append("High 3-day workload")
    if inp.rest_days < caps["rest_ok"]:
        score += 12
        flags.append("Insufficient rest")

    # pain/performance
    pain = max(inp.elbow_pain_0_10, inp.shoulder_pain_0_10)
    score += pain * 3.0
    if pain >= 5:
        flags.append("Pain ≥5/10")
    score += max(0.0, inp.velo_drop_mph) * 1.2

    # mechanics + youth
    score += min(inp.mechanics_flags * 4.0, 16)
    if inp.mechanics_flags >= 3:
        flags.append("Multiple mechanics flags")
    if inp.level == "youth":
        score += 6

    # normalize
    score = round(max(0.0, min(100.0, score)), 1)
    if score >= 70:
        level = "high"
        next_steps = [
            "Stop throwing today; begin recovery work",
            "Coach video review before next outing",
            "If pain persists >48 h, seek evaluation",
        ]
    elif score >= 40:
        level = "moderate"
        next_steps = [
            "Light catch only; no max-effort bullpens",
            "Mobility + cuff/scap stability routine",
            "Reassess in 24–48 h",
        ]
    else:
        level = "low"
        next_steps = [
            "Normal throwing volume",
            "Continue prehab routine",
            "Log workload daily",
        ]

    result = RiskResponse(risk_score=score, risk_level=level, flags=flags, next_steps=next_steps)
    log_event("/api/athletics/pitcher/risk", inp.model_dump_json(), result.model_dump_json())
    return result
