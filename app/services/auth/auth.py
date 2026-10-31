from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.users.refrest_token import RefreshToken
from app.models.users.user import User
from app.models.users.otp import OTP
from app.core.config import settings
from app.services.auth.email_services import EmailService
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)

from app.constants.constant import OTPPurposeEnum


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    async def request_signup_otp(self, email: str, username: str) -> dict:
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email Already Register."
            )
        
        existing_username = self.db.query(User).filter(User.username == username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Username Already Existing."
            )
        otp_code = EmailService.generate_otp()

        self.db.query(OTP).filter(OTP.identifier == email, OTP.purpose == OTPPurposeEnum.SIGNUP).delete()

        otp_record = OTP(
            identifier=email,
            code=otp_code,
            purpose=OTPPurposeEnum.SIGNUP,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
        )
        self.db.add(otp_record)
        self.db.commit()

        await EmailService.send_otp_email(email, otp_code, OTPPurposeEnum.SIGNUP)

        return {
            "message": "OTP sent to your email",
            "email": email,
            "expires_in_minutes": settings.OTP_EXPIRE_MINUTES,
        }
    
    async def verify_otp_and_signup(
            self, email: str, otp:str, password: str, username: str
    )-> User:
        otp_record = self.db.query(OTP).filter(OTP.identifier == email, OTP.purpose == OTPPurposeEnum.SIGNUP, OTP.is_verified.is_(False)).order_by(OTP.created_at.desc()).first()
        
        if not otp_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP Not Found or Already Used.",
            )
        if datetime.now(timezone.utc) > otp_record.expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired. Please request a new one.",
            )
        if otp_record.attempts >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed attempts. Please request a new OTP.",
            )
        if otp_record.code != otp:
           otp_record.attempts +=1
           self.db.commit()
           raise HTTPException(
               status_code=status.HTTP_400_BAD_REQUEST,
               detail=f"Invalid OTP. {5 - otp_record.attempts} attempts remaining.",
           )

        if self.db.query(User).filter(User.email == email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email Already Register."
            )
        if self.db.query(User).filter(User.username == username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username Already Existing."
            )

        new_user = User(
            username=username,
            email=email,
            password_hashed=hash_password(password),
            email_verified=True,
            is_active=True,
            first_name="",
            last_name="",
            full_name="",
            phone="",
            profile="",
            gender="",
        )
        self.db.add(new_user)
        otp_record.is_verified = True
        self.db.commit()
        self.db.refresh(new_user)

        await EmailService.send_welcome_email(email, username)
        return new_user
    
    # ====================
    # Login Access
    # ====================
    def login(self, email: str, password: str) -> dict:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
            )

        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email first",
            )

        if not verify_password(password, str(user.password_hashed)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated"
            )                                  

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        refresh_token_record = RefreshToken(
            user_id = user.id,
            token = refresh_token,
            expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )

        self.db.add(refresh_token_record)
        self.db.commit()

        return {
            "message": "Login Successful",
            "user": {
                "id": user.id,
                "username": user.username, 
                "email": user.email
            },
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            },
        }
    
    def logout(self, refresh_token: str, user_id: str) -> dict:
        payload = decode_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        token_record = self.db.query(RefreshToken).filter(RefreshToken.token == refresh_token, RefreshToken.user_id == int(user_id), RefreshToken.revoked.is_(False)).first()
        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh Token not found or has been revoked."
            )
        token_record.revoked = True

        self.db.commit()
        return {"message": "Logged out successfully."}                      
    
    def refresh_access_token(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if not payload :
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalids or expired refresh token"
            )
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        user_id = int(payload["sub"])
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token Payload."
            )
        
        token_record = self.db.query(RefreshToken).filter(RefreshToken.token == refresh_token, RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False)).first()
        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh Token not found or has been revoked."
            )
        if datetime.now(timezone.utc) > token_record.expires_at:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired. Please login again."
            )
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Access Not Found"
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User Account is Inactive."
            )
        # New Token access
        new_access_token = create_access_token(data={"sub": str(user.id)})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
        token_record.revoked = True

        new_token_record = RefreshToken(
            user_id = user.id,
            token=new_refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(new_token_record)
        self.db.commit()

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
    
    async def request_password_reset(self, email: str) -> dict:
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            return {
                "message": "If your email is registered, you will receive a password reset code",
                "email": email,
                "expires_in_minutes": settings.OTP_EXPIRE_MINUTES,
            }
        
        otp_code = EmailService.generate_otp()

        self.db.query(OTP).filter(OTP.identifier == email, OTP.purpose == OTPPurposeEnum.PASSWORD_RESET).delete()

        otp_record = OTP(
            identifier = email,
            code=otp_code,
            purpose=OTPPurposeEnum.PASSWORD_RESET,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        )

        self.db.add(otp_record)
        self.db.commit()

        await EmailService.send_otp_email(email, otp_code, "password reset")

        return {
            "message": "If your email is registered, you will receive a password reset code",
            "email": email,
            "expires_in_minutes": settings.OTP_EXPIRE_MINUTES,
        }
    
    async def reset_password_with_otp(self,otp: str, email: str, new_password: str) -> dict:
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        otp_record = self.db.query(OTP).filter(OTP.identifier == email, OTP.purpose == OTPPurposeEnum.PASSWORD_RESET, OTP.is_verified.is_(False)).order_by(OTP.created_at.desc()).first()

        if not otp_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP not found or already used."
            )
        if datetime.now(timezone.utc) > otp_record.expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired. Please request a new one.",
            )  
        
        if otp_record.attempts >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed attempts. Please request a new OTP.",
            )

        if otp_record.code != otp:
            otp_record.attempts += 1
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid OTP. {5 - otp_record.attempts} attempts remaining.",
            )  
        user.password_hashed = hash_password(new_password)

        otp_record.is_verified = True

        self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id, RefreshToken.revoked.is_(False)
        ).update({"revoked": True})

        self.db.commit()

        await EmailService.send_password_reset_confirmation(email, str(user.username))

        return {
            "message": "Password reset successful. Please login with your new password."
        }
    
    async def resend_otp(self, email: str, purpose: str) -> dict:
        if purpose not in [OTPPurposeEnum.SIGNUP, OTPPurposeEnum.PASSWORD_RESET]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Purpose must be 'signup' or 'password_reset'",
            )            

        if purpose == OTPPurposeEnum.SIGNUP:
            existing_user = self.db.query(User).filter(User.email == email).first()
            if existing_user and existing_user.email_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already verified. Please login.",
                )
        if purpose == OTPPurposeEnum.PASSWORD_RESET:
            user = self.db.query(User).filter(User.email == email).first()
            if not user:
                return {
                    "success": True,
                    "message": "If your email is registered, a new OTP has been sent",
                    "email": email,
                    "expires_in_minutes": settings.OTP_EXPIRE_MINUTES,
                }

        existing_otp = (
            self.db.query(OTP)
            .filter(
                OTP.identifier == email,
                OTP.purpose == purpose,
                OTP.is_verified.is_(False),
            )
            .order_by(OTP.created_at.desc())
            .first()
        )

        if existing_otp:
            time_since_last = datetime.now(timezone.utc) - existing_otp.created_at
            if time_since_last < timedelta(seconds=settings.RESEND_COOLDOWN_SECONDS):
                retry_after = settings.RESEND_COOLDOWN_SECONDS - int(
                    time_since_last.total_seconds()
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Please wait {retry_after} seconds before requesting another OTP",
                    headers={"Retry-After": str(retry_after)},
                )
        recent_otps_count = (
            self.db.query(OTP)
            .filter(
                OTP.identifier == email,
                OTP.purpose == purpose,
                OTP.created_at
                > datetime.now(timezone.utc)
                - timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
            )
            .count()
        )

        if recent_otps_count >= 3:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many OTP requests. Please try again in {settings.OTP_EXPIRE_MINUTES} minutes.",
            )

        otp_code = EmailService.generate_otp()

        self.db.query(OTP).filter(
            OTP.identifier == email,
            OTP.purpose == purpose,
            OTP.is_verified.is_(False),
        ).delete()

        otp_record = OTP(
            identifier=email,
            code=otp_code,
            purpose=purpose,
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
        )

        self.db.add(otp_record)
        self.db.commit()

        purpose_text = (
            OTPPurposeEnum.SIGNUP
            if purpose == OTPPurposeEnum.SIGNUP
            else OTPPurposeEnum.PASSWORD_RESET
        )
        await EmailService.send_otp_email(email, otp_code, purpose_text)

        return {
            "success": True,
            "message": f"A new OTP has been sent to {email}",
            "email": email,
            "expires_in_minutes": settings.OTP_EXPIRE_MINUTES,
        }
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> dict:
        user = self.db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if not verify_password(current_password, str(user.password_hashed)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters long",
            )
        if verify_password(new_password, str(user.password_hashed)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from current password",
            )

        user.password_hashed = hash_password(new_password)
        user.updated_at = datetime.now(timezone.utc)

        self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id, RefreshToken.revoked.is_(False)
        ).update({"revoked": True})

        self.db.commit()

        await EmailService.send_password_changed_email(
            email=str(user.email), username=str(user.username)
        )

        return {
            "message": "Password changed successfully. Please login again with your new password."
        }