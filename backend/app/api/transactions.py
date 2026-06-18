from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_jwt
from app.core.database import get_db
from app.models.models import Transaction
from app.schemas.transaction import TransactionCreate, TransactionRead
from app.services.receipt_parser import ReceiptParser
from app.services.rule_matcher import RuleMatcher

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionRead])
async def list_transactions(
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    uid = auth["user_id"]
    stmt = select(Transaction).where(Transaction.user_id == uid).order_by(Transaction.transaction_date.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    body: TransactionCreate,
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    uid = auth["user_id"]
    tx = Transaction(user_id=uid, **body.model_dump(exclude_unset=True))
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return tx


@router.post("/upload-receipt", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def upload_receipt(
    file: UploadFile = File(...),
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    """PWA share_target endpoint. Accepts PDF, image, or text receipt."""
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
        status="pending_netting" if abs(parsed["amount"]) >= 1000 else "settled",
    )
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return tx


@router.post("/webhook/{provider}")
async def webhook_ingest(
    provider: str,
    payload: dict,
    db: AsyncSession = Depends(get_db),
):
    """Passive income receiver called by external providers (MP, etc.).
    Auth handled by provider-side signing secret instead of JWT."""
    # TODO: verify provider webhook signature per-provider
    tx = Transaction(
        user_id="system",
        amount=payload.get("amount", 0),
        description=payload.get("description", ""),
        transaction_date=payload.get("date"),
        raw_data=payload,
    )
    db.add(tx)
    await db.commit()
    return {"status": "ok", "transaction_id": str(tx.id)}


@router.get("/netting", response_model=dict)
async def netting_balance(
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    """Returns real balance with netting groups resolved."""
    uid = auth["user_id"]
    stmt = select(Transaction).where(Transaction.user_id == uid, Transaction.status != "absorbed")
    result = await db.execute(stmt)
    txs = result.scalars().all()
    total = sum(tx.amount for tx in txs)
    return {"user_id": uid, "net_balance": str(total), "transaction_count": len(txs)}
