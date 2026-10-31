from sqlalchemy import Column, String, Integer, DateTime, func
from sqlalchemy.orm import relationship
from app.databases.db import Base

class AppPermission(Base):
    __tablename__ = "app_permissions"

    id = Column(Integer, primary_key=True, index=True)
    
    label = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    apps = relationship("Apps", back_populates="app_permission", cascade="all, delete-orphan")