# backend/eldercare.py
# COMPLETE file — patient-portal lite analysis + doctor-portal compatibility
# Includes robust error handling so failures return readable JSON (400) instead of 500.

from __future__ import annotations
from typing import Optional, List, Dict, Any, Tuple
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter(prefix="/eldercare", tags=["eldercare"])

# =============================================================================
# Schemas
# =============================================================================

class Intake(BaseModel):
    # Generic (patient + doctor)
    source: Optional[str] = None
    checkin_type: Optional[str] = None  # e.g., "patient_simple12" from patient portal

    # Patient portal may send everything inside `inputs` (we normalize it)
    inputs: Optional[Dict[str, Any]] = None
    client_score: Optional[Any] = None  # may be a number or {score: n, level: ...}

    # ---- Patient (12Q) / shared fields ----
    age: Optional[int] = None
    living: Optional[str] = None                 # patient: alone/with_family/assisted/facility
    falls_12m: Optional[str] = None
    unsteady: Optional[str] = None
    fear_fall: Optional[str] = None
    chair_rise: Optional[str] = None
    dizzy_stand: Optional[str] = None            # mapped from patient "dizzy"
    med_count: Optional[str] = None
    memory_change: Optional[str] = None          # mapped from patient "memory"
    mood: Optional[str] = None
    activity: Optional[str] = None
    home_hazards: Optional[str] = None           # mapped from patient "home_haz"

    # ---- Doctor portal additions (optional) ----
    pt_age: Optional[int] = None
    sex: Optional[str] = None
    weight_lb: Optional[float] = None
    height_in: Optional[float] = None

    bp_syst: Optional[float] = None
    bp_diast: Optional[float] = None
    hr: Optional[float] = None
    rr: Optional[float] = None
    spo2: Optional[float] = None
    temp: Optional[float] = None
    glucose_fasting: Optional[float] = None

    falls_12m_doctor: Optional[str] = None
    orthostatics: Optional[str] = None
    orthostat_sympt: Optional[str] = None
    postural_drops: Optional[str] = None

    # Checkbox groups (doctor portal)
    conditions: Optional[Dict[str, bool]] = None
    other_risks: Optional[Dict[str, bool]] = None
    interventions: Optional[Dict[str, bool]] = None
    followup: Optional[Dict[str, bool]] = None

    # Free text
    prior_fall_details: Optional[str] = None
    pain_assess: Optional[str] = None
    clinician_notes: Optional[str] = None


class PredictionOut(BaseModel):
    received_at: str
    risk_now: float
    risk_14d: float
    risk_28d: float
    bucket_now: str
    bucket_14d: str
    bucket_28d: str
    top_contributors: List[str]
    suggested_actions: List[str]
    confidence: float
    timeline: List[Dict[str, Any]]
    echo: Dict[str, Any]

# =============================================================================
# Utilities
# =============================================================================

def _nz(x, default=0.0) -> float:
    try:
        return float(x) if x is not None and x != "" else float(default)
    except Exception:
        return float(default)

def _bucket(score: float) -> str:
    if score >= 75: return "Very High"
    if score >= 55: return "High"
    if score >= 35: return "Moderate"
    return "Low"

def _cap(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))

def _bool(d: Optional[Dict[str, bool]], key: str) -> bool:
    return bool(d and d.get(key))

def _list_add(lst: List[str], item: str, cond: bool):
    if cond: lst.append(item)

def _safe_int(x: Any) -> Optional[int]:
    try:
        if x is None or x == "": return None
        return int(str(x).strip())
    except Exception:
        return None

# =============================================================================
# Patient → Doctor normalization
# =============================================================================

def normalize_patient_inputs(payload: Intake) -> Intake:
    """
    If the request includes patient-portal style `inputs`, map them into the
    doctor-style field names used by the risk engine. Returns a new Intake.
    If no `inputs` are present, returns the payload unchanged.
    """
    if not payload.inputs:
        return payload

    d = payload.inputs or {}

    # Maps for patient values → doctor-style vocab
    living_map = {
        "alone": "Alone",
        "with_family": "With family/partner",
        "assisted": "Assisted living",
        "facility": "Skilled nursing facility",
    }
    falls_map = {"0": "0", "1": "1", "2plus": "2 or more"}
    unsteady_map = {"no": "No", "sometimes": "Sometimes", "often": "Often"}
    fear_map = {"no": "No", "a_little": "A little", "yes": "Yes"}
    chair_map = {"yes": "Yes", "hard": "Yes, but hard", "no": "No"}
    dizzy_map = {"no": "No", "occasional": "Occasionally", "frequent": "Often"}
    med_map = {"0-3": "0–2", "4-7": "3–4", "8+": "5 or more"}
    memory_map = {"no": "No", "mild": "Some days", "significant": "Most days"}
    mood_map = {"no": "No", "sometimes": "Somewhat down/anxious", "often": "Depressed or anxious"}
    activity_map = {"low": "Hardly active", "moderate": "2–3x/week", "high": "4+ x/week"}
    home_map = {"none": "No", "some": "Yes", "many": "Yes"}

    mapped = Intake(
        # pass-through
        source=payload.source or "patient_portal",
        checkin_type=payload.checkin_type,
        client_score=payload.client_score,
        # mapped 12Q
        age=_safe_int(d.get("age")),
        living=living_map.get((d.get("living") or "").strip(), payload.living),
        falls_12m=falls_map.get((d.get("falls_12m") or "").strip(), payload.falls_12m),
        unsteady=unsteady_map.get((d.get("unsteady") or "").strip(), payload.unsteady),
        fear_fall=fear_map.get((d.get("fear_fall") or "").strip(), payload.fear_fall),
        chair_rise=chair_map.get((d.get("chair_rise") or "").strip(), payload.chair_rise),
        dizzy_stand=dizzy_map.get((d.get("dizzy") or "").strip(), payload.dizzy_stand),
        med_count=med_map.get((d.get("med_count") or "").strip(), payload.med_count),
        memory_change=memory_map.get((d.get("memory") or "").strip(), payload.memory_change),
        mood=mood_map.get((d.get("mood") or "").strip(), payload.mood),
        activity=activity_map.get((d.get("activity") or "").strip(), payload.activity),
        home_hazards=home_map.get((d.get("home_haz") or "").strip(), payload.home_hazards),
        # doctor fields preserved from original payload
        pt_age=payload.pt_age,
        sex=payload.sex,
        weight_lb=payload.weight_lb,
        height_in=payload.height_in,
        bp_syst=payload.bp_syst,
        bp_diast=payload.bp_diast,
        hr=payload.hr,
        rr=payload.rr,
        spo2=payload.spo2,
        temp=payload.temp,
        glucose_fasting=payload.glucose_fasting,
        falls_12m_doctor=payload.falls_12m_doctor,
        orthostatics=payload.orthostatics,
        orthostat_sympt=payload.orthostat_sympt,
        postural_drops=payload.postural_drops,
        conditions=payload.conditions,
        other_risks=payload.other_risks,
        interventions=payload.interventions,
        followup=payload.followup,
        prior_fall_details=payload.prior_fall_details,
        pain_assess=payload.pain_assess,
        clinician_notes=payload.clinician_notes,
    )
    return mapped

# =============================================================================
# Deterministic risk model (explainable)
# =============================================================================

def compute_base_risk(p: Intake) -> Tuple[float, List[str]]:
    """
    Compute a 0–100 risk index from whatever is present.
    Uses patient 12Q if available, and augments with vitals/flags from doctor intake.
    """
    contributors: List[str] = []
    s = 0.0

    # Age
    age = p.age or p.pt_age or 0
    if age >= 85: s += 14; contributors.append("Advanced age (85+)")
    elif age >= 75: s += 10; contributors.append("Age 75–84")
    elif age >= 65: s += 6;  contributors.append("Age 65–74")

    # Living situation
    if p.living == "Alone": s += 6; contributors.append("Lives alone")
    elif p.living == "Assisted living": s += 3; contributors.append("Assisted living")

    # Falls history
    falls = p.falls_12m or p.falls_12m_doctor or ""
    if falls == "1": s += 8; contributors.append("1 fall in 12m")
    elif falls in ("2 or more", "2+"): s += 16; contributors.append("2+ falls in 12m")

    # Gait / fear / chair rise / dizziness
    if p.unsteady in ("Sometimes", "Often"): s += 8; contributors.append("Unsteady gait")
    if p.fear_fall == "Yes": s += 6; contributors.append("Fear of falling")
    if p.chair_rise == "Yes, but hard": s += 6; contributors.append("Chair rise difficult")
    elif p.chair_rise == "No": s += 10; contributors.append("Cannot rise from chair")
    if p.dizzy_stand in ("Occasionally", "Often"): s += 6; contributors.append("Orthostatic symptoms")

    # Polypharmacy
    if p.med_count in ("3–4", "3-4", "0–2"):  # tolerate minor variants
        if p.med_count in ("3–4", "3-4"): s += 4; contributors.append("3–4 meds")
    elif p.med_count in ("5 or more", "5+"):
        s += 8; contributors.append("Polypharmacy (5+)")

    # Cognitive / mood / activity / hazards
    if p.memory_change in ("Some days", "Most days"): s += 6; contributors.append("Memory changes")
    if p.mood in ("Somewhat down/anxious", "Depressed or anxious"): s += 4; contributors.append("Mood concern")
    if p.activity == "Hardly active": s += 6; contributors.append("Low activity")
    if p.home_hazards in ("Yes", "Not sure"): s += 6; contributors.append("Home hazards")

    # Doctor vitals
    spo2 = _nz(p.spo2, None)
    if spo2 and spo2 < 92: s += 8; contributors.append("Low SpO₂")
    hr = _nz(p.hr, None)
    if hr and (hr < 50 or hr > 100): s += 4; contributors.append("Abnormal HR")
    sbp = _nz(p.bp_syst, None)
    dbp = _nz(p.bp_diast, None)
    if sbp and dbp and (sbp < 100 or dbp < 60): s += 8; contributors.append("Orthostatic/low BP suspected")
    temp = _nz(p.temp, None)
    if temp and temp >= 100.4: s += 3; contributors.append("Fever")
    gluc = _nz(p.glucose_fasting, None)
    if gluc and gluc >= 180: s += 3; contributors.append("High glucose")

    # Diagnoses / risk groups
    c = p.conditions or {}
    _list_add(contributors, "Gait/balance disorder", _bool(c, "gait_balance"))
    _list_add(contributors, "Neuropathy", _bool(c, "neuropathy"))
    _list_add(contributors, "Dementia", _bool(c, "dementia"))
    _list_add(contributors, "Depression", _bool(c, "depression"))
    _list_add(contributors, "Osteoporosis", _bool(c, "osteoporosis"))
    _list_add(contributors, "Vision/hearing impairment", _bool(c, "vision") or _bool(c, "hearing"))
    if any(_bool(c, k) for k in ["gait_balance","neuropathy","dementia","depression","osteoporosis","vision","hearing"]):
        s += 10

    # Orthostatics / postural drops
    if p.orthostatics in ("Dizziness on standing", "Lightheaded / near-syncope") or \
       p.orthostat_sympt in ("Dizziness","Lightheadedness","Syncope") or \
       p.postural_drops == "Yes":
        s += 8; contributors.append("Orthostatic symptoms/drops")

    # Client chip score (if present) can raise baseline
    if p.client_score is not None:
        try:
            cs = float(p.client_score["score"]) if isinstance(p.client_score, dict) and "score" in p.client_score else float(p.client_score)
            s = max(s, min(100.0, cs * 3.0))  # 0–33 chip → 0–99 cap
        except Exception:
            pass

    return _cap(s), contributors


def project_trajectory(r_now: float, p: Intake) -> Tuple[float, float, float]:
    r14 = r_now
    r28 = r_now

    # Risk drivers (upward pressure)
    drivers = 0
    if (p.falls_12m in ("1", "2 or more", "2+")): drivers += 1
    if p.unsteady in ("Sometimes", "Often"): drivers += 1
    if p.chair_rise in ("Yes, but hard", "No"): drivers += 1
    if p.memory_change in ("Some days", "Most days"): drivers += 1
    if p.home_hazards in ("Yes", "Not sure"): drivers += 1
    if (p.conditions and (p.conditions.get("gait_balance") or p.conditions.get("neuropathy") or p.conditions.get("dementia"))): drivers += 1
    if _nz(p.spo2, 100) < 92 or _nz(p.bp_syst, 200) < 100: drivers += 1

    # Interventions (downward pressure)
    ints = p.interventions or {}
    follow = p.followup or {}
    mitigators = 0
    mitigators += 1 if ints.get("pain") else 0
    mitigators += 1 if ints.get("wound") else 0
    mitigators += 1 if follow.get("pt") else 0
    mitigators += 1 if follow.get("home_safety") else 0
    mitigators += 1 if follow.get("med_review") else 0
    mitigators += 1 if follow.get("orthostatics") else 0

    # Net drift per 14 days + regression toward moderate
    drift14 = (drivers * 2.5) - (mitigators * 3.0)
    toward_mid = (35 - r_now) * 0.08
    r14 = _cap(r_now + drift14 + toward_mid)

    drift14_next = (drivers * 2.5) - (mitigators * 3.0)
    toward_mid_next = (35 - r14) * 0.08
    r28 = _cap(r14 + drift14_next + toward_mid_next)

    return r_now, r14, r28


def build_actions(p: Intake, contributors: List[str]) -> List[str]:
    actions: List[str] = []
    _list_add(actions, "Start PT for balance/strength; 2×/week for 4 weeks.", p.unsteady in ("Sometimes","Often"))
    _list_add(actions, "Home safety visit: remove throw rugs, add night lights, install grab bars.", p.home_hazards in ("Yes","Not sure"))
    _list_add(actions, "Chair-rise training daily (3 sets of 5–10) and adjust chair height.", p.chair_rise in ("Yes, but hard","No"))
    _list_add(actions, "Orthostatic vitals and hydration plan; review antihypertensives/diuretics.", p.dizzy_stand in ("Occasionally","Often") or p.orthostatics in ("Dizziness on standing","Lightheaded / near-syncope"))
    _list_add(actions, "Medication review targeting fall-risk meds; simplify regimen if possible.", (p.med_count in ("5 or more","5+")))
    _list_add(actions, "Cognitive and mood screen; consider caregiver support plan.", p.memory_change in ("Some days","Most days") or p.mood in ("Somewhat down/anxious","Depressed or anxious"))
    if not actions:
        actions.append("Daily 10-minute walk program; weekly check-in on symptoms and confidence.")
    return actions[:5]


def plan_timeline(actions: List[str]) -> List[Dict[str, Any]]:
    today = datetime.utcnow().date()
    return [
        {"date": str(today), "title": "Today", "action": actions[0] if actions else "Begin daily 10-minute walk."},
        {"date": str(today + timedelta(days=7)), "title": "Week 1 check-in", "action": "Review adherence, adjust plan; confirm home safety fixes."},
        {"date": str(today + timedelta(days=14)), "title": "Week 2", "action": "Progress PT intensity; re-check chair-rise count and dizziness."},
        {"date": str(today + timedelta(days=28)), "title": "Week 4", "action": "Re-evaluate falls risk; repeat orthostatic vitals; update care plan."},
    ]

# =============================================================================
# Routes
# =============================================================================

@router.get("/ping")
def ping():
    return {"ok": True, "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z"}

@router.post("/checkin", response_model=PredictionOut)
def checkin(payload: Intake) -> PredictionOut:
    """
    Unified endpoint:
    - Doctor portal: send fields directly (backward-compatible).
    - Patient portal: may send { source, checkin_type, inputs: {...}, client_score }
      — we normalize `inputs` into doctor-style fields, then run the same engine.
    """
    try:
        # Normalize if this is a patient-portal style body
        normalized = normalize_patient_inputs(payload) if payload.inputs else payload

        # Compute analysis
        base, contributors = compute_base_risk(normalized)
        r0, r14, r28 = project_trajectory(base, normalized)
        actions = build_actions(normalized, contributors)

        return PredictionOut(
            received_at=datetime.utcnow().isoformat(timespec="seconds") + "Z",
            risk_now=round(r0, 1),
            risk_14d=round(r14, 1),
            risk_28d=round(r28, 1),
            bucket_now=_bucket(r0),
            bucket_14d=_bucket(r14),
            bucket_28d=_bucket(r28),
            top_contributors=contributors[:6],
            suggested_actions=actions,
            confidence=0.62,  # deterministic rules; adjust when adding trained model
            timeline=plan_timeline(actions),
            echo={
                "age": normalized.age or normalized.pt_age,
                "falls_12m": normalized.falls_12m or normalized.falls_12m_doctor,
                "unsteady": normalized.unsteady,
                "chair_rise": normalized.chair_rise,
                "dizzy_stand": normalized.dizzy_stand,
                "med_count": normalized.med_count,
                "mood": normalized.mood,
                "activity": normalized.activity,
                "home_hazards": normalized.home_hazards,
            },
        )
    except HTTPException:
        # Already a clean API error; just bubble up
        raise
    except Exception as e:
        # Log will still include full traceback via uvicorn; return readable message to client
        raise HTTPException(status_code=400, detail=f"eldercare.checkin failed: {type(e).__name__}: {e}")
