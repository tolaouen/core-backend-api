from sqlalchemy import Column, Integer, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.databases.db import Base

class AppRoleFunction(Base):
    __tablename__ = "app_role_function"

    id = Column(Integer, primary_key=True, index=True)

    role_id = Column(Integer, ForeignKey("app_roles.id", ondelete="CASCADE"), nullable=False, index=True)
    function_id = Column(Integer, ForeignKey("app_func.id", ondelete="CASCADE"), nullable=False, index=True)

    permissions = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    role = relationship("AppRole", back_populates="role_functions")
    function = relationship("AppFunction", back_populates="role_functions")
    