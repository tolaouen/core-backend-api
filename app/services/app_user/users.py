from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, extract
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from zoneinfo import ZoneInfo
from datetime import datetime, time, timedelta
# from fastapi import UploadFile 

from app.models.users.user import User
from app.schemas.users.user import (
    UserCountTrend,
    UserCreate,
    UserDetailResponse,
    UserResponse,
    UserTrendResponse,
    UserUpdate,
)
from app.constants.constant import RoleEnum, UserRoleEnum
from app.utils.query_builder import build_query
from app.utils.paginations import paginate
from app.core.security import hash_password
from app.utils.format.format_phone_cambodia import format_cambodia_phone
from app.schemas.users.user_app_access import  AppUserAccessInDBBase
from app.schemas.users.user_app import UserAppResponse
from app.schemas.app_permission.app_user_permission import UserPermissionResponse
from app.services.uploads.upload_service import UploadService

from app.schemas.Responses.pagination import PaginatedResponse


class UserService:
    def __init__(self, db: Session, uploader: Optional[UploadService] = None):
        self.db = db
        self.uploader = uploader or UploadService()

    def get_all_user(
            self,
            page: int = 1,
            page_size: int = 10,
    ) -> PaginatedResponse[User]:
        query = self.db.query(User)

        query = build_query(query=query)

        return paginate(query, page=page, page_size=page_size)

    def get_active_user_count(self) -> int:
        return self.db.query(User).filter(User.is_active == True).count()
    
    def get_female_user_count(self) -> int:
        return self.db.query(User).filter(User.gender == "F").count()

    def get_user_email_verified(self) -> int:
        return self.db.query(User).filter(User.email_verified.is_(True)).count()

    def get_user_register_today(self) -> int:
        tz = ZoneInfo("Asia/Phnom_Penh")
        start = datetime.combine(datetime.now(tz).date(), time.min, tzinfo=tz)
        end = start + timedelta(days=1)

        return  self.db.query(User).filter(User.created_at >= start, User.created_at < end).count()
    
    # ===========================
    # Count User Trend by year
    # ===========================
    def counter_user_trend(self, year: Optional[int] = None) -> list[UserTrendResponse]:
        tz = ZoneInfo("Asia/Phnom_Penh")
        if year is None:
            year = datetime.now(tz).year
        start = datetime(year, 1, 1, tzinfo=tz)
        end = datetime(year + 1, 1, 1, tzinfo=tz)

        rows = (
            self.db.query(
                extract("month", User.created_at).label("month"),
                func.count(User.id).label("count"),
            )
            .filter(User.created_at >= start, User.created_at < end)
            .group_by("month")
            .all()
        )

        counts = {
            int(row._mapping["month"]): int(row._mapping["count"])
            for row in rows
        }
        names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        return [
            UserTrendResponse(
                year=year,
                data=[
                    UserCountTrend(month=names[month - 1], count=counts.get(month, 0))
                    for month in range(1, 13)
                ],
            )
        ]
    
    def get_all_user_id(self, id: int) -> User:
        users = self.db.query(User).filter(User.id == id).first()

        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User_Id {id} Not_Found."
            )

        return users
    
    def get_user_detail(self, user_id: int) -> UserDetailResponse:
        user = (
            self.db.query(User)
            .options(
                joinedload(User.user_apps),
                joinedload(User.user_permissions),
                joinedload(User.user_access),
            )
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # only keep GROUP-type rows for the raw user_access field
        group_access = [a for a in user.user_access if a.type == "ROLE" or a.type == "FUNCTION" or a.type == "GROUP"]

        return UserDetailResponse(
            **UserResponse.model_validate(user).model_dump(),
            user_apps=[UserAppResponse.model_validate(a) for a in user.user_apps],
            user_permissions=[UserPermissionResponse.model_validate(p) for p in user.user_permissions],
            user_access=[AppUserAccessInDBBase.model_validate(a) for a in group_access],
        )

    def create_user(self, data: UserCreate) -> User:
        # Validate password confirmation
        if data.password != data.verify_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match."
            )
        
        # Check if email already exists
        existing = self.db.query(User).filter(User.email == data.email).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="User Already Existing."
            )

        # Check if username already exists
        existing_username = self.db.query(User).filter(User.username == data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken."
            )

        # Generate full name
        full_name = " ".join(part for part in [data.first_name.strip(), data.last_name.strip()] if part).strip()
        phone = format_cambodia_phone(data.phone)
        # Create user with hashed password
        item = User(
            first_name=data.first_name,
            last_name=data.last_name,
            full_name=full_name,
            username=data.username,
            email=data.email,
            password_hashed=hash_password(data.password),
            phone=phone,
            gender=data.gender,
            user_type=str(data.user_type.value) if isinstance(data.user_type, RoleEnum) else (data.user_type or RoleEnum.USER.value),
            user_role=str(data.user_role.value) if isinstance(data.user_role, UserRoleEnum) else (data.user_role or UserRoleEnum.GUEST.value),
            profile="",
            is_active=True,
            email_verified=False,
        )

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return item

    def update_user(self, id: int, data: UserUpdate) -> Optional[User]:
        item = self.get_all_user_id(id)

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User Update by {id} Not Found."
            )

        # Every user column is NOT NULL, so an explicit null means "leave unchanged"
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        if update_data.get("username"):
            taken = self.db.query(User).filter(User.username == update_data["username"], User.id != id).first()
            if taken:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken."
                )

        if update_data.get("email"):
            taken = self.db.query(User).filter(User.email == update_data["email"], User.id != id).first()
            if taken:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already in use."
                )

        if "phone" in update_data:
            update_data["phone"] = format_cambodia_phone(update_data["phone"])

        if "first_name" in update_data or "last_name" in update_data:
            first_name = update_data.get("first_name", item.first_name) or ""
            last_name = update_data.get("last_name", item.last_name) or ""
            item.full_name = " ".join(part for part in [first_name.strip(), last_name.strip()] if part).strip()

        for field, value in update_data.items():
            if field == "user_type" and isinstance(value, RoleEnum):
                value = value.value
            if field == "user_role" and isinstance(value, UserRoleEnum):
                value = value.value
            setattr(item, field, value)

        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already in use."
            ) from exc
        self.db.refresh(item)
        return item

    async def upload_profile(self, user_id: int, file: UploadFile) -> User:
        user = self.get_all_user_id(user_id)
 
        new_url = await self.uploader.save_image(
            file,
            folder="profiles",
            prefix=str(user.id),
            max_dimension=512,
        )
 
        old_profile = user.profile
        try:
            user.profile = new_url
            self.db.commit()
        except Exception:
            self.db.rollback()
            await run_in_threadpool(self.uploader.delete, new_url)
            raise
 
        await run_in_threadpool(self.uploader.delete, old_profile)
        self.db.refresh(user)
        return user
    
    def delete_profile(self, user_id: int) -> User:
        user = self.get_all_user_id(user_id)
 
        old_profile = user.profile
        user.profile = "" 
        self.db.commit()
        self.db.refresh(user)
 
        self.uploader.delete(old_profile)
        return user

    def delete_user(self, id: int) -> Optional[User]:
        item = self.get_all_user_id(id)

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User Delete by {id} Not Found."
            )
        older_profile = item.profile
        self.db.delete(item)
        self.db.commit()

        if older_profile:
            try: 
                self.uploader.delete(older_profile)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to delete profile file {e}"
                )
                 
        return item
