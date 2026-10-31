from pydantic import BaseModel, Field, ConfigDict
from typing import Generic, List, TypeVar

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=200)
    total: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=0)
    has_next: bool
    has_prev: bool

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    meta: PaginationMeta
    items: List[T]

    model_config = ConfigDict(from_attributes=True)
