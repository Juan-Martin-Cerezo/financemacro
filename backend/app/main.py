import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import accounts, categories, envelopes, hermes, market, rules, transactions
from app.core.database import async_session_factory, engine, Base
from app.services.netting_engine import NettingEngine

logger = logging.getLogger(__name__)

NETTING_POLL_INTERVAL_SECONDS = 3600  # 1 hour


async def netting_worker():
    """Background loop: close expired netting groups every hour across all users."""
    while True:
        try:
            async with async_session_factory() as db:
                # Close expired groups for all users (empty string = wildcard scope)
                engine_svc = NettingEngine(db, user_id="")  # user_id unused in this variant
                stmt = "SELECT DISTINCT user_id FROM event_groups WHERE status = 'open'"
                result = await db.execute(stmt)
                user_ids = [row[0] for row in result.fetchall()]

                for uid in user_ids:
                    try:
                        e = NettingEngine(db, uid)
                        closed = await e.close_expired_groups()
                        if closed:
                            logger.info("Netting worker: closed %d groups for user %s", len(closed), uid)
                    except Exception as exc:
                        logger.error("Netting worker error for user %s: %s", uid, exc)

                await db.commit()
        except Exception as exc:
            logger.error("Netting worker cycle error: %s", exc)

        await asyncio.sleep(NETTING_POLL_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    task = asyncio.create_task(netting_worker(), name="netting-worker")

    yield

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    await engine.dispose()


app = FastAPI(title="FinanceMacro API", version="0.1.0", lifespan=lifespan)

app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(rules.router)
app.include_router(envelopes.router)
app.include_router(market.router)
app.include_router(hermes.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
