"""FastAPI entrypoint: env loading, CORS, router mounting."""

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(Path(__file__).parent / ".env")

# Imported after load_dotenv so services see the environment at call time.
from routes import ping, resume  # noqa: E402

app = FastAPI(title="Resume Analyzer API", version="0.1.0")

# Vite dev server runs on 5173; allow both hostname spellings.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ping.router)
app.include_router(resume.router)
