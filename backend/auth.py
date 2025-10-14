# backend/auth.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterInput(BaseModel):
    email: str
    password: str

class LoginInput(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(payload: RegisterInput):
    return {"ok": True, "message": "Registered (demo)", "email": payload.email}

@router.post("/login")
def login(payload: LoginInput):
    return {"ok": True, "message": "Logged in (demo)", "email": payload.email}
