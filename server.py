# backend/server.py — FastAPI app entrypoint (dual-compatible)

from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import so it works whether launched as:
#   - from project root:  python -m uvicorn backend.server:app --reload
#   - from backend dir:   python -m uvicorn server:app --reload
try:
    from .db import init_db
    from .eldercare import router as eldercare_router
except ImportError:  # running from backend/ as top-level
    from db import init_db
    from eldercare import router as eldercare_router

app = FastAPI(title="PredictWell API", version="2.0.0")

# -----------------------------------------------------------------------------
# CORS — explicit origins work better than "*" when allow_credentials=True.
# Add/remove entries here as needed for dev.
# -----------------------------------------------------------------------------
ALLOWED_ORIGINS = [
    "https://predictwellhealth.ai",     # production frontend
    "http://localhost:5500",            # local static preview (e.g., Live Server)
    "http://127.0.0.1:5500",
    "http://localhost:3000",            # common local ports
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Lifecycle
# -----------------------------------------------------------------------------
@app.on_event("startup")
def _startup():
    # Auto-creates app.db and tables if missing (safe to call each boot)
    init_db()

# -----------------------------------------------------------------------------
# Basic endpoints
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "PredictWell API is running. Visit /docs for Swagger."}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# -----------------------------------------------------------------------------
# Feature routers
# -----------------------------------------------------------------------------
# Eldercare AI endpoints (/eldercare/...)
app.include_router(eldercare_router)
