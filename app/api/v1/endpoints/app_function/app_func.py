from fastapi import APIRouter, status, Query, Depends, HTTPException
from typing import Optional, List, Union
from sqlalchemy.orm import Session

from app.schemas.app_function.app_func import (
    AppFuncCreate,
    AppFuncListResponse,
    AppFuncUpdate,
    AppFuncResponse,
    AppFunctionParentResponse,
)
from app.databases.db import get_db
from app.services.app_function.app_func import AppFuncService
from app.schemas.Responses.response import ApiResponse

app_func_router = APIRouter()


@app_func_router.post(
    "/", response_model=AppFuncResponse, status_code=status.HTTP_201_CREATED
)
async def create_app_function(data: AppFuncCreate, db: Session = Depends(get_db)):
    """Create a new app function."""
    functions = AppFuncService(db).create_app_function(data)
    return functions


@app_func_router.get(
    "/", response_model=AppFuncListResponse, status_code=status.HTTP_200_OK
)
async def get_app_functions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=200, description="Items per page"),
    name: Optional[str] = Query(None, description="Filter by function name"),
    code: Optional[str] = Query(None, description="Filter by function code"),
    path: Optional[str] = Query(None, description="Filter by function path"),
    app_id: Optional[int] = Query(None, description="Filter by app id"),
    status: Optional[str] = Query(None, description="Filter by function status"),
    db: Session = Depends(get_db),
):
    """Get paginated list of app functions with optional filters."""
    app = AppFuncService(db).get_app_function(
        page=page,
        page_size=page_size,
        name=name,
        code=code,
        path=path,
        app_id=app_id,
        status=status,
    )
    return app

# Menu App Function
@app_func_router.get(
    "/menu",
    response_model=ApiResponse[List[Union[AppFunctionParentResponse, AppFuncResponse]]],
    status_code=status.HTTP_200_OK,
)
async def get_menu_app_function(
    app_code: str = Query(..., description="Filter menu functions by app code"),
    db: Session = Depends(get_db),
):
    """Get menu functions for an app as parent/child trees."""
    menu_functions = AppFuncService(db).get_app_function_response(app_code)

    if not menu_functions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No menu functions found",
        )
    return ApiResponse(
        status=200,
        message="Menu functions retrieved successfully",
        data=menu_functions,
    )


@app_func_router.get(
    "/{function_id}",
    response_model=ApiResponse[AppFuncResponse],
    status_code=status.HTTP_200_OK,
)
async def get_app_function(
    function_id: int, db: Session = Depends(get_db)
):
    """Get a specific app function by ID."""
    app_func = AppFuncService(db).get_app_function_by_id(function_id)

    if not app_func:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Function {function_id} not found",
        )
    return ApiResponse(
        status=200,
        message="App function retrieved successfully",
        data=app_func
    )

@app_func_router.get("/{app_id}/function", response_model=ApiResponse[List[AppFuncResponse]])
async def get_multi_app_function(app_id: int, db: Session = Depends(get_db)):
    apps = AppFuncService(db).get_apps_by_function_id(app_id)

    return ApiResponse(
        status=200,
        message="Received Multi App.",
        data=apps
    )

@app_func_router.patch(
    "/{function_id}",
    response_model=AppFuncResponse,
    status_code=status.HTTP_200_OK,
)
async def update_app_function(
    function_id: int,
    data: AppFuncUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing app function (partial update)."""
    app_func = AppFuncService(db).update_app_function(function_id, data)

    if not app_func:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Function {function_id} not found",
        )
    return app_func


@app_func_router.delete(
    "/{function_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_app_function(
    function_id: int, db: Session = Depends(get_db)
):
    """Delete an app function."""
    result = AppFuncService(db).delete_app_function(function_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Function {function_id} not found",
        )
    return None
