# server.py — PredictWell Health.ai unified backend
# Includes: Eldercare, Athletics (Pitcher AI), Sleep, Auth

from __future__ import annotations

import importlib
import logging
import os
from logging.config import dictConfig
from typing import Iterable, List, Optional

from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi.middleware.cors import CORSMiddleware

# ===== Logger =====
log = logging.getLogger("predictwell")


# ===== Logging Configuration =====
def configure_logging() -> None:
    """Configure structured logging if not already configured.

    - Uses LOG_LEVEL env var (default: INFO)
    - Avoids clobbering existing root handlers (e.g., when run under uvicorn)
    """
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    # If root has handlers (e.g., uvicorn already configured), don't reconfigure.
    if logging.getLogger().handlers:
        log.setLevel(level_name)
        return

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": level_name,
                }
            },
            "root": {
                "handlers": ["console"],
                "level": level_name,
            },
        }
    )


# ===== Utility: CORS origins parsing =====
def _parse_csv_env(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def _sanitize_cors_origins(origins: List[str], allow_credentials: bool) -> List[str]:
    """Ensure we don't return wildcard origins when credentials are allowed."""
    if allow_credentials and ("*" in origins or origins == ["*"]):
        log.warning(
            "CORS: '*' is not permitted when allow_credentials=True. Falling back to localhost defaults."
        )
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    return origins or [
        # Safe development defaults
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


# ===== Dynamic Router Loader =====
def _load_router(
    module_candidates: Iterable[str],
    attr_name: str = "router",
    debug: bool = False,
) -> Optional[APIRouter]:
    """Try importing an APIRouter named `attr_name` from several module paths.

    Returns the router or None if not importable.
    Only ImportError/AttributeError are treated as expected skipping conditions.
    Any other exceptions are logged as errors and skipped.
    """
    for mod in module_candidates:
        try:
            m = importlib.import_module(mod)
        except ImportError as e:
            # Expected: module may not exist depending on deployment.
            log.debug(f"Router module import failed for {mod}: {e}")
            continue

        try:
            r = getattr(m, attr_name)
        except AttributeError:
            log.debug(f"Router attribute '{attr_name}' not found in {mod}")
            continue

        if not isinstance(r, APIRouter):
            log.error(f"{mod}.{attr_name} is not a fastapi.APIRouter; got {type(r).__name__}")
            continue

        log.info(f"Loaded router from {mod}.{attr_name}")
        return r

    # If here, no router could be loaded.
    return None


# ===== App Factory =====

def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="PredictWell API",
        version="1.0.0",
        description=(
            "Backend API for PredictWell Health.ai — Eldercare, Athletics (Pitcher AI), Sleep, and Auth."
        ),
    )

    # CORS configuration (env-driven)
    allow_credentials = os.getenv("ALLOW_CREDENTIALS", "true").lower() == "true"
    env_origins = _parse_csv_env(os.getenv("ALLOWED_ORIGINS"))
    allowed_origins = _sanitize_cors_origins(env_origins, allow_credentials)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes — prefer async endpoints for consistency
    @app.get("/")
    async def root():
        return {"message": "PredictWell API running. See /docs for details."}

    @app.get("/healthz")
    async def healthz():
        # Include resolved DB path to help runners/tests determine which DB file is used.
        try:
            from db import DB_PATH
        except Exception:
            DB_PATH = "unknown"
        return {"status": "ok", "db": DB_PATH}

    # Dynamic router loading
    debug_env = os.getenv("DEBUG", "false").lower() == "true" or logging.getLogger().isEnabledFor(
        logging.DEBUG
    )

    # Required modules — fail fast if missing
    required_missing: List[str] = []

    eldercare_router = _load_router(["backend.eldercare", "eldercare"], debug=debug_env)
    if eldercare_router:
        app.include_router(eldercare_router)
    else:
        log.error(
            "Eldercare router missing; /eldercare/checkin will not be available (required)."
        )
        required_missing.append("eldercare")

    athletics_router = _load_router(["backend.app_athletics", "app_athletics"], debug=debug_env)
    if athletics_router:
        app.include_router(athletics_router)
    else:
        log.error(
            "Athletics router missing; /athletics/risk will not be available (required)."
        )
        required_missing.append("athletics")

    # Optional modules — log at info
    sleep_router = _load_router(["backend.sleep", "sleep"], debug=debug_env)
    if sleep_router:
        app.include_router(sleep_router)
    else:
        log.info("Sleep router not found — skipping Sleep Sentinel module.")

    auth_router = _load_router(["backend.auth", "auth"], debug=debug_env)
    if auth_router:
        app.include_router(auth_router)
    else:
        log.info("Auth router not found — skipping authentication module.")

    if required_missing:
        # Fail fast to avoid running a half-functional API while claiming modules are 'Always Present'
        missing = ", ".join(required_missing)
        raise RuntimeError(f"Required routers missing: {missing}")

    # Startup confirmation moved to lifecycle event
    @app.on_event("startup")
    async def _startup_log() -> None:
        log.info("PredictWell backend initialized successfully.")

    return app


# Expose ASGI app for servers like uvicorn/gunicorn
app = create_app()
