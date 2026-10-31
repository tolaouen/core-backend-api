from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.app_permissions.app_permission import AppPermission
from app.schemas.app_permission.app_permission import PermissionCreate, PermissionUpdate
from app.utils.query_builder import build_query

class AppPermissionService:
    def __init__(self, db: Session):
        self.db = db 

    def build_query(self, search: Optional[str]):
        query = self.db.query(AppPermission)

        return build_query(
            query,
            search=search,
            search_fields=[AppPermission.label, AppPermission.value]
        )
    
    def get_all_permission(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> tuple[int, List[AppPermission]]:
        query = self.db.query(AppPermission)

        if search:
            search_filter = f"%{search}%"
            query = query.filter((AppPermission.label.ilike(search_filter)) | (AppPermission.value.ilike(search_filter)))

        total = query.count()

        permission = query.offset(skip).limit(limit).all()

        return total, permission
    
    def get_permission_by_id(self, permission_id: int) -> Optional[AppPermission]:
        permission = self.db.query(AppPermission).filter(AppPermission.id == permission_id).first()

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission ID {permission_id} Not Found."
            )
        return permission
    
    def get_permission_by_value(self, value: str) -> Optional[AppPermission]:
        app_value = self.db.query(AppPermission).filter(AppPermission.value == value).first()

        if not app_value:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission Value {value} Not Found." 
            )
        return app_value
    
    def create_permission(self, data: PermissionCreate) -> Optional[AppPermission]:
        existing = self.db.query(AppPermission).filter(AppPermission.value == data.value).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission value '{data.value}' already exists."
            )

        permission = AppPermission(
            value=data.value,
            label=data.label,
        )

        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)

        return permission
    
    def bulk_create_permissions(self, data: List[PermissionCreate]) -> List[AppPermission]:
        values = [p.value for p in data]
        if len(values) != len(set(values)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate permission values in request",
            )
        
        existing = self.db.query(AppPermission).filter(AppPermission.value.in_(values)).all()

        if existing:
            existing_values = ",".join([str(p.value) for p in existing])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permissions already exist: {existing_values}",
            )

        permissions = [
            AppPermission(label=p.label, value=p.value) for p in data
        ]

        self.db.add_all(permissions)
        self.db.commit()

        for permission in permissions:
            self.db.refresh(permission)

        return permissions

    def update_permission(self, permission_id: int, data: PermissionUpdate) -> Optional[AppPermission]:
        permission = self.get_permission_by_id(permission_id)

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission ID {permission_id} Not Found."
            )
        
        if data.value and data.value != permission.value:
            existing = self.db.query(AppPermission).filter(AppPermission.value == data.value, AppPermission.id != permission_id).first()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Permission with value '{data.value}' already exists",
                )

        if data.value is not None:
            permission.value = data.value

        if data.label is not None:
            permission.label = data.label

        self.db.commit()
        self.db.refresh(permission)

        return permission
    
    def delete_permission(self, permission_id: int) -> Optional[AppPermission]:
        permission = self.get_permission_by_id(permission_id)

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission Value {permission_id} Not Found."
            )
        
        self.db.delete(permission)
        self.db.commit()

        return permission
    
