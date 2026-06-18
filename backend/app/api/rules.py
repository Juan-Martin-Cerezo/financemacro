from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_jwt
from app.core.database import get_db
from app.models.models import CategorizationRule
from app.schemas.rule import RuleCreate, RuleRead, RuleUpdate

router = APIRouter(prefix="/api/v1/rules", tags=["rules"])


@router.get("", response_model=list[RuleRead])
async def list_rules(
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    uid = auth["user_id"]
    stmt = select(CategorizationRule).where(CategorizationRule.user_id == uid).order_by(CategorizationRule.created_at)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("", response_model=RuleRead, status_code=status.HTTP_201_CREATED)
async def create_rule(
    body: RuleCreate,
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    rule = CategorizationRule(user_id=auth["user_id"], **body.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.patch("/{rule_id}", response_model=RuleRead)
async def update_rule(
    rule_id: UUID,
    body: RuleUpdate,
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    uid = auth["user_id"]
    stmt = select(CategorizationRule).where(CategorizationRule.id == rule_id, CategorizationRule.user_id == uid)
    rule = (await db.execute(stmt)).scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(rule, field, val)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: UUID,
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    uid = auth["user_id"]
    stmt = select(CategorizationRule).where(CategorizationRule.id == rule_id, CategorizationRule.user_id == uid)
    rule = (await db.execute(stmt)).scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    await db.delete(rule)
    await db.commit()
