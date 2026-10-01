from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


def test_create_and_get_task():
    r = client.post("/tasks", json={"title": "learn devops"})
    assert r.status_code == 201
    task_id = r.json()["id"]

    r = client.get(f"/tasks/{task_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "learn devops"


def test_get_missing_task():
    r = client.get("/tasks/9999")
    assert r.status_code == 404
