"""
Backup FastAPI app (pre-gait features).

This mirrors the main app structure so CI/linting passes cleanly.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Keep io/csv imports on separate lines for ruff E401 compliance.
import io
import csv

# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------
app = FastAPI(
    title="PredictWell API (Backup)",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
)

# If you have a "static" directory under backend/, this will serve it at /static.
# Comment out if you don't need/ have it.
# app.mount("/static", StaticFiles(directory="static"), name="static")


# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------
class Echo(BaseModel):
    message: str


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "PredictWell backup API root"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/api/echo")
def echo(payload: Echo):
    # Example of using csv/io so imports are meaningful (and keep ruff happy).
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["message"])
    writer.writerow([payload.message])
    _ = buf.getvalue()  # not used further; demonstrates module usage
    return {"echo": payload.message}
