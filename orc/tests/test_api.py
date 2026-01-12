"""Simple API test (skeleton)."""
import pytest

# Skip if fastapi is not installed
pytest.importorskip("fastapi")

# Note: orc.api has been archived - this test is disabled
pytest.skip("API module archived - test disabled", allow_module_level=True)

# from fastapi.testclient import TestClient
# from orc.api.server import app


def test_health():
    # client = TestClient(app)
    # r = client.get("/health")
    # assert r.status_code == 200
    pytest.skip("API module archived")
