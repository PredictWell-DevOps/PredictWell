# backend/models.py — Minimal models, dual-compatible imports

from __future__ import annotations
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON

# Dual import for Base (works as package or top-level run)
try:
    from .db import Base  # when importing as 'backend' package
except Exception:
    from db import Base    # when running from inside backend/ as top-level

# Minimal table (handy for logging; safe if unused elsewhere)
class CheckinEvent(Base):
    __tablename__ = "checkin_events"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=True)
    checkin_type = Column(String, nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
# =========================
# AUTH MODELS (PredictWell)
# =========================
from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, ForeignKey, Index
)
from sqlalchemy.orm import relationship, declarative_base

# If your file already defines Base elsewhere, reuse it; otherwise uncomment next line:
# Base = declarative_base()

class UserRole(str, Enum):
    doctor = "doctor"
    patient = "patient"
    investor_dummy = "investor_dummy"

class SentinelKind(str, Enum):
    eldercare = "eldercare"
    athletics = "athletics"
    sleep = "sleep"
    multi = "multi"   # for investor demo or multi-access internal accounts

class VerificationStatus(str, Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"

class User(Base):  # type: ignore[name-defined]
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    first_name = Column(String(100), nullable=True)
    last_name  = Column(String(100), nullable=True)

    role = Column(String(32), nullable=False, default=UserRole.patient.value)
    sentinel = Column(String(32), nullable=False, default=SentinelKind.eldercare.value)

    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    doctor_profile = relationship("DoctorProfile", back_populates="user", uselist=False)
    patient_profile = relationship("PatientProfile", back_populates="user", uselist=False)
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

Index("ix_users_role", User.role)
Index("ix_users_sentinel", User.sentinel)

class DoctorProfile(Base):  # type: ignore[name-defined]
    __tablename__ = "doctor_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    license_number = Column(String(64), nullable=False)
    license_state  = Column(String(2),  nullable=False)   # e.g., MT
    npi            = Column(String(20), nullable=True)
    specialty      = Column(String(120), nullable=True)
    verification_status = Column(String(16), nullable=False, default=VerificationStatus.pending.value)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="doctor_profile")

class PatientProfile(Base):  # type: ignore[name-defined]
    __tablename__ = "patient_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    dob = Column(String(10), nullable=True)               # YYYY-MM-DD (simple string for now)
    address = Column(String(255), nullable=True)
    ssn_last4 = Column(String(4), nullable=True)          # store last4 only

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="patient_profile")

class RefreshToken(Base):  # type: ignore[name-defined]
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    token_hash = Column(String(255), nullable=False)      # store hash, not raw token
    user_agent = Column(String(255), nullable=True)
    ip = Column(String(64), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="refresh_tokens")

class AuditLog(Base):  # type: ignore[name-defined]
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_type = Column(String(64), nullable=False)       # e.g., register, login_success, login_failure, logout
    details = Column("metadata", String(1000), nullable=True)  # renamed attr; DB column still 'metadata'

    created_at = Column(DateTime, default=datetime.utcnow)
