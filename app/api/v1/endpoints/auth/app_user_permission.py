from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.databases.db import get_db
from app.schemas.app_permission.app_user_permission import (
    UserPermissionCreate,
    UserPermissionUpdate,
    UserPermissionResponse,
    UserPermissionListResponse,
)
from app.services.app_permission.app_user_permisson import UserPermissionService
from app.schemas.Responses.response import ApiResponse

app_user_permission_router = APIRouter()


@app_user_permission_router.get(
    "",
    response_model=UserPermissionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all user permissions (paginated)",
)
async def get_user_permissions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=200, description="Items per page"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    function_id: Optional[int] = Query(None, description="Filter by function ID"),
    db: Session = Depends(get_db),
):
    return UserPermissionService(db).get_all_user_permission(
        page=page, page_size=page_size, user_id=user_id, function_id=function_id
    )


@app_user_permission_router.get(
    "/{permission_id}",
    response_model=UserPermissionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user permission by ID",
)
async def get_user_permission(permission_id: int, db: Session = Depends(get_db)):
    return UserPermissionService(db).get_user_permission_by_id(permission_id)


@app_user_permission_router.get(
    "/user/{user_id}",
    response_model=ApiResponse[List[UserPermissionResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get all permissions for a specific user",
)
async def get_permissions_by_user(user_id: int, db: Session = Depends(get_db)):
    user_permission = UserPermissionService(db).get_permissions_by_user_id(user_id)

    return ApiResponse(
        status=200,
        message="Get all permissions for a specific user",
        data=user_permission
    )


@app_user_permission_router.get(
    "/function/{function_id}",
    response_model=ApiResponse[List[UserPermissionResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get all permissions for a specific function",
)
async def get_permissions_by_function(function_id: int, db: Session = Depends(get_db)):
    user_permission = UserPermissionService(db).get_permissions_by_function_id(function_id)

    return ApiResponse(
        status=200,
        message="Get all permissions for a specific function",
        data=user_permission
    )

@app_user_permission_router.post(
    "",
    response_model=UserPermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user permission",
)
async def create_user_permission(data: UserPermissionCreate, db: Session = Depends(get_db)):
    return UserPermissionService(db).create_user_permission(data)

@app_user_permission_router.patch(
    "/{permission_id}",
    response_model=UserPermissionResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a user permission",
)
async def update_user_permission(
    permission_id: int, data: UserPermissionUpdate, db: Session = Depends(get_db)
):
    return UserPermissionService(db).update_user_permission(permission_id, data)


@app_user_permission_router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user permission",
)
async def delete_user_permission(permission_id: int, db: Session = Depends(get_db)):
    UserPermissionService(db).delete_user_permission(permission_id)
    return None


@app_user_permission_router.delete(
    "/user/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all permissions for a user",
)
async def delete_permissions_by_user(user_id: int, db: Session = Depends(get_db)):
    UserPermissionService(db).delete_permissions_by_user_id(user_id)
    return None
