# backend/server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import sqlite3
import os

# ----- Schemas -----
class PitchRiskInput(BaseModel):
    pitch_count: int = Field(ge=0)
    days_rest: int = Field(ge=0)
    pain_level: int = Field(ge=0, le=10)
    session_intensity: int = Field(ge=1, le=10)
    previous_injury: bool = False

class EldercareRiskInput(BaseModel):
    age: int = Field(ge=0)
    falls_last_6mo: int = Field(ge=0)
    dizziness: int = Field(ge=0, le=10)
    steps: int = Field(ge=0)
    sleep_hours: float = Field(ge=0)
    hydration_cups: int = Field(ge=0)
    meds_changed: bool = False

class RiskOutput(BaseModel):
    risk_score: float
    risk_band: str
    factors: List[str]

class EldercareCheckinIn(BaseModel):
    patient_id: Optional[int] = None
    sleep_hours: Optional[float] = None
    hydration_cups: Optional[int] = None
    steps: Optional[int] = None
    dizziness: Optional[int] = None
    mood: Optional[int] = None
    notes: Optional[str] = None

class RiskRequest(BaseModel):
    pitch: Optional[PitchRiskInput] = None
    elder: Optional[EldercareRiskInput] = None

# ----- App -----
app = FastAPI(title="PredictWell API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- SQLite (simple) -----
DB_PATH = os.path.join(os.path.dirname(__file__), "predictwell.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS eldercare_checkins(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            sleep_hours REAL,
            hydration_cups INTEGER,
            steps INTEGER,
            dizziness INTEGER,
            mood INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    conn.close()

init_db()

# ----- Risk helpers -----
def _band(score: float) -> str:
    if score < 0.33:
        return "Low"
    if score < 0.66:
        return "Moderate"
    return "High"

def compute_pitch_score(p: PitchRiskInput, factors: List[str]) -> float:
    s = 0.0
    s += min(p.pitch_count / 100, 1.0) * 0.25
    s += min(p.session_intensity / 10, 1.0) * 0.20
    s += min(p.pain_level / 10, 1.0) * 0.25
    s += (0 if p.days_rest >= 2 else 0.15)
    s += (0.15 if p.previous_injury else 0.0)

    if p.pitch_count > 85:
        factors.append("High pitch count")
    if p.days_rest < 2:
        factors.append("Low rest")
    if p.pain_level >= 4:
        factors.append("Reported pain")
    if p.previous_injury:
        factors.append("History of injury")
    if p.session_intensity >= 8:
        factors.append("High session intensity")
    return s

def compute_elder_score(e: EldercareRiskInput, factors: List[str]) -> float:
    s = 0.0
    s += min(e.age / 100, 1.0) * 0.10
    s += min(e.falls_last_6mo / 3, 1.0) * 0.25
    s += min(e.dizziness / 10, 1.0) * 0.20
    s += (0.15 if e.meds_changed else 0.0)
    s += (0.10 if e.steps < 3000 else 0.0)
    s += (0.10 if e.sleep_hours < 6 else 0.0)
    s += (0.10 if e.hydration_cups < 6 else 0.0)

    if e.falls_last_6mo >= 1:
        factors.append("Recent falls")
    if e.dizziness >= 4:
        factors.append("Dizziness")
    if e.meds_changed:
        factors.append("Medication change")
    if e.steps < 3000:
        factors.append("Low activity")
    if e.sleep_hours < 6:
        factors.append("Low sleep")
    if e.hydration_cups < 6:
        factors.append("Low hydration")
    return s

# ----- Routes -----
@app.get("/")
def root():
    return {"message": "PredictWell API is running. Visit /docs for Swagger."}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/risk", response_model=RiskOutput)
def risk(req: RiskRequest):
    score: float = 0.0
    factors: List[str] = []
    if req.pitch:
        score += compute_pitch_score(req.pitch, factors)
    if req.elder:
        score += compute_elder_score(req.elder, factors)
    score = max(0.0, min(score, 1.0))
    return {"risk_score": round(score, 3), "risk_band": _band(score), "factors": factors}

@app.post("/eldercare/checkin")
def eldercare_checkin(payload: EldercareCheckinIn):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO eldercare_checkins
        (patient_id, sleep_hours, hydration_cups, steps, dizziness, mood, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.patient_id,
            payload.sleep_hours,
            payload.hydration_cups,
            payload.steps,
            payload.dizziness,
            payload.mood,
            payload.notes,
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return {"id": new_id}

# ----- Direct start for Render -----
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
