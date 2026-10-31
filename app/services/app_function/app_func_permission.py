from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, cast
from fastapi import HTTPException, status

from app.models.app_function.app_func import AppFunction
from app.models.app_function.app_func_permission import AppFuncPermission
from app.schemas.app_function.app_func_permission import AppFuncPermissionCreate, AppFuncPermissionUpdate
from app.utils.paginations import paginate
from app.schemas.Responses.pagination import PaginatedResponse



class AppFuncPermissionService:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------
    # Get All Function APP
    # ---------------------
    def get_app_function_permission(
            self,
            page: int = 1,
            page_size: int = 10,
            function_id: Optional[int] = None
    ) -> PaginatedResponse[AppFuncPermission]:
        query = self.db.query(AppFuncPermission)

        if function_id is not None:
            query = query.filter(AppFuncPermission.function_id == function_id)

        return paginate(query, page=page, page_size=page_size)

    def get_function_with_permission(self, app_code: Optional[str] = None) -> List[Dict[str, Any]]:
        query = self.db.query(AppFunction)

        if app_code:
            query = query.filter(AppFunction.app_code == app_code)

        functions = query.all()

        result = []

        for function in functions:
            function_id = cast(int, function.id)
            permission = self._find_by_function_id(function_id)

            result.append(
                {
                    "function_id": function.id,
                    "function_name": function.name,
                    "function_code": function.code,
                    "app_code": function.app_code,
                    "permissions": permission.permission if permission else None,
                }
            )

        return result

    def _find_by_function_id(self, function_id: int) -> Optional[AppFuncPermission]:
        return (
            self.db.query(AppFuncPermission)
            .filter(AppFuncPermission.function_id == function_id)
            .first()
        )

    def _find_by_id(self, permission_id: int) -> Optional[AppFuncPermission]:
        return (
            self.db.query(AppFuncPermission)
            .filter(AppFuncPermission.id == permission_id)
            .first()
        )

    def get_app_function_permission_id(self, function_id: int) -> AppFuncPermission:
        item = self._find_by_function_id(function_id)

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="App Function Permission Not Found."
            )

        return item

    def get_app_permission_id(self, permission_id: int) -> AppFuncPermission:
        permission = self._find_by_id(permission_id)

        if permission is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission ID {permission_id} Not Found."
            )

        return permission

    def create_app_function_permission(self, data: AppFuncPermissionCreate) -> AppFuncPermission:
        # Check Function App exists
        function = self.db.query(AppFunction).filter(AppFunction.id == data.function_id).first()

        if not function:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Function With ID {data.function_id} Not Found."
            )
        exist = self._find_by_function_id(data.function_id)

        if exist:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Permissions for function {data.function_id} already exist. Use update instead."
            )

        function_permission = AppFuncPermission(
            function_id=data.function_id,
            permission=data.permissions
        )

        self.db.add(function_permission)
        self.db.commit()
        self.db.refresh(function_permission)

        return function_permission

    def update_app_function_permission(self, permission_id: int, data: AppFuncPermissionUpdate) -> AppFuncPermission:
        permission = self._find_by_id(permission_id)

        if permission is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="App Function Permission Not Found."
            )

        permission.permission = data.permissions

        self.db.commit()
        self.db.refresh(permission)

        return permission

    def update_or_create_by_function_id(self, function_id: int, permissions: List[str]) -> AppFuncPermission:
        # Check Function App exists
        function = self.db.query(AppFunction).filter(AppFunction.id == function_id).first()

        if not function:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"App Function ID {function_id} Not Found."
            )
        
        exist = self._find_by_function_id(function_id)

        if exist:
            exist.permission = permissions
            self.db.commit()
            self.db.refresh(exist)
            return exist
        else:
            function_permission = AppFuncPermission(
                function_id=function_id,
                permission=permissions
            )

            self.db.add(function_permission)
            self.db.commit()
            self.db.refresh(function_permission)

            return function_permission

    def delete_function_permission(self, permission_id: int) -> AppFuncPermission:
        permission = self.get_app_permission_id(permission_id)

        self.db.delete(permission)
        self.db.commit()
        return permission

    def delete_by_function_id(self, function_id: int) -> AppFuncPermission:
        permission = self.get_app_function_permission_id(function_id)

        self.db.delete(permission)
        self.db.commit()

        return permission