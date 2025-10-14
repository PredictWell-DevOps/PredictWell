# backend/server.py — PredictWell API (full version with auth + sleep + eldercare)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --------------------------------------------------------------------------
# Router Imports (robust for both local and Render environments)
# --------------------------------------------------------------------------
try:
    from .eldercare import router as eldercare_router
    from .sleep import router as sleep_router
    from .auth import router as auth_router
except ImportError:
    from eldercare import router as eldercare_router
    from sleep import router as sleep_router
    from auth import router as auth_router

# --------------------------------------------------------------------------
# FastAPI App Initialization
# --------------------------------------------------------------------------
app = FastAPI(
    title="PredictWell API",
    version="1.0.0",
    description="Backend API for PredictWell Health.ai — Eldercare, Sleep, and Performance Sentinel modules.",
)

# --------------------------------------------------------------------------
# CORS Middleware (open during development; restrict later)
# --------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock down later to https://predictwellhealth.ai
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------
# Root & Health Check
# --------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "PredictWell API running. See /docs for details."}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# --------------------------------------------------------------------------
# Include Routers
# --------------------------------------------------------------------------
app.include_router(eldercare_router)
app.include_router(sleep_router)
app.include_router(auth_router)

# --------------------------------------------------------------------------
# End of File
# --------------------------------------------------------------------------
