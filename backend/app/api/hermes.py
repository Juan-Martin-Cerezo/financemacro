import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_m2m
from app.core.database import get_db
from app.models.models import Transaction
from app.schemas.hermes import ExecuteActionRequest, ExecuteActionResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/hermes", tags=["hermes"])


@router.get("/financial-context")
async def financial_context(
    auth: dict = Depends(verify_m2m),
    db: AsyncSession = Depends(get_db),
):
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


@router.post("/execute-action", response_model=ExecuteActionResponse)
async def execute_action(
    body: ExecuteActionRequest,
    auth: dict = Depends(verify_m2m),
):
    """AI action dispatcher stub — receives structured commands from Hermes agent.

    Currently acknowledges all actions. Future: route to actual service logic.
    """
    allowed_actions = {"allocate_funds", "re_categorize", "create_envelope", "close_group"}

    if body.action not in allowed_actions:
        logger.warning("Unknown action requested: %s", body.action)
        return ExecuteActionResponse(
            action=body.action,
            status="rejected",
            message=f"Unknown action '{body.action}'. Allowed: {sorted(allowed_actions)}",
        )

    logger.info("Action '%s' acknowledged with params=%s", body.action, body.params)
    return ExecuteActionResponse(
        action=body.action,
        status="acknowledged",
        message=f"Action '{body.action}' received. Processing stub — no side effects taken yet.",
    )
