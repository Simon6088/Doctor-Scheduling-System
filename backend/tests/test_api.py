from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Doctor Scheduling System API is running"

def test_health_db():
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
