# app_athletics.py
# PredictWell Health.ai — Athletics Risk Endpoint (Pitcher AI, Trainer Style)

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/athletics", tags=["Athletics"])

# ======== Input Schema ========
class PitcherIntake(BaseModel):
    # Section 1: Arm & Shoulder Condition
    shoulder_soreness: int
    elbow_soreness: int
    forearm_tightness: int
    triceps_fatigue: int
    biceps_pain: int
    shoulder_clicking: int

    # Section 2: Throwing Workload & Mechanics
    pitches_today: int
    pitches_7d: int
    velocity_drop: int
    arm_slot_change: int
    command_loss: int
    effort_level: int
    follow_through_pain: int

    # Section 3: Recovery & Readiness
    sleep_hours: float
    recovery_quality: int
    hydration_level: int
    nutrition_quality: int
    soreness_recovery: int
    rest_days: int

    # Section 4: Focus & Stress
    stress_level: int
    motivation_level: int
    concentration_score: int
    mood_level: int

    # Section 5: Lower-Body Health
    hip_flexor_tightness: int
    quad_soreness: int
    hamstring_tightness: int
    glute_activation: int
    calf_soreness: int
    ankle_stability: int
    knee_pain: int
    groin_tightness: int
    push_off_cramps: int
    balance_stability: int

# ======== Scoring Logic ========
def weighted_score(data: PitcherIntake) -> dict:
    """Computes weighted fatigue and overuse indicators by body region."""
    # Arm load = shoulder + elbow + forearm + triceps + biceps
    arm_load = (
        data.shoulder_soreness + data.elbow_soreness + data.forearm_tightness +
        data.triceps_fatigue + data.biceps_pain + data.shoulder_clicking
    ) / 6

    # Workload strain = pitches, velocity, effort, pain on follow-through
    workload = (
        data.pitches_today / 100 +
        data.pitches_7d / 300 +
        data.velocity_drop / 5 +
        data.arm_slot_change / 5 +
        data.command_loss / 5 +
        data.effort_level / 5 +
        data.follow_through_pain / 5
    ) * 10

    # Recovery quality (inverse weighting)
    recovery = (
        (10 - data.recovery_quality) +
        (10 - data.hydration_level) +
        (10 - data.nutrition_quality) +
        (10 - data.soreness_recovery)
    ) / 4

    # Mental load
    mental = (
        data.stress_level +
        (10 - data.motivation_level) +
        (10 - data.concentration_score) +
        (10 - data.mood_level)
    ) / 4

    # Lower body strain
    lower_body = (
        data.hip_flexor_tightness + data.quad_soreness + data.hamstring_tightness +
        data.glute_activation + data.calf_soreness + data.ankle_stability +
        data.knee_pain + data.groin_tightness + data.push_off_cramps + data.balance_stability
    ) / 10

    # Composite fatigue and risk score
    total_risk = (
        arm_load * 0.35 +
        workload * 0.25 +
        recovery * 0.15 +
        mental * 0.1 +
        lower_body * 0.15
    )

    return {
        "arm_load": round(arm_load, 2),
        "workload": round(workload, 2),
        "recovery": round(recovery, 2),
        "mental": round(mental, 2),
        "lower_body": round(lower_body, 2),
        "total_risk": round(total_risk, 2)
    }

# ======== Text Generation ========
def generate_feedback(scores: dict) -> str:
    """Creates trainer-style feedback based on calculated scores."""
    lines = []

    # Section 1: Muscles Under Stress
    if scores["arm_load"] > 6:
        lines.append("Muscles Under Stress:\nYour arm is feeling heavy today, especially around the shoulder and elbow. Limit high-intensity throws and focus on stretching and recovery work.")
    elif scores["arm_load"] > 4:
        lines.append("Muscles Under Stress:\nYou’re showing moderate arm fatigue. Pay attention to forearm and shoulder stabilizers — light band work will help.")
    else:
        lines.append("Muscles Under Stress:\nArm load looks manageable today. Stay consistent with mobility and band maintenance.")

    # Section 2: Recovery Advice
    if scores["recovery"] > 6:
        lines.append("Recovery Advice:\nYou might be under-recovering — get extra hydration and sleep tonight. Keep nutrition steady and avoid throwing two days in a row.")
    elif scores["recovery"] > 4:
        lines.append("Recovery Advice:\nYour recovery is fair but can improve. Try a mobility session and hydration boost before next outing.")
    else:
        lines.append("Recovery Advice:\nRecovery looks strong. Maintain your current routine and prioritize sleep on travel or game days.")

    # Section 3: Training Tip
    if scores["lower_body"] > 6:
        lines.append("Training Tip:\nLower-body fatigue is limiting your drive off the mound. Focus on glute activation and hip mobility work before your next session.")
    elif scores["lower_body"] > 4:
        lines.append("Training Tip:\nSome leg and hip tightness is showing — add light dynamic stretches to pre-throw warmup.")
    else:
        lines.append("Training Tip:\nLower-body stability is solid. Keep your current strength and movement prep going.")

    # Add summary
    lines.append(f"\nOverall Read: Total risk score = {scores['total_risk']} (0–10 scale).")
    return "\n\n".join(lines)

# ======== API Route ========
@router.post("/risk")
async def compute_pitcher_risk(intake: PitcherIntake):
    scores = weighted_score(intake)
    feedback = generate_feedback(scores)
    return {
        "status": "ok",
        "risk_score": scores["total_risk"],
        "feedback": feedback
    }
