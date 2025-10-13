# backend/db.py — SQLite engine + Base + init_db (env-aware)

from __future__ import annotations
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Declarative Base (models should import this as: from db import Base)
Base = declarative_base()

def _get_database_url() -> str:
    """Use DATABASE_URL if set (Render), else fallback to local app.db."""
    url = os.getenv("DATABASE_URL")
    if url and url.strip():
        return url

    # Fallback: local SQLite file next to this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_file = os.path.join(base_dir, "app.db")
    return f"sqlite:///{db_file}"

DATABASE_URL = _get_database_url()

# SQLite needs check_same_thread=False for single-threaded dev servers
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """
    Import models and create tables. Safe to call on every startup.
    Works whether 'backend' is a package or run as top-level.
    """
    try:
        from . import models  # noqa: F401
    except Exception:
        import models  # type: ignore  # noqa: F401

    Base.metadata.create_all(bind=engine)
