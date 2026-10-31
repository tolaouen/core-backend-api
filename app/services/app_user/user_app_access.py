from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status


from app.models.users.app_user_access import AppUserAccess
from app.schemas.users.user_app_access import (
    AppUserAccessCreate,
    AppUserAccessBulkCreate,
    AppUserAccessUpdate,
)


class AppUserAccessService():

    def __init__(self, db: Session):
        self.db = db

    def get_all_app_user_access(self) -> List[AppUserAccess]:
        app_access = self.db.query(AppUserAccess).all()
        return app_access

    def get_app_user_access_by_id(self, access_id: int) -> AppUserAccess:
        app_access = (
            self.db.query(AppUserAccess)
            .filter(AppUserAccess.id == access_id)
            .first()
        )
        if not app_access:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="App user access not found",
            )
        return app_access

    def get_app_user_access_by_user(self, user_id: int) -> List[AppUserAccess]:
        return (
            self.db.query(AppUserAccess)
            .filter(AppUserAccess.user_id == user_id)
            .all()
        )

    def get_app_user_access_by_user_and_type(
        self, user_id: int, type: str
    ) -> List[AppUserAccess]:
        return (
            self.db.query(AppUserAccess)
            .filter(
                AppUserAccess.user_id == user_id,
                AppUserAccess.type == type,
            )
            .all()
        )

    def create_app_user_access(
        self, obj_in: AppUserAccessCreate
    ) -> AppUserAccess:
        existing = self.db.query(AppUserAccess).filter(
            AppUserAccess.user_id == obj_in.user_id,
            AppUserAccess.ref_id == obj_in.ref_id,
            AppUserAccess.type == obj_in.type
        ).first()

        if existing:
            raise HTTPException(
                detail="App User Access is Already Existing.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        db_obj = AppUserAccess(
            user_id=obj_in.user_id,
            ref_id=obj_in.ref_id,
            type=obj_in.type,
        )

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def bulk_create_app_user_access(
        self, obj_in: AppUserAccessBulkCreate
    ) -> List[AppUserAccess]:
        if len(obj_in.items) != len(obj_in.ref_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="items and ref_ids must have the same length.",
            )
        db_objs = [
            AppUserAccess(user_id=obj_in.user_id, ref_id=ref_id, type=access_type)
            for access_type, ref_id in zip(obj_in.items, obj_in.ref_ids, strict=True)
        ]
        self.db.add_all(db_objs)
        self.db.commit()
        for obj in db_objs:
            self.db.refresh(obj)
        return db_objs

    def update_app_user_access(
        self, access_id: int, obj_in: AppUserAccessUpdate
    ) -> Optional[AppUserAccess]:
        db_obj = self.get_app_user_access_by_id(access_id)

        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="App Access Not Found."
            )

        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete_app_user_access(self, access_id: int) -> None:
        db_obj = self.get_app_user_access_by_id(access_id)

        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"App Access {access_id} Not Found."
            )
        
        self.db.delete(db_obj)
        self.db.commit()

    def delete_app_user_access_by_user(self, user_id: int) -> int:
        deleted = (
            self.db.query(AppUserAccess)
            .filter(AppUserAccess.user_id == user_id)
            .delete(synchronize_session=False)
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="App Access Not Found."
            )
        self.db.commit()
        return deleted

    def replace_user_access(
        self, user_id: int, type: str, ref_ids: List[int]
    ) -> List[AppUserAccess]:
        """Remove all existing access of a given type for a user, then re-create it."""
        self.db.query(AppUserAccess).filter(
            AppUserAccess.user_id == user_id,
            AppUserAccess.type == type,
        ).delete(synchronize_session=False)

        db_objs = [
            AppUserAccess(user_id=user_id, ref_id=ref_id, type=type)
            for ref_id in ref_ids
        ]
        self.db.add_all(db_objs)
        self.db.commit()
        for obj in db_objs:
            self.db.refresh(obj)
        return db_objs