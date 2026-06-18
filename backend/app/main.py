from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import engine, Base
from app.api import categories, transactions, rules, envelopes, market, hermes


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="FinanceMacro API", version="0.1.0", lifespan=lifespan)

app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(rules.router)
app.include_router(envelopes.router)
app.include_router(market.router)
app.include_router(hermes.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
