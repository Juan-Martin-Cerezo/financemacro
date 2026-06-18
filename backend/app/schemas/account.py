from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AccountCreate(BaseModel):
    provider: str  # mercadopago | invertironline | bank | manual
    type: str      # checking | savings | investment | credit
    name: str = ""


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    provider: str
    type: str
    name: str
    credentials: dict
    created_at: datetime
    updated_at: datetime
