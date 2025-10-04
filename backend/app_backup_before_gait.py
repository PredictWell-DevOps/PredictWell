from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import io, csv

app = FastAPI(title="PredictWell API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the web folder (simple frontend)
app.mount("/", StaticFiles(directory="web", html=True), name="web")

class RiskInput(BaseModel):
    pitch_count: int
    workload_7d: float
    sleep_hours: float
    prior_injury: bool

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/risk-score")
def risk_score(payload: RiskInput):
    base = 0.15
    score = (
        base
        + (payload.pitch_count / 150) * 0.35
        + (payload.workload_7d / 500.0) * 0.25
        + (1.0 - min(payload.sleep_hours / 8.0, 1.0)) * 0.15
        + (0.10 if payload.prior_injury else 0.0)
    )
    return {"risk_score": round(min(max(score, 0.0), 1.0), 3)}

@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Please upload a .csv file")
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    return {"rows": len(rows), "columns": reader.fieldnames}
