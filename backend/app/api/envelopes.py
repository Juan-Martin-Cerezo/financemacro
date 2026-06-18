from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_jwt
from app.core.database import get_db
from app.models.models import Envelope
from app.schemas.envelope import AllocateRequest, EnvelopeCreate, EnvelopeRead, EnvelopeUpdate

router = APIRouter(prefix="/api/v1/envelopes", tags=["envelopes"])


@router.get("", response_model=list[EnvelopeRead])
async def list_envelopes(
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    uid = auth["user_id"]
    stmt = select(Envelope).where(Envelope.user_id == uid).order_by(Envelope.name)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("", response_model=EnvelopeRead, status_code=status.HTTP_201_CREATED)
async def create_envelope(
    body: EnvelopeCreate,
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    env = Envelope(user_id=auth["user_id"], **body.model_dump())
    db.add(env)
    await db.commit()
    await db.refresh(env)
    return env


@router.patch("/{envelope_id}", response_model=EnvelopeRead)
async def update_envelope(
    envelope_id: UUID,
    body: EnvelopeUpdate,
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    uid = auth["user_id"]
    stmt = select(Envelope).where(Envelope.id == envelope_id, Envelope.user_id == uid)
    env = (await db.execute(stmt)).scalar_one_or_none()
    if not env:
        raise HTTPException(status_code=404, detail="Envelope not found")

    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(env, field, val)
    await db.commit()
    await db.refresh(env)
    return env


@router.post("/{envelope_id}/allocate", response_model=EnvelopeRead)
async def allocate_to_envelope(
    envelope_id: UUID,
    body: AllocateRequest,
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    """Allocate funds from general balance into a specific envelope."""
    uid = auth["user_id"]
    if body.amount <= 0:
        raise HTTPException(status_code=422, detail="Allocation amount must be positive")

    stmt = select(Envelope).where(Envelope.id == envelope_id, Envelope.user_id == uid)
    env = (await db.execute(stmt)).scalar_one_or_none()
    if not env:
        raise HTTPException(status_code=404, detail="Envelope not found")

    env.current_balance += body.amount
    await db.commit()
    await db.refresh(env)
    return env


@router.delete("/{envelope_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_envelope(
    envelope_id: UUID,
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    uid = auth["user_id"]
    stmt = select(Envelope).where(Envelope.id == envelope_id, Envelope.user_id == uid)
    env = (await db.execute(stmt)).scalar_one_or_none()
    if not env:
        raise HTTPException(status_code=404, detail="Envelope not found")
    await db.delete(env)
    await db.commit()
