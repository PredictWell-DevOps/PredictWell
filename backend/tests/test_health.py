from fastapi.testclient import TestClient
from backend.app import app

def test_healthz():
    client = TestClient(app)
    r = client.get("/healthz")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    # DB path can vary by GitHub runner, so only check filename
    assert "db" in data and data["db"].endswith("predictwell.db")
