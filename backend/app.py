from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# ------------------------------------------------------------
# Resolve absolute paths so static files work from any cwd
# Project layout:
#   C:\PredictWell\
#       backend\app.py   (this file)
#       web\index.html
#       web\assets\{styles.css, app.js}
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]   # C:\PredictWell
WEB_DIR = BASE_DIR / "web"
ASSETS_DIR = WEB_DIR / "assets"

app = FastAPI(
    title="PredictWell API",
    version="0.2.0 – Eldercare Sentinel"
)

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve assets (CSS/JS) at /assets and serve index.html at /
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

@app.get("/", include_in_schema=False)
def root_page():
    return FileResponse(str(WEB_DIR / "index.html"))

# -------------------------
# Example Endpoints
# -------------------------

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

class RiskInput(BaseModel):
    age: int
    sex: str
    heart_rate: int
    blood_pressure_sys: int
    respiration_rate: int
    oxygen_saturation: float
    gait_speed: float
    step_variability: float
    hrv: int
    sleep_hours: float
    recent_fall: bool
    mobility_aid: str

    # Extras added in UI (currently ignored by scoring until we update):
    cognitive_score: int | None = None
    balance_test: float | None = None
    medication_count: int | None = None

@app.post("/api/risk-score")
def risk_score(data: RiskInput):
    # Simple placeholder scoring; we’ll expand later
    score = 0
    if data.age > 75: score += 2
    if data.recent_fall: score += 3
    if data.gait_speed < 0.8: score += 2
    if data.oxygen_saturation < 95: score += 2
    if data.sleep_hours < 6: score += 1

    # (Optional) use extras later
    return {"risk_score": score, "message": "Risk score calculated"}

@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")
    content = await file.read()
    return {"filename": file.filename, "size": len(content)}
