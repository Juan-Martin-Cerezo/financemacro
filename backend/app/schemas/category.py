from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str
    color: str = "#6366f1"
    icon: str = "tag"


class CategoryUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    icon: str | None = None


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    name: str
    color: str
    icon: str
    created_at: datetime
