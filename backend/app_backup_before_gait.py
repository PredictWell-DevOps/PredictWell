# backend/app_backup_before_gait.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


app = FastAPI(
    title="PredictWell API",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
)


class Echo(BaseModel):
    message: str


@app.get("/")
def root():
    return {"ok": True}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/api/echo")
def api_echo(payload: Echo):
    return payload.model_dump()


# Mount static if you keep a "static/" folder with assets.
app.mount("/static", StaticFiles(directory="static"), name="static")
