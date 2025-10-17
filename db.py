import os
import sqlite3
from contextlib import contextmanager

# Exported so /healthz can show the resolved path
DB_PATH = os.environ.get("PREDICTWELL_DB", "predictwell.db")

DDL = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS patients (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  external_id TEXT UNIQUE,
  first_name TEXT, last_name TEXT, dob TEXT, sex TEXT
);

CREATE TABLE IF NOT EXISTS eldercare_checkins (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  patient_id INTEGER NOT NULL,

  -- History/context
  age INTEGER, prior_falls_12mo INTEGER, injurious_fall INTEGER,
  fear_of_falling INTEGER, device_use TEXT,

  -- Meds/vitals/sensory/comorbidity
  meds_count INTEGER, psychotropics INTEGER,
  ortho_bp_sup INTEGER, ortho_bp_sit INTEGER, ortho_bp_stand INTEGER,
  hr INTEGER,
  vision_corrected INTEGER, hearing_issue INTEGER,
  neuropathy INTEGER, diabetes INTEGER, parkinsons INTEGER,
  stroke INTEGER, arthritis INTEGER,
  adl_difficulty INTEGER,

  -- Clinic tests
  tug_sec REAL, bbs_total INTEGER, sppb_total INTEGER,

  -- Gait (single-task)
  gait_speed REAL, cadence REAL, stride_time REAL, stride_time_cv REAL,
  step_width REAL, step_width_cv REAL,
  double_support_pct REAL, ap_harmonic REAL, ml_harmonic REAL,
  rms_acc REAL, jerk REAL, sample_entropy REAL,

  -- Dual-task
  dt_gait_speed REAL, dt_stride_time_cv REAL, dt_cost_speed_pct REAL,

  notes TEXT,
  FOREIGN KEY(patient_id) REFERENCES patients(id)
);

CREATE TABLE IF NOT EXISTS pitcher_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  patient_id INTEGER NOT NULL,
  level TEXT, pitches_today INTEGER, pitches_last3d INTEGER, rest_days INTEGER,
  elbow_pain INTEGER, shoulder_pain INTEGER, velo_drop REAL, mechanics_flags INTEGER,
  FOREIGN KEY(patient_id) REFERENCES patients(id)
);

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  route TEXT NOT NULL,
  patient_id INTEGER,
  payload TEXT NOT NULL,
  result TEXT NOT NULL,
  FOREIGN KEY(patient_id) REFERENCES patients(id)
);
"""

@contextmanager
def get_conn():
    """Context manager returning a sqlite3 connection with Row dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db() -> None:
    """Create all tables if they don't exist."""
    with get_conn() as c:
        # executescript handles multiple statements safely
        c.executescript(DDL)

def log_event(route: str, patient_id: int | None, payload: str, result: str) -> None:
    """Audit log of input/output for research and debugging."""
    from datetime import datetime
    with get_conn() as c:
        c.execute(
            """INSERT INTO events (created_at, route, patient_id, payload, result)
               VALUES (?, ?, ?, ?, ?)""",
            (datetime.utcnow().isoformat(), route, patient_id, payload, result),
        )
