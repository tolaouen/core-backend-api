from typing import  Optional, List
from datetime import datetime
from pydantic import Field, ConfigDict, BaseModel, field_validator
from app.utils.paginations import PaginatedResponse
from app.auth.permissions import normalize_permission_list


class AppFuncPermissionBase(BaseModel):
    permissions: List[str] = Field(...)

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, v: List[str]) -> List[str]:
        return normalize_permission_list(v)

class AppFuncPermissionCreate(AppFuncPermissionBase):
    function_id: int = Field(..., gt=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "function_id": 1,
                "permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            }
        }
    )

class AppFuncPermissionUpdate(AppFuncPermissionBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            }
        }
    )

class AppFuncPermissionResponse(AppFuncPermissionBase):
    id: int
    function_id: int
    permissions: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "function_id": 1,
                "permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
                "created_at": "2025-11-25T14:00:00Z",
                "updated_at": None,
            }
        },
    )

class AppFuncPermissionListResponse(
    PaginatedResponse[AppFuncPermissionResponse]
):
    pass


class FuncWithPermissionsResponse(BaseModel):
    function_id: int
    function_name: str
    function_code: str
    app_code: str
    permissions: Optional[List[str]] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "function_id": 1,
                "function_name": "User Management",
                "function_code": "user_management",
                "app_code": "ADMIN",
                "permissions": ["CREATE", "READ", "UPDATE", "DELETE"],
            }
        },
    )
