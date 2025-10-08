from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.db import Base, engine, get_db
from backend import schemas
from datetime import datetime

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PredictWell Health.ai API", version="1.0")

@app.get("/healthz")
def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "db": str(engine.url)}

# Example: create a placeholder patient
@app.post("/patients/", response_model=schemas.PatientOut)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    new_patient = schemas.PatientOut(
        id=1,  # In real DB, this will auto-increment
        created_at=datetime.utcnow(),
        **patient.dict()
    )
    return new_patient
