from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.app_group.app_group import AppGroupCreate, AppGroupUpdate
from app.models.app_group.app_group import AppGroup

class AppGroupService:
    def __init__(self, db: Session):
        self.db = db   

    def get_all_groups(self) -> List[AppGroup]:
        return self.db.query(AppGroup).all()

    def get_group_by_id(self, group_id: int) -> Optional[AppGroup]:
        group = self.db.query(AppGroup).filter(AppGroup.id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"App Group ID {group_id} Not Found."
            )
        return group

    def create_group(self, data: AppGroupCreate) -> AppGroup:
        existing_group = self.db.query(AppGroup).filter(
            (AppGroup.name == data.name) | (AppGroup.code == data.code)
        ).first()
        if existing_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="App Group with the same name or code already exists."
            )   
        group = AppGroup(**data.model_dump())
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group

    def update_group(self, group_id: int, data: AppGroupUpdate) -> Optional[AppGroup]:
        group = self.get_group_by_id(group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"App Group ID {group_id} Not Found."
            )

        data_field = data.model_dump(exclude_unset=True)

        if data_field.get("name"):
            existing_group = self.db.query(AppGroup).filter(
                AppGroup.name == data_field["name"],
                AppGroup.id != group_id
            ).first()
            if existing_group:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="App Group with the same name already exists."
                )
            
        for key, value in data_field.items():
            setattr(group, key, value)
        self.db.commit()
        self.db.refresh(group)
        return group
