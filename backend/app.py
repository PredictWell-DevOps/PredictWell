from fastapi import FastAPI
from datetime import datetime

# Use the helpers that exist in your current SQLite db.py
from backend.db import init_db, DB_PATH
from backend.schemas import PatientCreate, PatientOut

# AI module (already added)
from backend.ai_module import RiskInput, RiskOutput, compute_risk

app = FastAPI(title="PredictWell Health.ai API", version="1.0")

# -----------------------------------------------------
# Init DB at startup (creates tables if missing)
# -----------------------------------------------------
@app.on_event("startup")
def _startup():
    init_db()

# -----------------------------------------------------
# Health Check
# -----------------------------------------------------
@app.get("/healthz")
def health_check():
    """Basic health check endpoint."""
    # DB_PATH is a string path to predictwell.db
    return {"status": "ok", "db": str(DB_PATH)}

# -----------------------------------------------------
# Example Patient Endpoint (placeholder, no DB write yet)
# -----------------------------------------------------
@app.post("/patients/", response_model=PatientOut)
def create_patient(patient: PatientCreate):
    # Placeholder echo until we wire SQL inserts (we’ll do that next)
    return PatientOut(
        id=1,  # in a real DB this will auto-increment
        created_at=datetime.utcnow(),
        **(patient.dict() if patient is not None else {}),
    )

# -----------------------------------------------------
# AI Risk Prediction Endpoint
# -----------------------------------------------------
@app.post("/risk", response_model=RiskOutput)
def calculate_risk(data: RiskInput):
    """
    Accepts health/workload data and returns a predictive risk score.
    Example Input:
    {
      "workload": 7.5,
      "sleep_hours": 6,
      "stress_level": 5,
      "wellness_score": 75
    }
    """
    result = compute_risk(data)
    return result
