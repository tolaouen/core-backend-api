from typing import Generic, TypeVar, Optional
from fastapi import status as http_status
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    """Standard API response format"""
    status: int = http_status.HTTP_200_OK
    message: str
    data: Optional[T] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": 200,
                "message": "Operation successful",
                "data": {}
            }
        }
    )