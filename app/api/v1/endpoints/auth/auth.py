from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.deps import get_current_user
from app.dependencies.session import session
from app.schemas.users.auth import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ResendOTPRequest,
    ResendOTPResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    SignupCompleteResponse,
    SignupRequestResponse,
    SignupRequestSchema,
    VerifyOTPSchema,
)

from app.services.auth.auth import AuthService
from app.models.users.user import User

auth_router = APIRouter()

@auth_router.post("/signup/request", response_model=SignupRequestResponse)
async def signup(request: SignupRequestSchema, db: Session = session):
    result = await AuthService(db).request_signup_otp(email=request.email, username=request.username)

    return result

@auth_router.post("/signup/verify", response_model=SignupCompleteResponse)
async def verify_otp_and_completed_signup(request: VerifyOTPSchema, db: Session = session):
    user = await AuthService(db).verify_otp_and_signup(
        email=request.email,
        otp=request.otp,
        password=request.password,
        username=request.username or request.email.split("@")[0],
    )
    return {
        "message": "Signup successful! You can now login.",
        "user_id": user.id,
        "email": user.email,
        "username": user.username,
    }

@auth_router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = session):
    result =  AuthService(db).login(
        email = request.email,
        password= request.password
    )

    return  result

@auth_router.post("/logout", response_model=LogoutResponse)
async def logout(request: LogoutRequest, current_user: User = Depends(get_current_user), db: Session = session):
    result = AuthService(db).logout(
        refresh_token=request.refresh_token,
        user_id=str(current_user.id)
    )
    return result

@auth_router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: Session = session):
    result = AuthService(db).refresh_access_token(
        refresh_token=request.refresh_token,
    )
    return result

@auth_router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(request: ForgotPasswordRequest, db: Session = session):
    result = await AuthService(db).request_password_reset(
        email=request.email
    )
    return result

@auth_router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(request: ResetPasswordRequest, db: Session = session):
    result = await AuthService(db).reset_password_with_otp(
        email=request.email,
        otp=request.otp,
        new_password=request.new_password,
    )
    return result

@auth_router.post("/resend-otp", response_model=ResendOTPResponse)
async def resend_otp(request: ResendOTPRequest, db: Session = session):
    result = await AuthService(db).resend_otp(
        email=request.email,
        purpose=request.purpose,
    )
    return result

@auth_router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(request: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = session):
    result = await AuthService(db).change_password(
        user_id=str(current_user.id),
        current_password=request.current_password,
        new_password=request.new_password,
    )
    return result


