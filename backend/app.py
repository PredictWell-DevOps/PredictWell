from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.db import Base, engine, get_db
from backend import schemas
from datetime import datetime

# Import AI module
from backend.ai_module import RiskInput, RiskOutput, compute_risk

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PredictWell Health.ai API", version="1.0")

# -----------------------------------------------------
# Health Check Endpoint
# -----------------------------------------------------
@app.get("/healthz")
def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "db": str(engine.url)}

# -----------------------------------------------------
# Example Patient Endpoint (placeholder)
# -----------------------------------------------------
@app.post("/patients/", response_model=schemas.PatientOut)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    new_patient = schemas.PatientOut(
        id=1,  # In a real DB, this auto-increments
        created_at=datetime.utcnow(),
        **patient.dict(),
    )
    return new_patient

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
