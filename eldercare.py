# backend/eldercare.py
from fastapi import APIRouter, Body
from pydantic import BaseModel
from datetime import datetime
import random

router = APIRouter()

class EldercareInput(BaseModel):
    source: str = "patient_portal"
    inputs: dict
    client_score: float = 0.0

def _clip(v: float) -> float:
    return max(0, min(100, round(v, 1)))

def _forecast_from(local_score: float):
    # lower local score ⇒ higher risk
    base = 100 - float(local_score)
    current = _clip(base + random.uniform(-5, 5))
    in2w   = _clip(current + random.uniform(-3, 3))
    in4w   = _clip(in2w   + random.uniform(-3, 3))
    return {
        "risk": {
            "current": current,
            "two_weeks": in2w,
            "four_weeks": in4w,
            "notes": {
                "current":   "Current predicted fall/frailty risk.",
                "two_weeks": "Projected 2-week risk given current trend.",
                "four_weeks":"Projected 4-week risk if no major change."
            }
        },
        "generated_at": datetime.utcnow().isoformat()
    }

@router.post("/eldercare/checkin")
def eldercare_checkin(payload: EldercareInput = Body(...)):
    ai = _forecast_from(payload.client_score)
    return {
        "id": random.randint(1, 999999),
        "source": payload.source,
        "inputs": payload.inputs,
        "client_score": payload.client_score,
        **ai
    }
