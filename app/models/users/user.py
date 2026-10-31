from sqlalchemy import Column, Integer, String, DateTime, Boolean,Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.databases.db import Base

class User(Base) :
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)

    password_hashed = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    phone = Column(String(255), nullable=False)
    user_type = Column(String(255), nullable=False, default="user")
    user_role = Column(String(255), nullable=False, default="guest")

    profile: Mapped[str] = mapped_column(Text, nullable=False, default="")
    gender = Column(String(255), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


    user_apps = relationship(
        "UserApp", back_populates="user", cascade="all, delete-orphan"
    )

    user_permissions = relationship(
        "AppUserPermission", back_populates="user", cascade="all, delete-orphan"
    )

    user_access = relationship(
        "AppUserAccess", back_populates="user", cascade="all, delete-orphan"
    )

    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
