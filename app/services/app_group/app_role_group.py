from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.app_group.app_role_group import AppRoleGroupCreate, AppRoleGroupUpdate
from app.models.app_group.app_group_role import AppGroupRole

class AppRoleGroupService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_role_groups(self) -> List[AppGroupRole]:
        return self.db.query(AppGroupRole).all()

    def get_role_group_by_id(self, role_group_id: int) -> Optional[AppGroupRole]:
        role_group = self.db.query(AppGroupRole).filter(AppGroupRole.id == role_group_id).first()
        if not role_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"App Role Group ID {role_group_id} Not Found."
            )
        return role_group

    def create_role_group(self, data: AppRoleGroupCreate) -> AppGroupRole:
        existing_role_group = self.db.query(AppGroupRole).filter(
            (AppGroupRole.group_id == data.group_id) & (AppGroupRole.role_id == data.role_id)
        ).first()
        if existing_role_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="App Role Group with the same group_id and role_id already exists."
            )
        role_group = AppGroupRole(**data.model_dump())
        self.db.add(role_group)
        self.db.commit()
        self.db.refresh(role_group)
        return role_group

    def update_role_group(self, role_group_id: int, data: AppRoleGroupUpdate) -> Optional[AppGroupRole]:
        role_group = self.get_role_group_by_id(role_group_id)
        if not role_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"App Role Group ID {role_group_id} Not Found."
            )

        data_field = data.model_dump(exclude_unset=True)

        if data_field.get("group_id") and data_field.get("role_id"):
            existing_role_group = self.db.query(AppGroupRole).filter(
                (AppGroupRole.group_id == data_field["group_id"]) &
                (AppGroupRole.role_id == data_field["role_id"]) &
                (AppGroupRole.id != role_group_id)
            ).first()
            if existing_role_group:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="App Role Group with the same group_id and role_id already exists."
                )

        for key, value in data_field.items():
            setattr(role_group, key, value)

        self.db.commit()
        self.db.refresh(role_group)
        return role_group
