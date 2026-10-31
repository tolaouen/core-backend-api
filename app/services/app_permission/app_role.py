from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.Responses.pagination import PaginatedResponse
from app.schemas.app_role import RoleCreate, RoleUpdate
from app.models.app_role.app_roles import AppRole
from app.utils.paginations import paginate
from app.utils.query_builder import build_query

class AppRoleService:
    def __init__(self, db: Session):
        self.db = db

    def get_role(
        self, 
        page: int = 1,
        page_size: int = 10,
        name: Optional[str] = None,
        code: Optional[str] = None,
        status: Optional[str] = None,
    ) -> PaginatedResponse[AppRole]:
        query = self.db.query(AppRole)

        filters = {}
        if name:
            filters[AppRole.name] = name
        if code:
            filters[AppRole.code] = code
        if status:
            filters[AppRole.status] = status

        query = build_query(query=query, filters=filters)

        return paginate(query, page=page, page_size=page_size)

    def get_role_by_id(self, role_id: int) -> Optional[AppRole]:
        role = self.db.query(AppRole).filter(AppRole.id == role_id).first()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"App Role ID {role_id} Not Found."
            )
        
        return role
    
    def create_role(self, data: RoleCreate) -> Optional[AppRole]:
        dup_role = self.db.query(AppRole).filter(AppRole.name == data.name, AppRole.code == data.code).first()

        if dup_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"App Role Name {data.name} or Code {data.code} Already Exists."
            )
        
        item = AppRole(**data.model_dump())

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return item
    
    def update_role(self, role_id: int, data: RoleUpdate) -> Optional[AppRole]:
        role = self.get_role_by_id(role_id)

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"App Role ID {role_id} Not Found."
            )
        
        update_data = data.model_dump(exclude_unset=True)

        for fields, value in update_data.items():
            setattr(role, fields, value)

        self.db.commit()
        self.db.refresh(role)

        return role
    
    def delete_role(self, role_id: int) -> Optional[AppRole]:
        item = self.get_role_by_id(role_id)

        if not item:
            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail=f"App Role ID {role_id} Not Found."
            )
        
        self.db.delete(item)
        self.db.commit()

        return item
    