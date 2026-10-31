from fastapi import APIRouter, status, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional, List

from app.databases.db import get_db
from app.schemas.users.user_app_access import (
    AppUserAccessBase,
    AppUserAccessBulkCreate,
    AppUserAccessUpdate,
    AppUserAccessCreate
)
from app.services.app_user.user_app_access import AppUserAccessService
from app.schemas.Responses.response import ApiResponse

access_router = APIRouter()


@access_router.post("", response_model=AppUserAccessBase, status_code=status.HTTP_200_OK)
async def create_app_user_access(
    obj_in: AppUserAccessCreate,
    db: Session = Depends(get_db),
):
    service = AppUserAccessService(db).create_app_user_access(obj_in)
    return service
    


@access_router.post("/bulk", response_model=List[AppUserAccessBase], status_code=status.HTTP_200_OK)
async def bulk_create_app_user_access(
    obj_in: AppUserAccessBulkCreate,
    db: Session = Depends(get_db),
):
    service = AppUserAccessService(db)
    return service.bulk_create_app_user_access(obj_in)


@access_router.get("", response_model=ApiResponse[List[AppUserAccessBase]], status_code=status.HTTP_200_OK)
async def get_all_app_user_access(
    db: Session = Depends(get_db),
):
    service = AppUserAccessService(db).get_all_app_user_access()
    return ApiResponse(
        status=200,
        message="Received All Access",
        data=service
    )


@access_router.get("/{access_id}", response_model=ApiResponse[AppUserAccessBase], status_code=status.HTTP_200_OK)
async def get_app_user_access_by_id(
    access_id: int,
    db: Session = Depends(get_db),
):
    service = AppUserAccessService(db).get_app_user_access_by_id(access_id)
    return ApiResponse(
          status=200,
          message="Received Access by ID",
          data=service
    )


@access_router.get("/user/{user_id}", response_model=ApiResponse[List[AppUserAccessBase]], status_code=status.HTTP_200_OK)
async def get_app_user_access_by_user(
    user_id: int,
    type: Optional[str] = Query(None, description="Filter by access type: ROLE, FUNCTION, GROUP"),
    db: Session = Depends(get_db),
):
    service = AppUserAccessService(db)
    if type:
        return ApiResponse(
            status=200,
            message="Revieved App Access",
            data = service.get_app_user_access_by_user_and_type(user_id, type)
            )
    return ApiResponse(
        status=200,
        message="Revieved App Access",
        data = service.get_app_user_access_by_user(user_id)
    )


@access_router.patch("/{access_id}", response_model=AppUserAccessBase, status_code=status.HTTP_200_OK)
async def update_app_user_access(
    access_id: int,
    obj_in: AppUserAccessUpdate,
    db: Session = Depends(get_db),
):
    service = AppUserAccessService(db)
    return service.update_app_user_access(access_id, obj_in)


@access_router.delete("/{access_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_app_user_access(
    access_id: int,
    db: Session = Depends(get_db),
):
    service = AppUserAccessService(db)
    service.delete_app_user_access(access_id)
    return None


@access_router.delete("/user/{user_id}", status_code=status.HTTP_200_OK)
async def delete_app_user_access_by_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    service = AppUserAccessService(db)
    deleted_count = service.delete_app_user_access_by_user(user_id)
    return {
        "message": "deleted succesfully",
        "deleted": deleted_count
        }


@access_router.patch("/user/{user_id}/replace", response_model=List[AppUserAccessBase], status_code=status.HTTP_200_OK)
async def replace_user_access(
    user_id: int,
    type: str = Query(..., description="Access type: ROLE, FUNCTION, GROUP"),
    ref_ids: List[int] = Query(..., description="List of ref_ids to assign"),
    db: Session = Depends(get_db),
):
    service = AppUserAccessService(db)
    return service.replace_user_access(user_id, type, ref_ids)