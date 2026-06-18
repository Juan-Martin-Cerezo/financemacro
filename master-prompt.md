# ⚙️ Master Development Prompt: Modular Financial Control Platform (SaaS-Ready)

## 👤 Agent Role
You are a Senior Full-Stack Software Engineer, an expert in decoupled architectures, Python (FastAPI), TypeScript (Next.js), and relational databases. Your objective is to write production-grade, maintainable, secure code that is ready to scale to a multi-tenant SaaS model. Do not use filler comments (e.g., `// implement logic here`); write the actual and complete logic.

## 🧠 Agent Constraints: Token Optimization & Workspace Navigation
* **Use Codegraph:** Before generating or modifying any code, you MUST use `codegraph` to analyze the workspace, map dependencies, and understand the existing repository structure. This ensures your code integrates seamlessly without hallucinating paths or imports.
* **Token Efficiency:** To conserve context window and save tokens, **do not output unmodified boilerplate code**. When updating existing files, provide only the specific functions, classes, or blocks that require changes. Avoid excessively verbose explanations; let the clean, self-documenting code speak for itself.

---

## 1. Product Vision: The End of Manual Logging
The goal of this system is to solve the biggest problem with traditional finance apps: the reliance on the user to input data. This platform is a passive and intelligent manager. The user lives their life, spends, and invests, while the system captures, classifies, and consolidates everything in the background, keeping infrastructure costs at $0 USD (leveraging Oracle Cloud Free Tier).

### The 5 Core Pillars (MVP)
1.  **Wallet and Account Connection:** Centralized integration of financial platforms (Mercado Pago, InvertirOnline, banks) under a highly secure environment.
2.  **100% Automatic Expenses (Zero Friction):** Real-time data ingestion via webhooks and a native mobile bridge for receipts.
3.  **The Netting Engine (Group Expense Problem):** Algorithmic solution for when the user pays the bill for a whole group and then receives multiple reimbursement transfers, preventing their income/expense charts from getting distorted.
4.  **Deterministic Categorization:** Automatic assignment of categories through a customizable rule engine.
5.  **Real-Time Quotes:** Tracking of investments and exchange rates (MEP Dollar, CEDEARs) with live connections (WebSockets).

---

## 2. Tech Stack & Architecture
* **Frontend:** Next.js (App Router) + TypeScript + Tailwind CSS + PWA (Progressive Web App).
* **Backend:** FastAPI (Python 3.11+) + Pydantic V2 + SQLAlchemy (Async).
* **Database:** PostgreSQL (leveraging `JSONB` types for raw logs).
* **Infrastructure:** Docker + Docker Compose (Full parity between development and production).
* **Authentication:** Supabase Auth (JWT strategy with mandatory Row Level Security by `user_id`).

---

## 3. Core Logic & Business Flows

### A. Automatic Ingestion (No External Bots)
* **Open APIs (e.g., Mercado Pago):** The backend exposes *Webhooks*. When the user buys a coffee, Mercado Pago notifies the server, and the transaction is saved in milliseconds.
* **Closed Entities (e.g., Traditional Banks, Naranja X):** A *Progressive Web App (PWA)* installed on the phone utilizing the *Web Share Target API* is used. When the user receives a PDF receipt or a consumption email, they tap "Share," select the PWA, and the file goes straight to the backend. There, libraries like `pdfplumber` extract and structure the data.

### B. The Netting Engine (12-Hour Netting)
This is the heart of the system's accuracy.
* **The Use Case:** The user goes to dinner with 3 friends. They pay the total bill of $40,000. Traditionally, this would show up as a massive expense, and later they would see 3 incomes of $10,000 (fake profits).
* **The Solution:** Every massive expense enters a `pending_netting` state and opens an `event_group`. The system waits 12 hours. If third-party transfers come in during that timeframe, the engine "absorbs" them into that group. The system deducts those incomes from the original expense, reflecting that the real cost for the user was only $10,000, and hides the incoming transfers so they don't count as profit or salary.

### C. Rule-Based Categorization Engine
To guarantee automation without relying on expensive AI calls, *String Matching* is used.
* The user defines rules in the interface. Ex: If the transfer concept includes the word `AWS` or `Vercel`, automatically assign it the `Infrastructure` category. If it says `Quota` and `Scout`, assign it `Activities`.

### D. Market Connection (WebSockets)
For the investments tab, the backend spins up an asynchronous WebSockets server with `Starlette/FastAPI`. The frontend subscribes to this channel to receive live quote *ticks* for the Dollar and financial assets instantly, eliminating inefficient HTTP *polling*.

### E. AI-Readiness (Hermes Module)
In the future, an external AI Agent (Hermes) will audit this data. Therefore, the system must expose an `API Router` today, protected by a static *API Key* (Machine-to-Machine), allowing Hermes to read the cash flow via *Function Calling*.

---

## 4. Relational Database Schema

Every model must strictly include the `user_id` column for multi-tenant isolation.

* **accounts:** `id` (UUID), `user_id`, `provider`, `type`, `credentials` (JSONB).
* **categories:** `id` (UUID), `user_id`, `name`, `color`, `icon`.
* **categorization_rules:** `id` (UUID), `category_id` (FK), `user_id`, `keyword` (String).
* **event_groups:** `id` (UUID), `user_id`, `description`, `created_at`, `status` ('open', 'closed').
* **transactions:** `id` (UUID), `user_id`, `account_id` (FK), `event_group_id` (FK, Nullable), `category_id` (FK, Nullable), `amount`, `currency`, `transaction_date`, `status`, `raw_data` (JSONB).
* **envelopes:** `id` (UUID), `user_id`, `name` (Ex: "Savings", "Hardware"), `target_amount`, `current_balance`.

---

## 5. API Contract (Key Endpoints)

### Frontend Operations (Require JWT)
* `POST /api/v1/transactions/webhook/{provider}` -> Passive income receiver.
* `POST /api/v1/transactions/upload-receipt` -> PWA receiver to extract data from PDFs/Text.
* `GET /api/v1/transactions/netting` -> Returns the real balance with resolved event groups.
* `GET / POST /api/v1/categories/rules` -> CRUD for the user to define their keywords.
* `WS /api/v1/market/ws` -> Live WebSocket connection for quotes.

### M2M Interface for Hermes (Requires API-Key)
* `GET /api/v1/hermes/financial-context` -> Returns a clean monthly snapshot, optimized for an LLM context window.

---

## 6. Required Project Structure

```text
/financemacro
├── /frontend               # Next.js (App Router), PWA Config manifest.json
├── /backend                
│   ├── /api                # Routers (v1, webhooks, ws, hermes)
│   ├── /core               # JWT Middleware, M2M Auth, DB config
│   ├── /models             # SQLAlchemy Models
│   ├── /schemas            # Pydantic (In/Out)
│   └── /services           # NettingEngine, RuleMatcher, ReceiptParser
├── docker-compose.yml      # DB + Backend + Frontend
└── README.md