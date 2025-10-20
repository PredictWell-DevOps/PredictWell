from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app_athletics import router as athletics_router

app = FastAPI(title="PredictWell Health.ai")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(athletics_router)

@app.get("/health")
def health():
    return {"status": "healthy"}
