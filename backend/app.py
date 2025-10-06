from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI(
    title="PredictWell API",
    docs_url="/docs",        # interactive Swagger UI
    redoc_url=None,
    openapi_url="/openapi.json"
)

# --- CORS (allow your frontend to call the API) ---
# For strict security, replace "*" with your exact Render static site URL.
# e.g., ["https://predictwell-frontend.onrender.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # TODO: tighten to your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Health & meta routes ---
@app.get("/", tags=["meta"])
def root():
    return {"service": "predictwell-backend", "status": "ok"}

@app.get("/healthz", tags=["health"])
def healthz():
    return {"status": "ok"}

# --- Example API route (optional) ---
class Echo(BaseModel):
    message: str

@app.post("/api/echo", tags=["demo"])
def echo(payload: Echo):
    return {"echo": payload.message}

# --- Local run (Render uses a process manager; this is for local dev) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
