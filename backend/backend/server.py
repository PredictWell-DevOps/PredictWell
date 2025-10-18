# server.py - PredictWell Health.ai unified backend
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("predictwell")

# Create FastAPI app
app = FastAPI(
    title="PredictWell API",
    version="1.0.0",
    description="Backend API for PredictWell Health.ai"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "PredictWell API running"}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

# Import routers
try:
    from eldercare import router as eldercare_router
    app.include_router(eldercare_router)
    logger.info("Loaded eldercare router")
except Exception as e:
    logger.error(f"Failed to load eldercare: {e}")

try:
    from app_athletics import router as athletics_router
    app.include_router(athletics_router)
    logger.info("Loaded athletics router")
except Exception as e:
    logger.error(f"Failed to load athletics: {e}")

try:
    from sleep import router as sleep_router
    app.include_router(sleep_router)
    logger.info("Loaded sleep router")
except Exception as e:
    logger.error(f"Failed to load sleep: {e}")

try:
    from auth import router as auth_router
    app.include_router(auth_router)
    logger.info("Loaded auth router")
except Exception as e:
    logger.error(f"Failed to load auth: {e}")
