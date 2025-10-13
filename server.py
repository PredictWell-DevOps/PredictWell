# server.py — FastAPI app with auth (cookies) + optional existing routers

from __future__ import annotations
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

# --- DB / Models ---
from db import SessionLocal, init_db
from models import (
    User, DoctorProfile, PatientProfile, RefreshToken, AuditLog,
    UserRole, SentinelKind, VerificationStatus
)

# --- Auth utils (hashing + JWT helpers) ---
from auth_utils import (
    hash_password, verify_password,
    make_access_token, make_refresh_token,
    decode_access, decode_refresh, sha256
)

# ------------------------------------------------------------------------------
# App + CORS
# ------------------------------------------------------------------------------
app = FastAPI(title="PredictWell API")

CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,https://predictwellhealth.ai"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# DB dependency
# ------------------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ensure tables exist in whichever DB we’re pointed at
@app.on_event("startup")
def _startup_create_tables():
    init_db()

# ------------------------------------------------------------------------------
# Cookie helpers
# ------------------------------------------------------------------------------
COOKIE_DOMAIN: Optional[str] = os.getenv("COOKIE_DOMAIN") or None

def set_auth_cookies(response: Response, access: str, refresh: str):
    # NOTE: secure=True assumes HTTPS (Render is HTTPS). For local dev over HTTP,
    # you may temporarily set secure=False or use a tool that supports HTTPS.
    response.set_cookie(
        "access_token", access,
        httponly=True, secure=True, samesite="lax", domain=COOKIE_DOMAIN
    )
    response.set_cookie(
        "refresh_token", refresh,
        httponly=True, secure=True, samesite="lax", domain=COOKIE_DOMAIN
    )

def clear_auth_cookies(response: Response):
    for name in ("access_token", "refresh_token"):
        response.delete_cookie(name, domain=COOKIE_DOMAIN)

# ------------------------------------------------------------------------------
# Schemas
# ------------------------------------------------------------------------------
class RegisterDoctorIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    license_number: str
    license_state: str = Field(min_length=2, max_length=2)
    npi: Optional[str] = None
    specialty: Optional[str] = None

class RegisterPatientIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    sentinel: SentinelKind
    ssn_last4: str = Field(min_length=4, max_length=4)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

# ------------------------------------------------------------------------------
# Health
# ------------------------------------------------------------------------------
@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# ------------------------------------------------------------------------------
# Auth endpoints
# ------------------------------------------------------------------------------
@app.post("/auth/register/doctor")
def register_doctor(
    data: RegisterDoctorIn,
    response: Response,
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    u = User(
        email=data.email,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        role=UserRole.doctor.value,
        sentinel=SentinelKind.multi.value,  # doctors may span sentinels
        email_verified=False,
    )
    db.add(u)
    db.flush()

    dp = DoctorProfile(
        user_id=u.id,
        license_number=data.license_number,
        license_state=data.license_state.upper(),
        npi=data.npi,
        specialty=data.specialty,
        verification_status=VerificationStatus.pending.value,
    )
    db.add(dp)
    db.add(AuditLog(user_id=u.id, event_type="register_doctor"))
    db.commit()

    # Auto-login
    access = make_access_token(str(u.id), u.role, u.sentinel)
    refresh, exp = make_refresh_token(str(u.id))
    db.add(RefreshToken(user_id=u.id, token_hash=sha256(refresh), expires_at=exp))
    db.commit()

    set_auth_cookies(response, access, refresh)
    return {"ok": True, "user_id": u.id, "role": u.role}

@app.post("/auth/register/patient")
def register_patient(
    data: RegisterPatientIn,
    response: Response,
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    u = User(
        email=data.email,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        role=UserRole.patient.value,
        sentinel=data.sentinel.value,   # Eldercare | Athletics | Sleep
        email_verified=False,
    )
    db.add(u)
    db.flush()

    pp = PatientProfile(user_id=u.id, ssn_last4=data.ssn_last4)
    db.add(pp)
    db.add(AuditLog(user_id=u.id, event_type="register_patient"))
    db.commit()

    # Auto-login
    access = make_access_token(str(u.id), u.role, u.sentinel)
    refresh, exp = make_refresh_token(str(u.id))
    db.add(RefreshToken(user_id=u.id, token_hash=sha256(refresh), expires_at=exp))
    db.commit()

    set_auth_cookies(response, access, refresh)
    return {"ok": True, "user_id": u.id, "role": u.role, "sentinel": u.sentinel}

@app.post("/auth/login")
def login(
    data: LoginIn,
    response: Response,
    db: Session = Depends(get_db),
):
    u = db.query(User).filter(User.email == data.email).first()
    if not u or not verify_password(data.password, u.password_hash):
        # Log failure; don't reveal which part was wrong
        db.add(AuditLog(user_id=u.id if u else None, event_type="login_failure"))
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = make_access_token(str(u.id), u.role, u.sentinel)
    refresh, exp = make_refresh_token(str(u.id))
    db.add(RefreshToken(user_id=u.id, token_hash=sha256(refresh), expires_at=exp))
    db.add(AuditLog(user_id=u.id, event_type="login_success"))
    db.commit()

    set_auth_cookies(response, access, refresh)
    # Frontend can route by role/sentinel
    return {"ok": True, "role": u.role, "sentinel": u.sentinel}

@app.post("/auth/logout")
def logout(response: Response):
    clear_auth_cookies(response)
    return {"ok": True}

@app.post("/auth/refresh")
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    rt = request.cookies.get("refresh_token")
    if not rt:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    try:
        payload = decode_refresh(rt)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    db_token = db.query(RefreshToken).filter(
        RefreshToken.user_id == int(user_id),
        RefreshToken.token_hash == sha256(rt),
    ).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Unknown refresh token")

    u = db.get(User, int(user_id))
    if not u:
        raise HTTPException(status_code=401, detail="User missing")

    access = make_access_token(str(u.id), u.role, u.sentinel)
    set_auth_cookies(response, access, rt)  # keep same refresh cookie
    return {"ok": True}

@app.get("/auth/me")
def me(request: Request, db: Session = Depends(get_db)):
    at = request.cookies.get("access_token")
    if not at:
        raise HTTPException(status_code=401, detail="Not signed in")
    try:
        payload = decode_access(at)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid access token")

    u = db.get(User, int(payload["sub"]))
    if not u:
        raise HTTPException(status_code=401, detail="User not found")

    return {
        "id": u.id,
        "email": u.email,
        "role": u.role,
        "sentinel": u.sentinel,
        "name": f"{u.first_name or ''} {u.last_name or ''}".strip(),
        "verification_status": (
            u.doctor_profile.verification_status
            if u.role == "doctor" and u.doctor_profile
            else None
        ),
    }

# ------------------------------------------------------------------------------
# Include your existing routers if present (no crash if missing)
# ------------------------------------------------------------------------------
try:
    from eldercare import router as eldercare_router  # if you’ve defined APIRouter there
    app.include_router(eldercare_router, prefix="/eldercare", tags=["eldercare"])
except Exception:
    pass

try:
    from athletics import router as athletics_router
    app.include_router(athletics_router, prefix="/athletics", tags=["athletics"])
except Exception:
    pass

try:
    from sleep import router as sleep_router  # future module
    app.include_router(sleep_router, prefix="/sleep", tags=["sleep"])
except Exception:
    pass
