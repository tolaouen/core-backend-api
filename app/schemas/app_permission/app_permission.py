from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.Responses.pagination import PaginatedResponse


class PermissionBase(BaseModel):
    label: str = Field(
        ..., min_length=1, max_length=255, description="Permission label (e.g., 'Read')"
    )
    value: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Permission value (e.g., 'user:read')",
    )

    model_config = ConfigDict(from_attributes=True)


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    label: Optional[str] = Field(None, min_length=1, max_length=255)
    value: Optional[str] = Field(None, min_length=1, max_length=255)

    model_config = ConfigDict(from_attributes=True)


class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


PermissionListResponse = PaginatedResponse[PermissionResponse]
