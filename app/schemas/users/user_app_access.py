from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.constants.constant import AccessType

class AppUserAccessBase(BaseModel):
    user_id: int
    ref_id: int
    type: AccessType

class AppUserAccessCreate(AppUserAccessBase):
    pass

class AppUserAccessUpdate(BaseModel):
    user_id: Optional[int] = None
    ref_id: Optional[int] = None
    type: Optional[AccessType] = None


class AppUserAccessInDBBase(AppUserAccessBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AppUserAccess(AppUserAccessInDBBase):
    pass


class AppUserAccessBulkCreate(BaseModel):
    user_id: int
    items: list[AccessType]
    ref_ids: list[int]