from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_jwt
from app.core.database import get_db
from app.models.models import Account, AccountProvider, AccountType
from app.schemas.account import AccountCreate, AccountRead

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountRead])
async def list_accounts(
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    uid = auth["user_id"]
    stmt = select(Account).where(Account.user_id == uid).order_by(Account.provider, Account.name)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(
    body: AccountCreate,
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    uid = auth["user_id"]

    # Validate provider enum
    try:
        provider = AccountProvider(body.provider)
    except ValueError:
        valid = [e.value for e in AccountProvider]
        raise HTTPException(status_code=422, detail=f"Invalid provider. Valid: {valid}")

    # Validate type enum
    try:
        acct_type = AccountType(body.type)
    except ValueError:
        valid = [e.value for e in AccountType]
        raise HTTPException(status_code=422, detail=f"Invalid type. Valid: {valid}")

    acct = Account(
        user_id=uid,
        provider=provider,
        type=acct_type,
        name=body.name,
        credentials={},
    )
    db.add(acct)
    await db.commit()
    await db.refresh(acct)
    return acct


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: UUID,
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    uid = auth["user_id"]
    stmt = select(Account).where(Account.id == account_id, Account.user_id == uid)
    acct = (await db.execute(stmt)).scalar_one_or_none()
    if not acct:
        raise HTTPException(status_code=404, detail="Account not found")
    await db.delete(acct)
    await db.commit()
