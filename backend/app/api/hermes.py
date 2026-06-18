from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_m2m
from app.core.database import get_db
from app.models.models import Transaction

router = APIRouter(prefix="/api/v1/hermes", tags=["hermes"])


@router.get("/financial-context")
async def financial_context(
    auth: dict = Depends(verify_m2m),
    db: AsyncSession = Depends(get_db),
):
    """M2M endpoint — returns clean monthly snapshot for Hermes AI agent."""
    stmt = select(Transaction).order_by(Transaction.transaction_date.desc()).limit(200)
    result = await db.execute(stmt)
    txs = result.scalars().all()

    summary = {
        "total_transactions": len(txs),
        "total_income": sum(t.amount for t in txs if t.amount > 0),
        "total_expenses": sum(t.amount for t in txs if t.amount < 0),
        "recent": [
            {
                "id": str(t.id),
                "amount": str(t.amount),
                "currency": t.currency,
                "description": t.description,
                "date": t.transaction_date.isoformat(),
                "status": t.status.value,
            }
            for t in txs[:50]
        ],
    }
    return summary
