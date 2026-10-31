from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from app.databases.db import Base

class AppUserAccess(Base):
    __tablename__ = "app_user_access"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    ref_id = Column(Integer, nullable=False)
    type = Column(Enum("ROLE", "FUNCTION", "GROUP", name="access_type"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="user_access")