from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TransactionCreate(BaseModel):
    account_id: UUID | None = None
    amount: Decimal
    currency: str = "ARS"
    description: str = ""
    transaction_date: datetime = None  # type: ignore[assignment]


class CategoryBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    color: str
    icon: str


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    account_id: UUID | None
    event_group_id: UUID | None
    category_id: UUID | None
    category: CategoryBrief | None = None
    amount: Decimal
    currency: str
    description: str
    transaction_date: datetime
    status: str
    raw_data: dict | None
    created_at: datetime
