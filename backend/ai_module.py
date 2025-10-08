from pydantic import BaseModel
from math import exp
from datetime import datetime

class RiskInput(BaseModel):
    workload: float          # e.g., training load / activity intensity
    sleep_hours: float       # nightly sleep
    stress_level: float      # 1-10 subjective
    wellness_score: float    # 0-100 general wellbeing

class RiskOutput(BaseModel):
    risk_score: float
    category: str
    timestamp: datetime

def compute_risk(data: RiskInput) -> RiskOutput:
    """Lightweight logistic-style risk computation (placeholder for AI model)."""
    # Normalize and weight factors
    x = (
        0.4 * (data.workload / 10)
        + 0.3 * (data.stress_level / 10)
        - 0.2 * (data.sleep_hours / 8)
        - 0.1 * (data.wellness_score / 100)
    )

    risk = 1 / (1 + exp(-8 * (x - 0.5)))  # logistic curve
    category = (
        "Low" if risk < 0.33 else
        "Moderate" if risk < 0.66 else
        "High"
    )

    return RiskOutput(
        risk_score=round(risk, 3),
        category=category,
        timestamp=datetime.utcnow()
    )
