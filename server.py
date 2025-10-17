# backend/server.py — PredictWell Health.ai unified backend
# Includes: Eldercare, Athletics (Pitcher AI), Sleep, Auth

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import importlib
import logging

# ===== Logging Setup =====
log = logging.getLogger("predictwell")
logging.basicConfig(level=logging.INFO)

# ===== FastAPI App =====
app = FastAPI(
    title="PredictWell API",
    version="1.0.0",
    description="Backend API for PredictWell Health.ai — Eldercare, Athletics (Pitcher AI), Sleep, and Auth.",
)

# ===== CORS (open for now; restrict later) =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with ["https://predictwellhealth.ai"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Root Routes =====
@app.get("/")
def root():
    return {"message": "PredictWell API running. See /docs for details."}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# ===== Dynamic Router Loader =====
def _load_router(module_candidates, attr_name="router"):
    """
    Try importing a router from several module paths.
    Returns the router or None if not importable.
    """
    for mod in module_candidates:
        try:
            m = importlib.import_module(mod)
            r = getattr(m, attr_name)
            log.info(f"Loaded router from {mod}.{attr_name}")
            return r
        except Exception as e:
            log.warning(f"Router not found at {mod}.{attr_name}: {e}")
    return None

# ===== Eldercare (Always Present) =====
eldercare_router = _load_router(["backend.eldercare", "eldercare"])
if eldercare_router:
    app.include_router(eldercare_router)
else:
    log.error("Eldercare router missing; /eldercare/checkin will not be available.")

# ===== Athletics (Pitcher AI — Always Present) =====
athletics_router = _load_router(["backend.app_athletics", "app_athletics"])
if athletics_router:
    app.include_router(athletics_router)
else:
    log.error("Athletics router missing; /athletics/risk will not be available.")

# ===== Sleep Sentinel (Optional) =====
sleep_router = _load_router(["backend.sleep", "sleep"])
if sleep_router:
    app.include_router(sleep_router)
else:
    log.info("Sleep router not found — skipping Sleep Sentinel module.")

# ===== Auth (Optional) =====
auth_router = _load_router(["backend.auth", "auth"])
if auth_router:
    app.include_router(auth_router)
else:
    log.info("Auth router not found — skipping authentication module.")

# ===== Startup Confirmation =====
log.info("PredictWell backend initialized successfully.")
