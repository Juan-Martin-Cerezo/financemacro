from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RuleCreate(BaseModel):
    category_id: UUID
    keyword: str


class RuleUpdate(BaseModel):
    category_id: UUID | None = None
    keyword: str | None = None


class RuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    category_id: UUID
    keyword: str
    created_at: datetime
