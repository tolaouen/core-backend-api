from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator

from app.constants.constant import RoleEnum, UserRoleEnum
from app.schemas.Responses.pagination import PaginatedResponse
from app.schemas.users.user_app_access import AppUserAccessInDBBase
from app.schemas.users.user_app import UserAppResponse
from app.schemas.app_permission.app_user_permission import UserPermissionResponse


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    user_type: Optional[str] = RoleEnum.USER.value
    user_role: Optional[str] = UserRoleEnum.GUEST.value
    phone: str
    gender: str
    password: str = Field(..., min_length=8, max_length=20)
    verify_password: str = Field(...,min_length=8, max_length=20)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isalpha() for c in value):
            raise ValueError("Password must contain at least one letter")
        return value


class UserUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    profile: Optional[str] = None
    gender: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

    model_config = ConfigDict(from_attributes=True)

class UserCountResponse(BaseModel):
    total_users: int
    female_users: int
    email_verified: int
    register_today: int

class UserCountTrend(BaseModel):
    month: str = Field(..., examples=["Jan"])
    count: int = Field(..., ge=0, examples=[12])

class UserTrendResponse(BaseModel):
    year: int = Field(..., examples=[2026])
    data: list[UserCountTrend]

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    full_name: str
    profile: str
    phone: str
    gender: str
    user_type: str
    # user_role: str
    username: str
    email: EmailStr
    is_active: bool
    email_verified: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(UserResponse):
    user_apps: List[UserAppResponse] = []
    user_permissions: List[UserPermissionResponse] = []
    user_access: List[AppUserAccessInDBBase] = []

    model_config = ConfigDict(from_attributes=True)


class UserListItem(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


UserListResponse = PaginatedResponse[UserListItem]