# Resume Analyzer

Local full-stack app that analyzes a resume against a job description using the
Gemini API. See [AGENTS.md](AGENTS.md) for the standing technical conventions.

**Current state:** project scaffolding only (KAN-4). The backend, frontend and
Gemini wiring are in place and verified end to end via a single smoke-test
endpoint. No upload, analysis, or database work yet.

## Prerequisites

- Python 3.11+
- Node.js 18+
- A Gemini API key — https://aistudio.google.com/app/apikey

## Setup

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env    # then add your real GEMINI_API_KEY
uvicorn main:app --reload
```

Backend serves on http://localhost:8000 (interactive docs at `/docs`).

> **Note (Python 3.14):** `google-generativeai` pulls in `cryptography`, which
> has no prebuilt wheel for some 3.14 builds and fails to compile from source.
> If `pip install -r requirements.txt` fails on `cryptography`, run
> `pip install --only-binary=:all: cryptography` first, then retry.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend serves on http://localhost:5173. It calls the backend at
`http://localhost:8000` by default; override with `VITE_API_BASE_URL` in
`frontend/.env` (see `frontend/.env.example`).

## Verifying the stack

Open http://localhost:5173 and click **Ping Gemini**. A successful call renders
the live Gemini reply along with the model name and the prompt that was sent.
If the key is missing or invalid the backend returns `502` and the UI shows the
error detail.

Equivalent check from the shell:

```bash
curl http://localhost:8000/api/health       # {"status":"ok"}
curl http://localhost:8000/api/ping-gemini  # live Gemini reply
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Liveness check; does not call Gemini |
| GET | `/api/ping-gemini` | Sends a hardcoded prompt to Gemini and returns the reply |

## Layout

```
backend/
├── main.py                    # FastAPI entrypoint, env loading, CORS, routers
├── models.py                  # Pydantic response schemas
├── routes/ping.py             # /api/health, /api/ping-gemini
├── services/gemini_client.py  # Gemini SDK wrapper + prompt construction
├── requirements.txt
└── .env.example               # GEMINI_API_KEY placeholder
frontend/
├── src/api/                   # fetch wrappers to the backend
├── src/components/            # GeminiPingCard
├── src/App.jsx
└── vite.config.js
```
