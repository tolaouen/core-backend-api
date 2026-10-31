from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class AppBase(BaseModel):
    permission_id: Optional[int] = Field(None)
    name: str = Field(..., max_length=255)
    base_url: str = Field(..., max_length=255)
    app_code: str = Field(..., max_length=50)


class AppCreate(AppBase):
    pass

class AppUpdate(BaseModel):
    permission_id: Optional[int] = Field(None)
    name: Optional[str] = Field(None, max_length=255)
    base_url: Optional[str] = Field(None, max_length=255)
    app_code: Optional[str] = Field(None, max_length=50)

    model_config = ConfigDict(from_attributes=True)

class AppResponse(AppBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
