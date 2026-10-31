from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session

from app.dependencies.session import session
from app.schemas.app_function.app_func_permission import (
    AppFuncPermissionCreate,
    AppFuncPermissionListResponse,
    AppFuncPermissionResponse,
    FuncWithPermissionsResponse,
    AppFuncPermissionUpdate,
)
from app.services.app_function.app_func_permission import AppFuncPermissionService

app_func_permission_router = APIRouter()


@app_func_permission_router.post(
    "", response_model=AppFuncPermissionResponse, status_code=status.HTTP_201_CREATED
)
async def create_func_permission(
    permission: AppFuncPermissionCreate, db: Session = session
):
    """Create a new app function permission."""
    result = AppFuncPermissionService(db).create_app_function_permission(permission)
    return result


@app_func_permission_router.get(
    "", response_model=AppFuncPermissionListResponse, status_code=status.HTTP_200_OK
)
async def get_func_permission(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=200, description="Item per page"),
    function_id: Optional[int] = Query(None, description="Filter by function ID"),
    db: Session = session,
):
    """Get paginated list of app function permissions."""
    result = AppFuncPermissionService(db).get_app_function_permission(
        page=page, page_size=page_size, function_id=function_id
    )
    return result


@app_func_permission_router.get(
    "/with-functions",
    response_model=List[FuncWithPermissionsResponse],
    status_code=status.HTTP_200_OK,
)
async def get_func_with_permission(
    app_code: Optional[str] = Query(None, description="Filter by app code"),
    db: Session = session,
):
    """Get functions with their associated permissions."""
    result = AppFuncPermissionService(db).get_function_with_permission(app_code)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No functions with permissions found",
        )
    return result


@app_func_permission_router.get(
    "/{permission_id}",
    response_model=AppFuncPermissionResponse,
    status_code=status.HTTP_200_OK,
)
async def get_function_permission(
    permission_id: int, db: Session = session
):
    """Get a specific app function permission by ID."""
    result = AppFuncPermissionService(db).get_app_permission_id(permission_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission {permission_id} not found",
        )
    return result


@app_func_permission_router.get(
    "/by-function/{function_id}",
    response_model=AppFuncPermissionResponse,
    status_code=status.HTTP_200_OK,
)
async def get_permission_by_function(
    function_id: int, db: Session = session
):
    """Get permission by function ID."""
    permission = AppFuncPermissionService(db).get_app_function_permission_id(
        function_id
    )

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permissions for function {function_id} not found",
        )
    return permission


@app_func_permission_router.put(
    "/{permission_id}",
    response_model=AppFuncPermissionResponse,
    status_code=status.HTTP_200_OK,
)
async def update_function_permission(
    permission_id: int,
    data: AppFuncPermissionUpdate,
    db: Session = session,
):
    """Update an existing app function permission."""
    permission = AppFuncPermissionService(db).update_app_function_permission(
        permission_id, data
    )

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission {permission_id} not found",
        )
    return permission


@app_func_permission_router.put(
    "/by-function/{function_id}",
    response_model=AppFuncPermissionResponse,
    status_code=status.HTTP_200_OK,
)
async def update_or_create_permission(
    function_id: int,
    data: AppFuncPermissionUpdate,
    db: Session = session,
):
    """Update or create permission for a specific function."""
    functions = AppFuncPermissionService(db).update_or_create_by_function_id(
        function_id, data.permissions
    )

    if not functions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Function {function_id} not found",
        )
    return functions


@app_func_permission_router.delete(
    "/{permission_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_function_permission(
    permission_id: int, db: Session = session
):
    """Delete an app function permission."""
    result = AppFuncPermissionService(db).delete_function_permission(permission_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission {permission_id} not found",
        )
    return None


@app_func_permission_router.delete(
    "/by-function/{function_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_permission_by_function(
    function_id: int, db: Session = session
):
    """Delete permissions for a specific function."""
    functions = AppFuncPermissionService(db).delete_by_function_id(function_id)

    if not functions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Function {function_id} not found",
        )
    return None