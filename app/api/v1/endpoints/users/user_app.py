from fastapi import APIRouter, status, Query, Depends
from sqlalchemy.orm import Session 
from typing import Optional

from app.schemas.users.user_app import UserAppCreate, UserAppListResponse, UserAppResponse, UserAppUpdate
from app.services.app_user.user_app import UserAppService
from app.databases.db import get_db

app_user_router = APIRouter()

@app_user_router.post("/", response_model=UserAppResponse, status_code=status.HTTP_201_CREATED)
async def create_user_app(data: UserAppCreate, db: Session = Depends(get_db)):
    user_app = UserAppService(db).create_user_app(data)

    return user_app

@app_user_router.get("/", response_model=UserAppListResponse, status_code=status.HTTP_200_OK)
async def get_user_apps(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=200),
    app_code: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    apps =  UserAppService(db).get_all_user_app(
        page=page,
        page_size=page_size,
        app_code=app_code,
        status=status,
    )

    return apps

@app_user_router.get("/{id}", response_model=UserAppResponse, status_code=status.HTTP_200_OK)
async def get_user_app(id: int, db: Session = Depends(get_db)):
    item = UserAppService(db).get_user_app_by_id(id)

    return item

@app_user_router.patch("/{id}", response_model=UserAppResponse, status_code=status.HTTP_200_OK)
async def update_user_app(id: int, data: UserAppUpdate, db: Session = Depends(get_db)):
    app_user = UserAppService(db).update_user_app(id, data)

    return app_user

@app_user_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_app(id: int, db: Session = Depends(get_db)):

    UserAppService(db).delete_user_app(id)
