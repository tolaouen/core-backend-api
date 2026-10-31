from typing import  Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.users.app_user import Apps, UserApp
# from app.models.users.user import User
from app.schemas.users.user_app import UserAppCreate, UserAppUpdate
from app.utils.query_builder import build_query
from app.utils.paginations import paginate

from app.schemas.Responses.pagination import PaginatedResponse

class UserAppService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_user_app(
            self, 
            page: int = 1,
            page_size: int = 10,
            app_code: Optional[str] = None,
            status: Optional[str] = None
    ) -> PaginatedResponse[UserApp]:
        query = self.db.query(UserApp)

        filters = {}
        if app_code:
            filters[UserApp.app_code] = app_code
        if status:
            filters[UserApp.status] = status

        query = build_query(query=query, filters=filters)

        return paginate(query, page=page, page_size=page_size)
    
    def get_user_app_by_id(self, user_id: int) -> Optional[UserApp]:
        user = self.db.query(UserApp).filter(UserApp.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User by {user_id} Not Found."
            )
        
        return user
    
    def create_user_app(self, data: UserAppCreate) -> UserApp:
        app = self.db.query(Apps).filter(Apps.id == data.app_id).first()
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"App with id {data.app_id} not found."
            )

        # user = self.db.query(User).filter(User.id == data.user_id).first()
        # if not user:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"User with id {data.user_id} not found."
        #     )

        user_app = self.db.query(UserApp).filter(
            UserApp.user_id == data.user_id,
            UserApp.app_id == data.app_id,
        ).first()
        if user_app:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {data.user_id} is already assigned to app {data.app_id}."
            )

        item_data = data.model_dump()
        item_data["app_code"] = app.app_code
        item = UserApp(**item_data)

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return item 
    
    def update_user_app(self, user_id: int, data: UserAppUpdate) -> Optional[UserApp]:
        item = self.get_user_app_by_id(user_id)

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Not Found."
            )
        
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(item, field, value)

        self.db.commit()
        self.db.refresh(item)

        return item

    def delete_user_app(self, user_id: int) -> Optional[UserApp]:
        item = self.get_user_app_by_id(user_id)

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Not Found."
            )

        self.db.delete(item)
        self.db.commit()
        return item  