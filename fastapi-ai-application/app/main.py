from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .routers import ai, auth, notes

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="FastAPI AI Application",
    description="REST API backend with JWT authentication, CRUD, AI integration and PostgreSQL. Dockerized.",
    version="1.0.0",
    lifespan=lifespan,
)

# Lets the UI work even if it is opened from VS Code Live Server (port 5500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(ai.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/ui/")


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


# Frontend: http://localhost:8000/ui/
app.mount("/ui", StaticFiles(directory=STATIC_DIR, html=True), name="ui")
