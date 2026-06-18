# FinanceMacro

Modular financial control platform — passive expense tracking, netting engine for group payments, deterministic rule-based categorisation.

## Stack

- **Frontend:** Next.js 14 (App Router) + PWA (Web Share Target for receipt capture)
- **Backend:** FastAPI + SQLAlchemy (async) + Pydantic V2
- **Database:** PostgreSQL 16
- **Auth:** Supabase Auth (JWT) + M2M API key for Hermes agent

## Quick Start

```bash
cp .env.example .env   # edit secrets
docker compose up -d
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
/financemacro
├── frontend/            # Next.js PWA
├── backend/
│   ├── api/             # FastAPI routers
│   ├── core/            # Config, DB, auth
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic (in/out)
│   └── services/        # NettingEngine, RuleMatcher
├── docker-compose.yml
└── .env
```
