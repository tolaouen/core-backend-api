from typing import Literal, Optional, List
from datetime import datetime
from pydantic import Field, ConfigDict, BaseModel, model_validator
from app.utils.paginations import PaginatedResponse
from app.constants.constant import Is_ParentType

FunctionStatus = Literal["ACT", "INC", "DEL"]

class AppFuncBase(BaseModel):
    app_id: Optional[int] = Field(None, ge=1)
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[int] = Field(None, ge=1)
    is_parent: str = Field(default=Is_ParentType.Child.value, min_length=1, max_length=100)
    sector: Optional[str] = Field(None, min_length=1, max_length=255)
    path: Optional[str] = Field(None)
    icon: Optional[str] = Field(None, min_length=1, max_length=255)
    app_code: Optional[str] = Field(None, min_length=1, max_length=100)
    is_show: bool = Field(default=False)
    order: Optional[int] = Field(None, ge=1)
    status: FunctionStatus = Field(default="ACT")


class AppFuncCreate(AppFuncBase):
    pass

class AppFuncUpdate(BaseModel):
    app_id: Optional[int] = Field(None)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_id: Optional[int] = Field(None)
    is_parent: Optional[str] = Field(None, min_length=1, max_length=100)
    sector: Optional[str] = Field(None, min_length=1, max_length=255)
    path: Optional[str] = Field(None)
    icon: Optional[str] = Field(None, min_length=1, max_length=255)
    app_code: Optional[str] = Field(None, min_length=1,max_length=255)
    is_show: Optional[bool] = Field(None)
    order: Optional[int] = Field(None)
    status: Optional[FunctionStatus] = Field(None)

    @model_validator(mode="before")
    @classmethod
    def reject_null_required_fields(cls, values):
        if isinstance(values, dict):
            required_fields = {"app_id", "name", "code", "type", "app_code"}
            null_fields = required_fields.intersection(
                field for field, value in values.items() if value is None
            )
            if null_fields:
                fields = ", ".join(sorted(null_fields))
                raise ValueError(f"Fields cannot be null: {fields}")
        return values

class AppFuncResponse(AppFuncBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AppFunctionParentResponse(AppFuncResponse):
    subtitle: List[AppFuncResponse] = Field(default_factory=list)

AppFuncListResponse = PaginatedResponse[AppFuncResponse]
