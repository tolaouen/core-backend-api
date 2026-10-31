from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

Status = Literal["ACT", "INC", "DEL"]

from app.schemas.Responses.pagination import PaginatedResponse


class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=100)
    app_code: str = Field(..., min_length=1, max_length=100)
    status: Status = Field(default="ACT")


class RoleCreate(RoleBase):
    pass


class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    code: Optional[str] = Field(None, max_length=100)
    app_code: Optional[str] = Field(None, max_length=100)
    status: Optional[Status] = Field(None)


RoleListResponse = PaginatedResponse[RoleResponse]
