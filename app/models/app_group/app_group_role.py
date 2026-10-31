from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.databases.db import Base

class AppGroupRole(Base):
    __tablename__ = "app_group_roles"

    id = Column(Integer, primary_key=True, index=True)

    group_id = Column(Integer, ForeignKey("app_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("app_roles.id", ondelete="CASCADE"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    group = relationship("AppGroup", back_populates="group_roles")
    role = relationship("AppRole", back_populates="group_roles")