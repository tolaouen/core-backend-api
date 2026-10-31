from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.app_permissions.app_user_permissions import AppUserPermission
from app.models.app_function.app_func import AppFunction
from app.schemas.app_permission.app_user_permission import (
    UserPermissionCreate,
    UserPermissionUpdate
)
from app.schemas.Responses.pagination import PaginatedResponse
from app.utils.paginations import paginate
from app.utils.query_builder import build_query


class UserPermissionService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_user_permission(
        self,
        page: int = 1,
        page_size: int = 10,
        user_id: Optional[int] = None,
        function_id: Optional[int] = None,
    ) -> PaginatedResponse[AppUserPermission]:
        query = self.db.query(AppUserPermission).options(
            joinedload(AppUserPermission.function)
        )

        filters = {}
        if user_id:
            filters[AppUserPermission.user_id] = user_id
        if function_id:
            filters[AppUserPermission.function_id] = function_id

        query = build_query(query=query, filters=filters)

        return paginate(query, page=page, page_size=page_size)

    def get_user_permission_by_id(self, permission_id: int) -> Optional[AppUserPermission]:
        user_permission = self.db.query(AppUserPermission).options(
            joinedload(AppUserPermission.function)
        ).filter(
            AppUserPermission.id == permission_id
        ).first()

        if not user_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User Permission ID {permission_id} Not Found."
            )

        return user_permission

    def get_permissions_by_user_id(self, user_id: int) -> List[AppUserPermission]:
        return self.db.query(AppUserPermission).options(
            joinedload(AppUserPermission.function)
        ).filter(
            AppUserPermission.user_id == user_id
        ).all()

    def get_permissions_by_function_id(self, function_id: int) -> List[AppUserPermission]:
        return self.db.query(AppUserPermission).options(
            joinedload(AppUserPermission.function)
        ).filter(
            AppUserPermission.function_id == function_id
        ).all()

    def create_user_permission(self, data: UserPermissionCreate) -> Optional[AppUserPermission]:
        function = self.db.query(AppFunction).filter(AppFunction.id == data.function_id).first()
        if not function:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Function ID {data.function_id} Not Found."
            )

        existing = self.db.query(AppUserPermission).filter(
            AppUserPermission.user_id == data.user_id,
            AppUserPermission.function_id == data.function_id,
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission for user {data.user_id} on function {data.function_id} already exists."
            )

        permission = AppUserPermission(
            user_id=data.user_id,
            function_id=data.function_id,
            permissions=data.permissions,
        )

        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)

        return permission

    def update_user_permission(self, permission_id: int, data: UserPermissionUpdate) -> Optional[AppUserPermission]:
        permission = self.get_user_permission_by_id(permission_id)

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(permission, field, value)

        self.db.commit()
        self.db.refresh(permission)

        return permission

    def delete_user_permission(self, permission_id: int) -> Optional[AppUserPermission]:
        permission = self.get_user_permission_by_id(permission_id)

        self.db.delete(permission)
        self.db.commit()

        return permission

    def delete_permissions_by_user_id(self, user_id: int) -> int:
        """Delete all permissions for a given user. Returns the count of deleted records."""
        count = self.db.query(AppUserPermission).filter(
            AppUserPermission.user_id == user_id
        ).delete()

        self.db.commit()

        return count