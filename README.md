# Resume Analyzer

Local full-stack app that analyzes a resume against a job description using the
Gemini API. See [AGENTS.md](AGENTS.md) for the standing technical conventions.

**Current state:** resume-vs-JD analysis works end to end (KAN-5). Upload a
resume, supply a job description, and Gemini returns a fitment score plus
recommendations. Results are not yet persisted — every report lives only as
long as the page (KAN-6 adds SQLite storage and history).

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

> **Note (Python 3.14):** `google-genai` pulls in `cryptography`, which
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

## Using it

Open http://localhost:5173, choose a resume (`.pdf` or `.md`), paste the job
description or upload it as a file, and click **Analyze resume**. The report
shows a 0-100 fitment score with its tier, a summary, matched strengths,
missing keywords, skill gaps and recommended edits.

Bad file types, an empty job description and Gemini outages all surface as a
message above the report rather than a blank screen.

Checks from the shell:

```bash
curl http://localhost:8000/api/health       # {"status":"ok"}
curl http://localhost:8000/api/ping-gemini  # live Gemini reply

curl -F resume=@Resume.pdf \
     -F jd_text="$(cat 'Job Description.txt')" \
     http://localhost:8000/api/analyze
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Liveness check; does not call Gemini |
| GET | `/api/ping-gemini` | Sends a hardcoded prompt to Gemini and returns the reply |
| POST | `/api/analyze` | Analyzes a resume against a job description |

`POST /api/analyze` takes multipart form data:

| Field | Required | Notes |
|---|---|---|
| `resume` | yes | Resume file, `.pdf` or `.md`, max 5 MB |
| `jd_text` | see note | Job description as plain text |
| `jd_file` | see note | Job description file, `.pdf`, `.md` or `.txt` |

Supply the job description through either field; `jd_file` wins if both are
sent, and omitting both is a `400`. Unreadable uploads return `400`, Gemini
failures `502`.

## Layout

```
backend/
├── main.py                    # FastAPI entrypoint, env loading, CORS, routers
├── models.py                  # Pydantic request/response schemas
├── routes/
│   ├── ping.py                # /api/health, /api/ping-gemini
│   └── resume.py              # /api/analyze
├── services/
│   ├── gemini_client.py       # Gemini SDK wrapper + prompt construction
│   └── file_parser.py         # PDF/Markdown/text extraction + validation
├── requirements.txt
└── .env.example               # GEMINI_API_KEY placeholder
frontend/
├── src/api/                   # fetch wrappers to the backend
├── src/components/            # ResumeUploadForm, AnalysisReport, ReportSection
├── src/pages/ResumeReview.jsx # Upload form + report, wired to the API
├── src/App.jsx
└── vite.config.js
```
