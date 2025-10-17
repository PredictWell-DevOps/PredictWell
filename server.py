# backend/server.py — resilient load (eldercare + optional sleep/auth)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import importlib
import logging

log = logging.getLogger("predictwell")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="PredictWell API",
    version="1.0.0",
    description="Backend API for PredictWell Health.ai — Eldercare, Sleep, Auth (optional).",
)

# CORS (open for now; restrict to https://predictwellhealth.ai later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "PredictWell API running. See /docs for details."}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

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

# Always present (your working endpoint)
eldercare_router = _load_router(["backend.eldercare", "eldercare"])
if eldercare_router:
    app.include_router(eldercare_router)
else:
    log.error("Eldercare router missing; /eldercare/checkin will not be available.")

# Optional routers — will load if the modules exist; otherwise skipped gracefully
sleep_router = _load_router(["backend.sleep", "sleep"])
if sleep_router:
    app.include_router(sleep_router)

auth_router = _load_router(["backend.auth", "auth"])
if auth_router:
    app.include_router(auth_router)
from app_athletics import router as athletics_router 
app.include_router(athletics_router) 
