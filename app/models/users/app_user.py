from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.databases.db import Base


class Apps(Base):
    __tablename__ = "apps"
    id = Column(Integer, primary_key=True, index=True)
    permission_id = Column(Integer, ForeignKey("app_permissions.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(100), nullable=False)
    base_url = Column(String(255), nullable=False)
    app_code = Column(String(50), nullable=False)
    status = Column(String(10), default="ACT")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_apps = relationship("UserApp", back_populates="app", cascade="all, delete-orphan")
    app_permission = relationship("AppPermission", back_populates="apps")

    app_functions = relationship(
        "AppFunction", back_populates="app", cascade="all, delete-orphan"
    )

 
    
class UserApp(Base):
    __tablename__ = "user_app"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    app_code = Column(String(50), nullable=False)
    status = Column(String(10), default="ACT")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="user_apps")
    app = relationship("Apps", back_populates="user_apps")
