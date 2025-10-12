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
