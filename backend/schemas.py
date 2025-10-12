from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ---------- Core Models ----------
class PatientBase(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    dob: Optional[str]
    sex: Optional[str]

class PatientCreate(PatientBase):
    external_id: Optional[str]

class PatientOut(PatientBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# ---------- Eldercare ----------
class EldercareCheckInBase(BaseModel):
    patient_id: int
    age: Optional[int]
    prior_falls_12mo: Optional[int]
    injurious_fall: Optional[int]
    fear_of_falling: Optional[int]
    device_use: Optional[str]
    meds_count: Optional[int]
    psychotropics: Optional[int]
    ortho_bp_sup: Optional[int]
    ortho_bp_sit: Optional[int]
    ortho_bp_stand: Optional[int]
    hr: Optional[int]
    vision_corrected: Optional[int]
    hearing_issue: Optional[int]
    neuropathy: Optional[int]
    diabetes: Optional[int]
    parkinsons: Optional[int]
    stroke: Optional[int]
    arthritis: Optional[int]
    adl_difficulty: Optional[int]
    tug_sec: Optional[float]
    bbs_total: Optional[int]
    sppb_total: Optional[int]
    gait_speed: Optional[float]
    cadence: Optional[float]
    stride_time: Optional[float]
    stride_time_cv: Optional[float]
    step_width: Optional[float]
    step_width_cv: Optional[float]
    double_support_pct: Optional[float]
    ap_harmonic: Optional[float]
    ml_harmonic: Optional[float]
    rms_acc: Optional[float]
    jerk: Optional[float]
    sample_entropy: Optional[float]
    dt_gait_speed: Optional[float]
    dt_stride_time_cv: Optional[float]
    dt_cost_speed_pct: Optional[float]
    notes: Optional[str]

class EldercareCheckInCreate(EldercareCheckInBase):
    pass

class EldercareCheckInOut(EldercareCheckInBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# ---------- Pitcher (Athlete) ----------
class PitcherSessionBase(BaseModel):
    patient_id: int
    level: Optional[str]
    pitches_today: Optional[int]
    pitches_last3d: Optional[int]
    rest_days: Optional[int]
    elbow_pain: Optional[int]
    shoulder_pain: Optional[int]
    velo_drop: Optional[float]
    mechanics_flags: Optional[int]

class PitcherSessionCreate(PitcherSessionBase):
    pass

class PitcherSessionOut(PitcherSessionBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
