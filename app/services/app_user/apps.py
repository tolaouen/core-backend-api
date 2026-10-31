from typing import  Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.users.app_user import Apps
from app.models.app_permissions.app_permission import AppPermission
from app.schemas.users.apps import AppCreate, AppUpdate


class AppsService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_apps(self) -> List[Apps]:
        return self.db.query(Apps).all()

    def get_app_by_id(self, app_id: int) -> Optional[Apps]:
        app = self.db.query(Apps).filter(Apps.id == app_id).first()

        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"App with ID {app_id} not found."
            )
        
        return app

    def get_apps_by_permission_id(self, permission_id: int) -> List[Apps]:
        apps = self.db.query(Apps).filter(Apps.permission_id == permission_id).all()

        if not apps:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No apps found for permission ID {permission_id}."
            )

        return apps

    def create_app(self, data: AppCreate) -> Apps:
        app_data = data.model_dump()

        if data.permission_id is not None:
            permission = (
                self.db.query(AppPermission)
                .filter(AppPermission.id == data.permission_id)
                .first()
            )
            if not permission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Permission ID {data.permission_id} not found.",
                )

            app_data["app_code"] = permission.value

        item = Apps(**app_data)

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return item

    def update_app(self, app_id: int, data: AppUpdate) -> Apps:
        app = self.get_app_by_id(app_id)
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"App with ID {app_id} not found."
            )
        
        data_field = data.model_dump(exclude_unset=True)

        if data.permission_id is not None:
            permission = (
                self.db.query(AppPermission)
                .filter(AppPermission.id == data.permission_id)
                .first()
            )
            if not permission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Permission ID {data.permission_id} not found.",
                )

            data_field["app_code"] = permission.value

        for key, value in data_field.items():
            setattr(app, key, value)

        self.db.commit()
        self.db.refresh(app)

        return app