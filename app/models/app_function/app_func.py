from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.databases.db import Base
from app.constants.constant import Is_ParentType

class AppFunction(Base):
    __tablename__ = "app_func"

    id = Column(Integer, primary_key=True, index=True)
    
    app_id = Column(Integer, ForeignKey("apps.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(255), nullable=False)
    type = Column(String(255), nullable=False)
    parent_id = Column(Integer, nullable=True)
    is_parent = Column(String(255), nullable=True, default=Is_ParentType.Child.value)
    sector = Column(String(255), nullable=True)
    path = Column(String(255), nullable=True)
    app_code = Column(String(255), nullable=False)
    icon = Column(String(255), nullable=True)
    is_show = Column(Boolean, default=True)
    order = Column(Integer, nullable=True)
    status = Column(Enum("ACT", "INC", "DEL", name="function_status"), default="ACT")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    function_permissions = relationship(
        "AppFuncPermission", back_populates="function", cascade="all, delete-orphan",
    )

    user_permission = relationship(
        "AppUserPermission", back_populates="function", cascade="all, delete-orphan"
    )

    role_functions = relationship(
        "AppRoleFunction", back_populates="function", cascade="all, delete-orphan"
    )

    app = relationship("Apps", back_populates="app_functions")