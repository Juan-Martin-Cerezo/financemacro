# FinanceMacro

Modular financial control platform — passive expense tracking, netting engine for group payments, deterministic rule-based categorisation.

## Stack

- **Frontend:** Next.js 14 (App Router) + PWA (Web Share Target for receipt capture)
- **Backend:** FastAPI + SQLAlchemy (async) + Pydantic V2
- **Database:** PostgreSQL 17 (via Supabase)
- **Auth:** Supabase Auth (JWT) + M2M API key for Hermes agent
- **Infrastructure:** Serverless / PaaS
  - Backend → Render.com (web service)
  - Frontend → Vercel.com
  - Database → Supabase

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
├── render.yaml          # Render.com IaC
└── .env
```

## Deploy to Render.com (Backend)

1. Push repo to GitHub.

2. In [Render Dashboard](https://dashboard.render.com), click **New +** → **Blueprint**.

3. Connect your GitHub repo. Render reads `render.yaml` and auto-creates the web service.

4. In the Blueprint review screen, populate the following **Environment Variables** (click each one to edit):

   | Variable | Value |
   |----------|-------|
   | `DATABASE_URL` | Supabase transaction pooler URI: `postgresql+asyncpg://postgres.<PROJECT_REF>:<DB_PASSWORD>@aws-0-us-east-1.pooler.supabase.com:6543/postgres` |
   | `SUPABASE_URL` | `https://<PROJECT_REF>.supabase.co` |
   | `SUPABASE_ANON_KEY` | Your Supabase anon / publishable key |
   | `SUPABASE_SERVICE_ROLE_KEY` | Your Supabase service_role key (keep secret) |
   | `HERMES_API_KEY` | A random string for Hermes agent auth |
   | `SECRET_KEY` | A random string for JWT signing |
   | `TELEGRAM_BOT_TOKEN` | *(optional)* Telegram bot token |
   | `TELEGRAM_CHAT_ID` | *(optional)* Telegram chat ID |

5. Click **Apply**. Render deploys the backend.

   > **Finding your Supabase values:**
   > - Go to [Supabase Dashboard](https://supabase.com/dashboard) → your project → **Project Settings** → **Database** for the pooler URI.
   > - **Project Settings** → **API** for the URL, anon key, and service_role key.
   > - The pooler password is the one you set when creating the Supabase project.

## Deploy to Vercel.com (Frontend)

1. In [Vercel Dashboard](https://vercel.com), click **Add New** → **Project**.

2. Import your GitHub repo.

3. Set **Root Directory** to `frontend`.

4. **Framework Preset:** Next.js (auto-detected).

5. **Environment Variables:**

   | Variable | Value |
   |----------|-------|
   | `NEXT_PUBLIC_SUPABASE_URL` | `https://<PROJECT_REF>.supabase.co` |
   | `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Your Supabase anon / publishable key |
   | `NEXT_PUBLIC_API_URL` | Your Render backend URL, e.g. `https://financemacro-api.onrender.com` |

6. Click **Deploy**.

## Local Development

```bash
# 1. Clone & enter
git clone <repo-url>
cd financemacro

# 2. Install backend deps
cd backend
pip install -r requirements.txt

# 3. Configure .env (copy from .env.example)
cp .env.example .env
# Edit .env with your Supabase credentials (see Render table above)

# 4. Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Run frontend (separate terminal)
cd frontend
npm install
npm run dev
```

- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- Frontend: http://localhost:3000
