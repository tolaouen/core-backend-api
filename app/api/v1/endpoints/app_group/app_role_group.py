from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.schemas.app_group.app_role_group import AppRoleGroupCreate, AppRoleGroupListResponse
from app.services.app_group.app_role_group import AppRoleGroupService
from app.databases.db import get_db 
from app.schemas.Responses.response import ApiResponse

app_role_group_router = APIRouter()

@app_role_group_router.post(
    "/", response_model=AppRoleGroupListResponse, status_code=status.HTTP_201_CREATED
)
async def create_role_group(
    role_group: AppRoleGroupCreate, db: Session = Depends(get_db)
):
    """Create a new app role group."""
    result = AppRoleGroupService(db).create_role_group(role_group)
    return result

@app_role_group_router.get(
    "/", response_model=ApiResponse[List[AppRoleGroupListResponse]], status_code=status.HTTP_200_OK
)
async def get_role_groups(db: Session = Depends(get_db)):
    """Get all app role groups."""
    result = AppRoleGroupService(db).get_all_role_groups()
    return ApiResponse(
        status=200,
        message="App Role Groups retrieved successfully",
        data=result
    )

@app_role_group_router.get(
    "/{role_group_id}",
    response_model=ApiResponse[AppRoleGroupListResponse],
    status_code=status.HTTP_200_OK
)
async def get_role_group(
    role_group_id: int, db: Session = Depends(get_db)
):
    """Get a specific app role group by ID."""
    result = AppRoleGroupService(db).get_role_group_by_id(role_group_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"App Role Group {role_group_id} not found",
        )

    return ApiResponse(
        status=200,
        message="App Role Group retrieved successfully",
        data=result
    )