from sqlalchemy.orm import Session
from fastapi import APIRouter, status, Depends, Query, UploadFile, File
from typing import List, Optional

# from app.core.security import hash_password
from app.schemas.users.user import UserCountResponse, UserResponse, UserUpdate, UserCreate, UserDetailResponse, UserTrendResponse
from app.auth.deps import get_current_user
from app.databases.db import get_db
from app.models.users.user import User
from app.schemas.Responses.response import ApiResponse
from app.services.app_user.users import UserService

router = APIRouter()

@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return ApiResponse(
        message="Successfully retrieved user profile",
        status=200,
        data=current_user
    )

@router.post("/me/profile", response_model=ApiResponse[UserResponse])
async def upload_current_user_profile_image(
    file: UploadFile = File(..., description="JPEG, PNG or WEBP, max 5 MB"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
 ):
    user = await UserService(db).upload_profile(current_user.id, file)
 
    return ApiResponse(
        status=200,
        message="Profile image uploaded successfully.",
        data=user,
    )

@router.delete("/me/profile", response_model=ApiResponse[UserResponse])
def delete_current_user_profile_image(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = UserService(db).delete_profile(current_user.id)
    return ApiResponse(
        status=200,
        message="Profile image removed successfully.",
        data=user,
    )

@router.get("/count", response_model=ApiResponse[UserCountResponse])
async def get_user_count(db: Session = Depends(get_db)):
    service = UserService(db)
    total = service.get_active_user_count()
    female = service.get_female_user_count()
    email_verified = service.get_user_email_verified()
    register_today = service.get_user_register_today()

    return ApiResponse(
        status=200,
        message="Received user counts.",
        data=UserCountResponse(
            total_users=total,
            female_users=female,
            email_verified=email_verified,
            register_today=register_today
        )
    )

@router.get("/trend", response_model=ApiResponse[List[UserTrendResponse]])
def count_user_trend_app(db: Session = Depends(get_db), year: Optional[int] = Query(default=None, description="Defaults to the current year")):
    service = UserService(db).counter_user_trend(year)

    return ApiResponse(
        status=200,
        message="All User Trend",
        data=service,
    )

@router.get("", response_model= ApiResponse[List[UserResponse]])
async def get_all_users(db:Session = Depends(get_db)):
    users = db.query(User).all()
    return ApiResponse(
        status=200,
        message="Received all users.",
        data = users
    )

# Search Endpoint
@router.get("/search", response_model=ApiResponse[List[UserResponse]])
async def search_user(
    q: str = Query(default="", description="Search keyword for username, email, full name, or phone"),
    role_type: str | None = Query(default=None, description="Filter by role, e.g. Staff, Manager, Admin, Guest"),
    db: Session = Depends(get_db),
):
    query = db.query(User)

    if q:
        search_term = f"%{q.strip()}%"
        query = query.filter(
            (User.username.ilike(search_term)) |
            (User.email.ilike(search_term)) |
            (User.full_name.ilike(search_term)) |
            (User.phone.ilike(search_term))
        )

    if role_type:
        query = query.filter(User.user_role.ilike(role_type.strip()))

    users = query.order_by(User.id).all()

    return ApiResponse(
        status=200,
        message="Users matched your search." if q or role_type else "Received all users.",
        data=users,
    )

# User Detail 

@router.get("/{user_id}", response_model=ApiResponse[UserResponse])
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = UserService(db).get_all_user_id(user_id)

    return ApiResponse(
        status=200,
        message="Received single user",
        data=user
    )
@router.get("/{user_id}/detail", response_model=ApiResponse[UserDetailResponse], status_code=status.HTTP_200_OK)
async def get_user_detail(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db).get_user_detail(user_id)
    return ApiResponse(
        status=200,
        message="Reveived User Detail.",
        data=service
    )

@router.post("", response_model=UserResponse)
async def create_user(data: UserCreate, db: Session = Depends(get_db)):
    users = UserService(db).create_user(data)
    return users

@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(data: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return UserService(db).update_user(current_user.id, data)

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    users = UserService(db).update_user(user_id, data)
    return users

@router.delete("/me")
def delete_current_user_account(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    current_user.is_active = False
    db.commit()


    return {"message": "Account deactivated successfully"}
