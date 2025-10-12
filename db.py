# backend/db.py — SQLite engine + Base + init_db (dual-compatible)

from __future__ import annotations
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# -----------------------------------------------------------------------------
# SQLite path alongside this file (backend/app.db)
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "app.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # needed for SQLite in single process
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Exported Declarative Base
Base = declarative_base()

# -----------------------------------------------------------------------------
# init_db: import models safely (works whether backend is a package or top-level)
# -----------------------------------------------------------------------------
def init_db() -> None:
    """
    Import models and create tables. Safe to call on every startup.
    """
    # Try relative import when 'backend' is treated as a package
    try:
        from . import models  # noqa: F401
    except Exception:
        # Fallback when running from inside backend/ as top-level
        import models  # type: ignore  # noqa: F401

    # Create all tables registered on Base
    Base.metadata.create_all(bind=engine)
