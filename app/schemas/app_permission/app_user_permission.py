from datetime import datetime
from typing import Optional,List
from pydantic import BaseModel, ConfigDict, field_validator
from app.auth.permissions import normalize_permission_list
from app.schemas.Responses.pagination import PaginatedResponse


class UserPermissionBase(BaseModel):
    permissions: List[str]

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, v: List[str]) -> List[str]:
        return normalize_permission_list(v)

class UserPermissionCreate(UserPermissionBase):
    user_id: int 
    function_id: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 1,
                "function_id": 1,
                "permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            }
        }
    )

class UserPermissionUpdate(UserPermissionBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            }
        }
    )

class UserPermissionResponse(UserPermissionBase):
    id: int
    user_id: int 
    function_id: int
    function_name: Optional[str] = None
    app_code: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 1,
                "function_id": 1,
                "function_name": "Dashboard",
                "app_code": "auth_service",
                "permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            }
        }
    )


UserPermissionListResponse = PaginatedResponse[UserPermissionResponse]
