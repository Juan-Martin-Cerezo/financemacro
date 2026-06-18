from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy import extract, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.auth import verify_jwt
from app.core.database import get_db
from app.models.models import Envelope, Transaction
from app.schemas.transaction import TransactionCreate, TransactionRead
from app.services.netting_engine import NettingEngine
from app.services.receipt_parser import ReceiptParser
from app.services.rule_matcher import RuleMatcher
from app.services.telegram_notifier import TelegramNotifier

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


async def _notify_if_deficit(db: AsyncSession, user_id: str) -> None:
    """Check liquidity deficit and push Telegram alert if needed."""
    bal_stmt = select(Transaction).where(
        Transaction.user_id == user_id,
        Transaction.status != "absorbed",
    )
    txs = (await db.execute(bal_stmt)).scalars().all()
    net_balance = sum(t.amount for t in txs)

    env_stmt = select(Envelope).where(Envelope.user_id == user_id)
    envs = (await db.execute(env_stmt)).scalars().all()
    targets_total = sum(abs(e.target_amount or 0) for e in envs)

    if net_balance < targets_total and targets_total > 0:
        notifier = TelegramNotifier()
        await notifier.notify_liquidity_deficit(
            net_balance=float(net_balance),
            envelope_targets_total=float(targets_total),
            user_id=user_id,
        )


async def _process_and_persist(
    db: AsyncSession,
    tx: Transaction,
    user_id: str,
) -> None:
    matcher = RuleMatcher(db, user_id)
    await matcher.apply(tx)

    engine = NettingEngine(db, user_id)
    if tx.amount < 0:
        await engine.process_new_transaction(tx)
    elif tx.amount > 0:
        await engine.try_match_incoming(tx)

    db.add(tx)
    await db.commit()
    await db.refresh(tx)

    # Fire-and-forget deficit check (non-blocking)
    await _notify_if_deficit(db, user_id)


def _base_stmt(user_id: str):
    return (
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .options(selectinload(Transaction.category))
    )


@router.get("", response_model=list[TransactionRead])
async def list_transactions(
    month: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2000, le=2100),
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    uid = auth["user_id"]
    stmt = _base_stmt(uid)
    if month:
        stmt = stmt.where(extract("month", Transaction.transaction_date) == month)
    if year:
        stmt = stmt.where(extract("year", Transaction.transaction_date) == year)
    stmt = stmt.order_by(Transaction.transaction_date.desc())
    result = await db.execute(stmt)
    return list(result.unique().scalars().all())


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    body: TransactionCreate,
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    uid = auth["user_id"]
    tx = Transaction(user_id=uid, **body.model_dump(exclude_unset=True))
    await _process_and_persist(db, tx, uid)
    return tx


@router.post("/upload-receipt", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def upload_receipt(
    file: UploadFile = File(...),
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    uid = auth["user_id"]
    raw = await file.read()
    parser = ReceiptParser()
    parsed = await parser.parse(raw, file.filename or "", file.content_type or "")

    tx = Transaction(
        user_id=uid,
        amount=parsed["amount"],
        description=parsed["description"],
        transaction_date=parsed["transaction_date"],
        currency="ARS",
        raw_data=parsed.get("raw_data") or {},
    )
    await _process_and_persist(db, tx, uid)
    return tx


@router.post("/webhook/{provider}")
async def webhook_ingest(
    provider: str,
    payload: dict,
    db: AsyncSession = Depends(get_db),
):
    user_id = "system"
    amount = payload.get("amount", 0)
    tx = Transaction(
        user_id=user_id,
        amount=amount,
        description=payload.get("description", ""),
        transaction_date=payload.get("date"),
        raw_data=payload,
    )
    if user_id:
        await _process_and_persist(db, tx, user_id)
    else:
        db.add(tx)
        await db.commit()
        await db.refresh(tx)
    return {"status": "ok", "transaction_id": str(tx.id)}


@router.get("/netting", response_model=dict)
async def netting_balance(
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    uid = auth["user_id"]
    stmt = select(Transaction).where(Transaction.user_id == uid, Transaction.status != "absorbed")
    result = await db.execute(stmt)
    txs = result.scalars().all()
    total = sum(tx.amount for tx in txs)
    return {"user_id": uid, "net_balance": str(total), "transaction_count": len(txs)}
