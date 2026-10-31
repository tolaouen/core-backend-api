from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session

from app.databases.db import get_db
from app.schemas.app_role.role import RoleResponse, RoleCreate, RoleListResponse, RoleUpdate
from app.services.app_permission.app_role import AppRoleService

app_role_router = APIRouter()

@app_role_router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(data: RoleCreate, db: Session = Depends(get_db)):
    app_role = AppRoleService(db).create_role(data)

    return app_role

@app_role_router.get("/", response_model=RoleListResponse, status_code=status.HTTP_200_OK)
async def get_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=200),
    name: Optional[str] = None,
    code: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return AppRoleService(db).get_role(
        page=page, page_size=page_size, name=name, code=code, status=status
    )

@app_role_router.get("/{role_id}", response_model=RoleResponse, status_code=status.HTTP_200_OK)
async def get_role_id(role_id: int, db: Session = Depends(get_db)):
    app_role = AppRoleService(db).get_role_by_id(role_id)

    return app_role

@app_role_router.patch("/{role_id}", response_model=RoleResponse, status_code=status.HTTP_200_OK)
async def update_role(role_id: int, data: RoleUpdate, db: Session = Depends(get_db)):
    app_func = AppRoleService(db).update_role(role_id,data)

    return app_func

@app_role_router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: int, db: Session = Depends(get_db)):
    app_func = AppRoleService(db).delete_role(role_id)

    if not app_func:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role {role_id} not found",
        )
    return None