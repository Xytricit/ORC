"""Simple API test (skeleton)."""
from fastapi.testclient import TestClient
from orc.api.server import app


def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
