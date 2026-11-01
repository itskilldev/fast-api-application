import os

# Use an isolated SQLite DB for tests (must be set before the app is imported)
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["ANTHROPIC_API_KEY"] = ""

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def auth_headers(client, username="alice", password="secret123"):
    client.post("/auth/register", json={"username": username, "password": password})
    r = client.post("/auth/login", data={"username": username, "password": password})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_register_login_and_me(client):
    h = auth_headers(client)
    r = client.get("/auth/me", headers=h)
    assert r.status_code == 200 and r.json()["username"] == "alice"


def test_duplicate_register_and_bad_login(client):
    client.post("/auth/register", json={"username": "bob", "password": "secret123"})
    dup = client.post("/auth/register", json={"username": "bob", "password": "secret123"})
    assert dup.status_code == 409
    bad = client.post("/auth/login", data={"username": "bob", "password": "wrong"})
    assert bad.status_code == 401


def test_notes_require_auth(client):
    assert client.get("/notes").status_code == 401


def test_notes_crud(client):
    h = auth_headers(client)
    created = client.post("/notes", json={"title": "First", "content": "Hello world."}, headers=h)
    assert created.status_code == 201
    nid = created.json()["id"]

    assert len(client.get("/notes", headers=h).json()) == 1
    assert client.get(f"/notes/{nid}", headers=h).json()["title"] == "First"

    updated = client.put(f"/notes/{nid}", json={"title": "Edited"}, headers=h)
    assert updated.json()["title"] == "Edited" and updated.json()["content"] == "Hello world."

    assert client.delete(f"/notes/{nid}", headers=h).status_code == 204
    assert client.get(f"/notes/{nid}", headers=h).status_code == 404


def test_users_cannot_access_each_others_notes(client):
    a = auth_headers(client, "alice")
    b = auth_headers(client, "bruno")
    nid = client.post("/notes", json={"title": "Private", "content": "Mine"}, headers=a).json()["id"]
    assert client.get(f"/notes/{nid}", headers=b).status_code == 404
    assert client.delete(f"/notes/{nid}", headers=b).status_code == 404


def test_ai_summarize_text_and_note(client):
    h = auth_headers(client)
    text = "FastAPI is a modern web framework. It is built on Starlette. It is fast. It is easy to learn."
    r = client.post("/ai/summarize", json={"text": text}, headers=h)
    assert r.status_code == 200
    assert r.json()["provider"] == "local-fallback"
    assert r.json()["summary"].startswith("FastAPI is a modern web framework.")

    nid = client.post("/notes", json={"title": "AI", "content": text}, headers=h).json()["id"]
    summarized = client.post(f"/ai/notes/{nid}/summarize", headers=h)
    assert summarized.status_code == 200 and summarized.json()["summary"]


def test_frontend_is_served(client):
    r = client.get("/ui/")
    assert r.status_code == 200 and "Daybook" in r.text
