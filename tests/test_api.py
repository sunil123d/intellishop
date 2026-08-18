# tests/test_api.py
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Runs ONCE before any test, guaranteed.
    Explicitly creates tables and enables pgvector
    extension before anything else touches the database.
    """
    from app.database import init_db
    init_db()
    yield


@pytest.fixture(scope="session")
def client(setup_database):
    """Creates TestClient AFTER database is confirmed ready"""
    from app.main import app
    with TestClient(app) as c:
        yield c


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_search_endpoint_validation(client):
    response = client.post("/search", json={"query": ""})
    assert response.status_code == 422


def test_search_endpoint_valid_request(client):
    response = client.post("/search", json={
        "query": "running shoes",
        "top_k": 3
    })
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["query"] == "running shoes"


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"