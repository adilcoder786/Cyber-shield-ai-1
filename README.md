# 🛡️ CyberShield AI

**AI-powered phishing, message, and file risk detection platform**
Built for **DevHack IIMTU 2026 — Build for Impact**

CyberShield AI scans URLs, emails/messages, and uploaded files, and returns a
**Safe / Suspicious / Malicious** verdict with a **0–100 risk score** and a
plain-English explanation of *why* — combining transparent rule-based
heuristics with scikit-learn models, and (optionally) live threat
intelligence from Google Safe Browsing / VirusTotal.

> **Fully working MVP** — real FastAPI backend, real MySQL database, a
> trained ML engine, and a React dashboard, all wired together. Runs
> completely **offline** for hackathon demos (no internet or API keys
> required) and upgrades automatically to live threat intel when keys are
> added.

---

## Table of contents

1. [Why this matters](#why-this-matters)
2. [Feature list](#feature-list)
3. [Architecture](#architecture)
4. [Tech stack](#tech-stack)
5. [Project structure](#project-structure)
6. [Quick start](#quick-start)
7. [Full setup (MySQL)](#full-setup-mysql)
8. [Docker setup (one command)](#docker-setup-one-command)
9. [Environment variables](#environment-variables)
10. [API reference](#api-reference)
11. [How the risk engine works](#how-the-risk-engine-works)
12. [Demo script for judges](#demo-script-for-judges)
13. [Security practices used in this project](#security-practices-used-in-this-project)
14. [Roadmap](#roadmap)

---

## Why this matters

Phishing is the entry point for the vast majority of breaches and ransomware
attacks. Most people have no easy way to check a suspicious link, email, or
downloaded file before it's too late — antivirus engines are heavyweight,
and enterprise threat-intel tools aren't built for individuals, students, or
small teams. CyberShield AI gives anyone a **fast, explainable, three-in-one
risk check** they can run in seconds, entirely in the browser.

## Feature list

| # | Feature | Status |
|---|---|---|
| 1 | Professional cybersecurity dashboard with live charts | ✅ |
| 2 | URL / website phishing scanner | ✅ |
| 3 | Phishing email / message / SMS analyzer | ✅ |
| 4 | File risk analyzer (malware disguise detection) | ✅ |
| 5 | AI-based risk scoring (rule engine + ML ensemble) | ✅ |
| 6 | Explainable results (human-readable reasons, not a black box) | ✅ |
| 7 | Scan history with search, filters, and pagination | ✅ |
| 8 | Threat statistics & trend charts | ✅ |
| 9 | Fully responsive UI (desktop + mobile) | ✅ |
| 10 | Loading states, validation, centralized error handling | ✅ |
| 11 | Optional live threat intel (Google Safe Browsing / VirusTotal) | ✅ |
| 12 | Runs fully offline for demos, no API keys required | ✅ |

## Architecture

```
 React Frontend                       FastAPI Backend
 (Vite + Tailwind)     HTTPS/JSON     ------------------------------
 Dashboard, Scanners  <----------->   Detection Engine
 History, Charts                        url_analyzer.py
                                         message_analyzer.py
                                         file_analyzer.py
                                         risk_scorer.py
                                                |
                                                v
                                      ML Models (scikit-learn)
                                         url_model.joblib
                                         message_model.joblib
                                                |
                                                v
                                      Threat Intel (optional)
                                         Google Safe Browsing
                                         VirusTotal
                                                |
                                                v  SQLAlchemy
                                      MySQL Database
                                         `scans` table
```

Every scan runs through the same pipeline regardless of type:
**extract features → score with rules → score with ML → blend → check threat
intel (if configured) → assign verdict + confidence → save to DB → return
explanation.**

## Tech stack

- **Frontend:** React 18, React Router, Tailwind CSS, Recharts, Axios, Lucide icons
- **Backend:** Python 3.12, FastAPI, Uvicorn, Pydantic
- **Database:** MySQL 8 (via SQLAlchemy + PyMySQL) — SQLite fallback for offline demos
- **ML/Security:** scikit-learn (RandomForest for URLs, TF-IDF + Logistic Regression for messages), custom URL/file/text feature engineering
- **Threat Intel:** Google Safe Browsing API, VirusTotal API (both optional)
- **Containerization:** Docker + docker-compose

## Project structure

```
cybershield-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI entrypoint, middleware, error handling
│   │   ├── config.py               # env-based settings
│   │   ├── database.py             # SQLAlchemy engine/session
│   │   ├── models.py               # Scan ORM model
│   │   ├── schemas.py              # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── url_scan.py
│   │   │   ├── message_scan.py
│   │   │   ├── file_scan.py
│   │   │   ├── history.py
│   │   │   └── stats.py
│   │   ├── engine/
│   │   │   ├── url_analyzer.py     # rule-based + ML URL analysis
│   │   │   ├── message_analyzer.py # rule-based + ML message analysis
│   │   │   ├── file_analyzer.py    # extension/magic-byte/entropy analysis
│   │   │   ├── risk_scorer.py      # shared verdict/confidence logic
│   │   │   └── threat_intel.py     # optional external API integrations
│   │   └── ml/
│   │       ├── url_features.py     # feature extraction shared by rules + ML
│   │       ├── train_model.py      # trains & saves both ML models
│   │       ├── url_model.joblib     # pre-trained (generated)
│   │       └── message_model.joblib # pre-trained (generated)
│   ├── seed_data.py                # populates realistic demo scan history
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/client.js           # Axios wrapper, all API calls
│   │   ├── components/             # Sidebar, Topbar, RiskGauge, ScanResultPanel, ...
│   │   ├── pages/                  # Dashboard, UrlScanner, MessageAnalyzer, FileAnalyzer, History
│   │   ├── App.jsx
│   │   └── index.css
│   ├── package.json
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── .env.example
├── database/
│   └── schema.sql                  # MySQL schema + sample rows
├── docker-compose.yml
└── README.md
```

## Quick start

The fastest way to see it working (no MySQL install required):

```bash
# 1. Backend
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# open .env and set: USE_SQLITE_FALLBACK=true
python -m app.ml.train_model      # trains the ML models (~10 seconds)
python seed_data.py               # populates realistic demo history
uvicorn app.main:app --reload --port 8000

# 2. Frontend (new terminal)
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open **http://localhost:5173** — the dashboard, scanners, and history will
all be live and populated with demo data.

## Full setup (MySQL)

```bash
# 1. Create the database (or let the app auto-create tables on first boot)
mysql -u root -p < database/schema.sql

# 2. Configure backend/.env
DB_HOST=localhost
DB_PORT=3306
DB_USER=cybershield_user
DB_PASSWORD=change-this-password
DB_NAME=cybershield_ai
USE_SQLITE_FALLBACK=false

# 3. Install, train, seed, run — same as Quick Start above
cd backend
pip install -r requirements.txt
python -m app.ml.train_model
python seed_data.py
uvicorn app.main:app --reload --port 8000

# 4. Frontend — same as Quick Start above
```

## Docker setup (one command)

```bash
cp backend/.env.example backend/.env   # edit DB_PASSWORD if desired
docker compose up --build
```

This starts MySQL, the backend (auto-trains ML models during image build),
and the frontend, all networked together. Then seed demo data:

```bash
docker compose exec backend python seed_data.py
```

Open **http://localhost:5173**.

## Environment variables

See `backend/.env.example` and `frontend/.env.example` for the full list.
Key ones:

| Variable | Purpose | Required? |
|---|---|---|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | MySQL connection | Yes (or use `USE_SQLITE_FALLBACK=true`) |
| `USE_SQLITE_FALLBACK` | Skip MySQL entirely, use a local SQLite file | No — demo convenience only |
| `GOOGLE_SAFE_BROWSING_API_KEY` | Enables live URL reputation checks | No — falls back to offline heuristics |
| `VIRUSTOTAL_API_KEY` | Enables live file-hash reputation checks | No — falls back to offline heuristics |
| `ALLOWED_ORIGINS` | CORS allow-list for the frontend | Yes |
| `SECRET_KEY` | App secret (rotate before production use) | Yes |
| `VITE_API_URL` | Backend URL the frontend calls | Yes |

**No API keys are required to run or demo this project.** Every external
integration is wrapped in a try/except that degrades gracefully to the
offline heuristic + ML engine, by design — see `engine/threat_intel.py`.

## API reference

Interactive Swagger docs are auto-generated at **`/docs`** once the backend
is running (e.g. `http://localhost:8000/docs`).

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/scan/url` | Scan a URL — `{ "url": "..." }` |
| `POST` | `/api/scan/message` | Scan a message — `{ "content": "...", "channel": "email", "sender": "..." }` |
| `POST` | `/api/scan/file` | Scan a file — multipart form, field `file` |
| `GET` | `/api/history` | Paginated scan history — `?page=&page_size=&scan_type=&verdict=&search=` |
| `GET` | `/api/history/{id}` | Full detail for one scan |
| `DELETE` | `/api/history/{id}` | Delete a scan record |
| `GET` | `/api/stats/summary` | Dashboard aggregate stats + 7-day trend + top indicators |
| `GET` | `/api/health` | Health check |

## How the risk engine works

**URLs** — 19 engineered features (IP-address hosts, `@` tricks, punycode,
brand impersonation, suspicious TLDs, entropy, shorteners, etc.) are scored
by transparent rules (for the explanation) *and* fed into a trained
RandomForest classifier. The two scores are blended, then boosted if Google
Safe Browsing flags the URL.

**Messages** — Rule-based NLP checks for urgency language, requests for
sensitive data (passwords, OTPs, card numbers), prize/refund bait, generic
greetings, and threats — combined with a TF-IDF + Logistic Regression text
classifier. Any links found inside the message are automatically extracted
and re-scanned through the URL engine.

**Files** — Static, execution-free checks: extension risk category,
double-extension disguises (`invoice.pdf.exe`), **magic-byte vs. extension
mismatch** (catches an executable renamed to look like a PDF), Shannon
entropy (flags packed/encrypted payloads), and embedded suspicious
string/command scanning — optionally cross-checked against VirusTotal by
file hash.

All three pipelines funnel into one shared `risk_scorer.py`, so every scan
type reports a consistent 0–100 score, verdict, and confidence.

> **Note on the ML models:** they're trained on synthetic, pattern-generated
> data (see `train_model.py`) so the whole project trains and runs fully
> offline with no external dataset downloads — ideal for a hackathon
> environment with unreliable venue wifi. Swap in a real labeled dataset
> (PhishTank, a SOC's own corpus, etc.) for production use; the
> training/serving code doesn't need to change.

## Demo script for judges

A ready-made demo flow using cases already seeded into the database — see
[`PITCH.md`](./PITCH.md) for the full 3-minute pitch script, and use the
**"Try:"** quick-example buttons on each scanner page for a live, on-stage
demo:

1. **Dashboard** — show the live charts (they're already populated by `seed_data.py`).
2. **URL Scanner** → click *"Phishing example"* → explain the risk score and reasoning.
3. **Message Analyzer** → click *"Prize scam"* → point out the embedded-link cross-check.
4. **File Analyzer** → click *"Download disguised file"*, then upload it → show the double-extension + magic-byte detection.
5. **History** → filter by *Malicious* to show everything caught so far.

## Security practices used in this project

- Environment-based secrets (`.env`, never committed) with `.env.example` templates
- Input validation on every endpoint via Pydantic
- File upload size limits and content-based (not extension-based) type checks
- Parameterized queries via SQLAlchemy ORM (no raw string SQL)
- CORS allow-list instead of wildcard origins
- Security response headers (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`)
- Centralized error handling that never leaks stack traces to the client
- Least-privilege MySQL application user (see `database/schema.sql`)
- External API calls wrapped with timeouts + safe fallback (never blocks or crashes on a flaky third-party API)

## Roadmap

- User accounts + team/organization workspaces
- Browser extension for real-time URL scanning while browsing
- Deeper file analysis (sandboxed macro/script execution tracing)
- Slack/Teams bot for scanning links shared in chat
- Fine-tuning ML models on a real labeled threat-intel dataset

---

Built for **DevHack IIMTU 2026 — Build for Impact**.
