"""Simple API test (skeleton)."""
import pytest

# Skip if fastapi is not installed
pytest.importorskip("fastapi")

from fastapi.testclient import TestClient
from orc.api.server import app


def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
