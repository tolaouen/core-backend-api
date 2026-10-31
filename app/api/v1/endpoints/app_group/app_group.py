from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.orm import Session

from app.schemas.app_group.app_group import AppGroupCreate, AppGroupUpdate, AppGroupListResponse
from app.services.app_group.app_group import AppGroupService
from app.databases.db import get_db 
from app.schemas.Responses.response import ApiResponse

app_group_router = APIRouter()

@app_group_router.post(
    "/", response_model=AppGroupListResponse, status_code=status.HTTP_201_CREATED
)
async def create_group(
    group: AppGroupCreate, db: Session = Depends(get_db)
):
    """Create a new app group."""
    result = AppGroupService(db).create_group(group)
    return result

@app_group_router.get(
    "/", response_model=ApiResponse[List[AppGroupListResponse]], status_code=status.HTTP_200_OK
)
async def get_groups(db: Session = Depends(get_db)):

    result = AppGroupService(db).get_all_groups()
    return ApiResponse(
        status=200,
        message="App Groups retrieved successfully",
        data=result
    )

@app_group_router.get(
    "/{group_id}",
    response_model=ApiResponse[AppGroupListResponse],
    status_code=status.HTTP_200_OK,
)
async def get_group(group_id: int, db: Session = Depends(get_db)):
    """Get a specific app group by ID."""
    result = AppGroupService(db).get_group_by_id(group_id)
    return ApiResponse(
        status=200,
        message="App Group retrieved successfully",
        data=result
    )

@app_group_router.patch(
    "/{group_id}",
    response_model=AppGroupListResponse,
    status_code=status.HTTP_200_OK
)
async def update_group(
    group_id: int, group: AppGroupUpdate, db: Session = Depends(get_db)
):
    """Update an existing app group."""
    result = AppGroupService(db).update_group(group_id, group)
    return result