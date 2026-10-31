from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.utils.paginations import paginate

from app.schemas.app_permission.app_permission import PermissionCreate, PermissionResponse, PermissionListResponse, PermissionUpdate
from app.services.app_permission.app_permission import AppPermissionService
from app.databases.db import get_db

permission_router = APIRouter()

@permission_router.post("/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(data: PermissionCreate, db: Session = Depends(get_db)):
    permission_app = AppPermissionService(db).create_permission(data)
    return permission_app

@permission_router.post(
    "/bulk",
    response_model=list[PermissionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple permissions at once",
)
def bulk_create_permissions(
    permissions: list[PermissionCreate], db: Session = Depends(get_db)
):
    return AppPermissionService(db).bulk_create_permissions(permissions)

@permission_router.get("/", response_model=PermissionListResponse, summary="Get all permissions")
def get_permissions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=200, description="Items per page"),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = AppPermissionService(db).build_query(search)

    paginated = paginate(query, page=page, page_size=page_size)

    return paginated

@permission_router.get(
    "/{permission_id}",
    response_model=PermissionResponse,
    summary="Get permission by id",
)
def get_permission(permission_id: int, db: Session = Depends(get_db)):
    permission = AppPermissionService(db).get_permission_by_id(permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with id {permission_id} not found",
        )

    return permission

@permission_router.get(
    "/value/{value}",
    response_model=PermissionResponse,
    summary="Get permission by value",
)
def get_permission_by_value(value: str, db: Session = Depends(get_db)):
    permission = AppPermissionService(db).get_permission_by_value(value)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with value '{value}' not found",
        )

    return permission

@permission_router.patch(
    "/{permission_id}", response_model=PermissionResponse, summary="Update a permission"
)
def update_permission(
    permission_id: int, permission: PermissionUpdate, db: Session = Depends(get_db)
):
    return AppPermissionService(db).update_permission(permission_id, permission)


@permission_router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a permission",
)
def delete_permission(permission_id: int, db: Session = Depends(get_db)):
    AppPermissionService(db).delete_permission(permission_id)
    return None
