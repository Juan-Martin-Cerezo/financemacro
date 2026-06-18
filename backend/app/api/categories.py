from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_jwt
from app.core.database import get_db
from app.models.models import Category
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.rule_matcher import RuleMatcher

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
async def list_categories(
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    uid = auth["user_id"]
    stmt = select(Category).where(Category.user_id == uid).order_by(Category.name)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    body: CategoryCreate,
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    cat = Category(user_id=auth["user_id"], **body.model_dump())
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: UUID,
    body: CategoryUpdate,
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    uid = auth["user_id"]
    stmt = select(Category).where(Category.id == category_id, Category.user_id == uid)
    cat = (await db.execute(stmt)).scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(cat, field, val)
    await db.commit()
    await db.refresh(cat)
    return cat


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    auth: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    uid = auth["user_id"]
    stmt = select(Category).where(Category.id == category_id, Category.user_id == uid)
    cat = (await db.execute(stmt)).scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(cat)
    await db.commit()
