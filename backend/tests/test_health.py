# backend/tests/test_health.py
from fastapi.testclient import TestClient
from app import app  # app is defined in backend/app.py; pytest runs from backend/

client = TestClient(app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
