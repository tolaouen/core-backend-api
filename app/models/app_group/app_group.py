from sqlalchemy import Column, String, Integer, DateTime, Enum, func
from sqlalchemy.orm import relationship
from app.databases.db import Base

class AppGroup(Base):
    __tablename__ = "app_groups"

    id = Column(Integer, primary_key=True, index=True)
    
    name = Column(String(255), nullable=False)
    app_code = Column(String(255), nullable=False)
    code = Column(String(255), nullable=False)
    status = Column(Enum("ACT", "INC", "DEL", name="group_status"), default="ACT")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    group_roles = relationship("AppGroupRole", back_populates="group", cascade="all, delete-orphan")

