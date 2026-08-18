# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

# Ensure database tables exist before running any tests
init_db()

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_search_endpoint_validation():
    response = client.post("/search", json={"query": ""})
    assert response.status_code == 422


def test_search_endpoint_valid_request():
    response = client.post("/search", json={
        "query": "running shoes",
        "top_k": 3
    })
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["query"] == "running shoes"
    # Note: results may be empty in CI since we don't seed data,
    # that's fine — we're testing the endpoint WORKS, not that
    # specific products exist


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"