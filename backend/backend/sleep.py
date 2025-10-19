# backend/sleep.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/sleep", tags=["sleep"])

class SleepCheckin(BaseModel):
    avg_spo2: Optional[float] = None
    hrv_rmssd: Optional[float] = None
    sleep_efficiency: Optional[float] = None
    pap_adherence_hours: Optional[float] = None

@router.post("/checkin")
def sleep_checkin(data: SleepCheckin):
    # demo placeholder response for presentation
    risk = 0.42
    return {
        "ok": True,
        "risk": risk,
        "inputs": data.dict(),
        "note": "Demo response — model integration pending."
    }
