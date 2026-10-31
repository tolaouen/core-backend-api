from sqlalchemy import Column, String, Integer, Enum, DateTime, func
from sqlalchemy.orm import relationship
from app.databases.db import Base

class AppRole(Base):
    __tablename__ = "app_roles"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)
    app_code = Column(String(255), nullable=False)
    code = Column(String(255), nullable=False)
    status = Column(Enum("ACT", "INC", "DEL", name="role_status"), default="ACT")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    role_functions = relationship("AppRoleFunction", back_populates="role", cascade="all, delete-orphan")
    group_roles = relationship("AppGroupRole", back_populates="role", cascade="all, delete-orphan")

