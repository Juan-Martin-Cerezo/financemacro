from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EnvelopeCreate(BaseModel):
    name: str
    target_amount: Decimal | None = None


class EnvelopeUpdate(BaseModel):
    name: str | None = None
    target_amount: Decimal | None = None


class AllocateRequest(BaseModel):
    amount: Decimal  # positive = add to envelope


class EnvelopeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    name: str
    target_amount: Decimal | None
    current_balance: Decimal
    created_at: datetime
    updated_at: datetime
