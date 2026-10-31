from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.Responses.pagination import PaginatedResponse


class UserAppBase(BaseModel):
    user_id: int
    app_id: int 
    app_code: str = Field(..., max_length=50)
    status: str = Field(default="ACT", max_length=10)


class UserAppCreate(UserAppBase):
    pass


class UserAppUpdate(BaseModel):
    user_id: Optional[int] = None
    app_id: Optional[int] = None
    app_code: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=10)

    model_config = ConfigDict(from_attributes=True)


class UserAppResponse(UserAppBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


UserAppListResponse = PaginatedResponse[UserAppResponse]

