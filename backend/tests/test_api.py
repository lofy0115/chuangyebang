import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_complaint_types():
    response = client.get("/api/complaint-types")
    assert response.status_code == 200
    assert "complaint_types" in response.json()

def test_analyze_valid_keyword():
    response = client.post("/api/analyze", json={"keyword": "母婴"})
    assert response.status_code == 200
    assert "industry" in response.json()

def test_analyze_invalid_keyword():
    response = client.post("/api/analyze", json={"keyword": "x"})
    assert response.status_code == 400