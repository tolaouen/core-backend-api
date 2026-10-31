from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field



class AppRoleGroupBase(BaseModel):
    group_id: int = Field(..., gt=0)
    role_id: int = Field(..., gt=0)


class AppRoleGroupCreate(AppRoleGroupBase):
    pass
    

class AppRoleGroupResponse(AppRoleGroupBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AppRoleGroupUpdate(BaseModel):
    group_id: Optional[int] = Field(None, gt=0)
    role_id: Optional[int] = Field(None, gt=0)

AppRoleGroupListResponse = AppRoleGroupResponse
