# backend/server.py — PredictWell API (complete, working)

from typing import Optional
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="PredictWell API", version="1.0.0")

# CORS so the static site can call this backend
# (You can later restrict allow_origins to ["https://predictwellhealth.ai"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Root & Health
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "PredictWell API is running. Visit /docs for Swagger."}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# -----------------------------------------------------------------------------
# Optional: simple risk stub (kept for compatibility/testing)
# -----------------------------------------------------------------------------
class RiskRequest(BaseModel):
    value: Optional[float] = None
    label: Optional[str] = None

class RiskOutput(BaseModel):
    score: int
    band: str

@app.post("/risk", response_model=RiskOutput)
def risk(req: RiskRequest):
    base = int((req.value or 0) % 101)
    band = "Low" if base < 33 else ("Moderate" if base < 66 else "High")
    return RiskOutput(score=base, band=band)

# -----------------------------------------------------------------------------
# Eldercare Check-in (returns id only)
# -----------------------------------------------------------------------------
ELDERCARE_ID = 0

@app.post("/eldercare/checkin")
def eldercare_checkin(payload: dict = Body(...)):
    """
    Accepts any eldercare JSON payload and returns a server id.
    Replace with DB writes if you want persistence.
    """
    global ELDERCARE_ID
    ELDERCARE_ID += 1
    return {"id": ELDERCARE_ID}

# -----------------------------------------------------------------------------
# Athletics Check-in (returns id only)
# -----------------------------------------------------------------------------
class Athlete(BaseModel):
    name: Optional[str] = None
    athlete_id: Optional[str] = None
    age: Optional[int] = Field(None, ge=12, le=60)
    sex: Optional[str] = None
    sport: Optional[str] = None
    position: Optional[str] = None
    team: Optional[str] = None

class Workload(BaseModel):
    rpe: Optional[float] = None
    duration_min: Optional[float] = None
    distance_km: Optional[float] = None
    sprints: Optional[int] = None
    jumps: Optional[int] = None
    strength_sets: Optional[int] = None
    atl: Optional[float] = None
    ctl: Optional[float] = None
    session_load: Optional[float] = None
    acwr: Optional[float] = None

class Wellness(BaseModel):
    sleep_hours: Optional[float] = None
    soreness: Optional[float] = None
    fatigue: Optional[float] = None
    stress: Optional[float] = None
    mood: Optional[float] = None

class Vitals(BaseModel):
    resting_hr: Optional[float] = None
    hrv_rmssd: Optional[float] = None
    spo2: Optional[float] = None

class Health(BaseModel):
    pain_areas: Optional[str] = None
    recent_injury: Optional[str] = None
    recent_illness: Optional[str] = None

class AthleticsCheckin(BaseModel):
    athlete: Optional[Athlete] = None
    workload: Optional[Workload] = None
    wellness: Optional[Wellness] = None
    vitals: Optional[Vitals] = None
    health: Optional[Health] = None
    notes: Optional[str] = None
    timestamp: Optional[str] = None

ATHLETICS_ID = 0

@app.post("/athletics/checkin")
def athletics_checkin(payload: AthleticsCheckin):
    """
    Accepts an athletics check-in payload and returns a server id.
    Replace with DB writes if you want persistence.
    """
    global ATHLETICS_ID
    ATHLETICS_ID += 1
    return {"id": ATHLETICS_ID}

# -----------------------------------------------------------------------------
# Local dev entry (Render runs `python server.py` inside /backend)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import os
    import uvicorn
    # Render provides PORT env var; default for local runs if unset
    port = int(os.environ.get("PORT", "8000"))
    # Because Start Command is `backend/ $ python server.py`, the module path is `server:app`
    uvicorn.run("server:app", host="0.0.0.0", port=port)
