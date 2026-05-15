import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

client = TestClient(app)

def get_token():
    client.post("/auth/register", json={"username": "testuser", "password": "pass123"})
    res = client.post("/auth/login", json={"username": "testuser", "password": "pass123"})
    return res.json()["access_token"]

def auth_headers():
    return {"Authorization": f"Bearer {get_token()}"}

def test_register():
    res = client.post("/auth/register", json={"username": "alice", "password": "pass123"})
    assert res.status_code == 200
    assert res.json()["username"] == "alice"

def test_login():
    client.post("/auth/register", json={"username": "bob", "password": "pass123"})
    res = client.post("/auth/login", json={"username": "bob", "password": "pass123"})
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_create_task():
    res = client.post("/tasks/", json={"title": "Buy milk"}, headers=auth_headers())
    assert res.status_code == 200
    assert res.json()["title"] == "Buy milk"

def test_get_tasks():
    headers = auth_headers()
    client.post("/tasks/", json={"title": "Task 1"}, headers=headers)
    res = client.get("/tasks/", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1

def test_complete_task():
    headers = auth_headers()
    task = client.post("/tasks/", json={"title": "Test task"}, headers=headers).json()
    res = client.patch(f"/tasks/{task['id']}", json={"completed": True}, headers=headers)
    assert res.json()["completed"] is True

def test_delete_task():
    headers = auth_headers()
    task = client.post("/tasks/", json={"title": "Delete me"}, headers=headers).json()
    res = client.delete(f"/tasks/{task['id']}", headers=headers)
    assert res.json()["message"] == "Task deleted"
