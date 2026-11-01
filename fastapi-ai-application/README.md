---
title: FastAPI AI Application
emoji: 📝
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# FastAPI AI Application

REST API backend with AI integration and a database.

**Features:** JWT authentication, CRUD, AI summarization, PostgreSQL, deployment with Docker.

**Stack:** Python · FastAPI · PostgreSQL · Docker · SQLAlchemy

## Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/auth/register` | Create an account | No |
| POST | `/auth/login` | Get a JWT access token | No |
| GET | `/auth/me` | Current user | Yes |
| POST | `/notes` | Create a note | Yes |
| GET | `/notes` | List your notes (`skip`, `limit`) | Yes |
| GET | `/notes/{id}` | Get one note | Yes |
| PUT | `/notes/{id}` | Update a note | Yes |
| DELETE | `/notes/{id}` | Delete a note | Yes |
| POST | `/ai/summarize` | Summarize any text | Yes |
| POST | `/ai/notes/{id}/summarize` | Summarize a note and save the summary | Yes |
| GET | `/health` | Health check | No |

Web app (frontend): `http://localhost:8000/ui/`  (open this, not the HTML file directly)

Interactive API docs: `http://localhost:8000/docs`

## Run with Docker (PostgreSQL)

```bash
cp .env.example .env      # set SECRET_KEY (and ANTHROPIC_API_KEY if you want real AI summaries)
docker compose up --build
```

Open http://localhost:8000/docs

## Run locally (without Docker)

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

This uses SQLite by default. Set `DATABASE_URL` to a PostgreSQL URL to use PostgreSQL.

## Run tests

```bash
pytest -q
```

## AI integration

If `ANTHROPIC_API_KEY` is set, summaries come from the Anthropic Messages API (model set by `AI_MODEL`).
Without a key, or if the API is unreachable, the app falls back to a simple local summarizer, so it always works.

## Quick example

```bash
curl -X POST localhost:8000/auth/register -H "Content-Type: application/json" \
  -d '{"username":"quratulain","password":"secret123"}'

TOKEN=$(curl -s -X POST localhost:8000/auth/login -d "username=quratulain&password=secret123" | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -X POST localhost:8000/notes -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"title":"First note","content":"FastAPI is fast. It is built on Starlette. It is easy to learn."}'
```

## Deploy (easiest: Hugging Face Spaces)

Create a new Space with SDK **Docker**, upload these files, and add a secret named `SECRET_KEY`. The app opens at `/ui/`.
Free Spaces use SQLite, so data resets when the Space restarts; use PostgreSQL (`DATABASE_URL`) for permanent data.

### Other hosts


Push to GitHub, then deploy the Docker image to Render, Railway or Fly.io with a managed PostgreSQL and these
environment variables: `DATABASE_URL`, `SECRET_KEY`, `ANTHROPIC_API_KEY` (optional).
