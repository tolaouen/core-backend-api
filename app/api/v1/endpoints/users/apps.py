from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session 
from typing import List

from app.schemas.users.apps import AppCreate, AppUpdate, AppResponse
from app.services.app_user.apps import AppsService
from app.databases.db import get_db
from app.schemas.Responses.response import ApiResponse

app_router = APIRouter()

@app_router.post("/", response_model=AppResponse, status_code=status.HTTP_201_CREATED)
async def create_app(data: AppCreate, db: Session = Depends(get_db)):
    app = AppsService(db).create_app(data)

    return app 

@app_router.get("/", response_model=ApiResponse[List[AppResponse]], status_code=status.HTTP_200_OK)
async def get_all_app(db: Session = Depends(get_db)):
    apps = AppsService(db).get_all_apps()

    return ApiResponse(
        status=200,
        message="List all application",
        data=apps
    )

@app_router.get("/{id}", response_model=ApiResponse[AppResponse], status_code=status.HTTP_200_OK)
async def get_app(id: int, db: Session = Depends(get_db)):
    app = AppsService(db).get_app_by_id(id)

    return ApiResponse(
        status=200,
        message="App retrieved successfully",
        data=app
    )

@app_router.get("/{permission_id}/apps_client", response_model=ApiResponse[List[AppResponse]], status_code=status.HTTP_200_OK)
async def get_multi_app(permission_id: int, db: Session = Depends(get_db)):
    app = AppsService(db).get_apps_by_permission_id(permission_id)

    return ApiResponse(
        status=200,
        message="App retrieved successfully",
        data=app
    )

@app_router.patch("/{id}", response_model=AppResponse, status_code=status.HTTP_200_OK)
async def update_app(id: int, data: AppUpdate, db: Session = Depends(get_db)):
    app = AppsService(db).update_app(id, data)

    return app