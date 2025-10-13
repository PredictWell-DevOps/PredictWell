import os, hashlib
from datetime import datetime, timedelta
from typing import Tuple
import jwt
from passlib.hash import argon2

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change")
JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET", "dev-refresh-change")

ACCESS_TTL_MIN = 30
REFRESH_TTL_DAYS = 14

def hash_password(p: str) -> str:
    return argon2.hash(p)

def verify_password(p: str, ph: str) -> bool:
    return argon2.verify(p, ph)

def make_access_token(sub: str, role: str, sentinel: str) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": sub,
        "role": role,
        "sentinel": sentinel,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TTL_MIN)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def make_refresh_token(sub: str) -> Tuple[str, datetime]:
    now = datetime.utcnow()
    exp = now + timedelta(days=REFRESH_TTL_DAYS)
    payload = {"sub": sub, "iat": int(now.timestamp()), "exp": int(exp.timestamp()), "typ": "refresh"}
    return jwt.encode(payload, JWT_REFRESH_SECRET, algorithm="HS256"), exp

def decode_access(t: str) -> dict:
    return jwt.decode(t, JWT_SECRET, algorithms=["HS256"])

def decode_refresh(t: str) -> dict:
    return jwt.decode(t, JWT_REFRESH_SECRET, algorithms=["HS256"])

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
