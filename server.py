# backend/server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Robust import whether run as a package or a module
try:
    from .eldercare import router as eldercare_router
except ImportError:  # when working dir is /backend
    from eldercare import router as eldercare_router

app = FastAPI(title="PredictWell API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock down later to https://predictwellhealth.ai
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "PredictWell API running. See /docs"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# ⬇️ this exposes POST /eldercare/checkin
app.include_router(eldercare_router)
