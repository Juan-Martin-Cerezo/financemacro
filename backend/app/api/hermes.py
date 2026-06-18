import logging
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_m2m
from app.core.database import get_db
from app.models.models import Envelope, Transaction
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


ALLOWED_ACTIONS = {"allocate_funds", "re_categorize", "create_envelope", "close_group"}


@router.post("/execute-action", response_model=ExecuteActionResponse)
async def execute_action(
    body: ExecuteActionRequest,
    auth: dict = Depends(verify_m2m),
    db: AsyncSession = Depends(get_db),
):
    """AI action dispatcher — executes real DB operations for known actions."""

    if body.action not in ALLOWED_ACTIONS:
        return ExecuteActionResponse(
            action=body.action,
            status="rejected",
            message=f"Unknown action '{body.action}'. Allowed: {sorted(ALLOWED_ACTIONS)}",
        )

    if body.action == "allocate_funds":
        return await _handle_allocate_funds(body, db)

    logger.info("Action '%s' acknowledged (stub), params=%s", body.action, body.params)
    return ExecuteActionResponse(
        action=body.action,
        status="acknowledged",
        message=f"Action '{body.action}' acknowledged — no real side effects taken yet.",
    )


async def _handle_allocate_funds(
    body: ExecuteActionRequest,
    db: AsyncSession,
) -> ExecuteActionResponse:
    envelope_id_str = body.params.get("envelope_id")
    amount_str = body.params.get("amount")

    if not envelope_id_str or not amount_str:
        return ExecuteActionResponse(
            action="allocate_funds",
            status="rejected",
            message="Missing 'envelope_id' or 'amount' in params.",
        )

    try:
        envelope_id = UUID(envelope_id_str)
        amount = Decimal(str(amount_str))
    except (ValueError, TypeError) as e:
        return ExecuteActionResponse(
            action="allocate_funds",
            status="error",
            message=f"Invalid param format: {e}",
        )

    if amount <= 0:
        return ExecuteActionResponse(
            action="allocate_funds",
            status="rejected",
            message="Allocation amount must be positive.",
        )

    stmt = select(Envelope).where(Envelope.id == envelope_id)
    env = (await db.execute(stmt)).scalar_one_or_none()
    if not env:
        return ExecuteActionResponse(
            action="allocate_funds",
            status="error",
            message=f"Envelope {envelope_id} not found.",
        )

    env.current_balance += amount
    await db.commit()
    await db.refresh(env)

    logger.info(
        "Hermes M2M allocate_funds: envelope=%s amount=%s new_balance=%s",
        envelope_id, amount, env.current_balance,
    )

    return ExecuteActionResponse(
        action="allocate_funds",
        status="acknowledged",
        message=f"Allocated ${amount} to envelope '{env.name}'. New balance: ${env.current_balance}.",
    )
