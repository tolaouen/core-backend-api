from sqlalchemy import Column, Integer, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship
from app.databases.db import Base


class AppUserPermission(Base):
    __tablename__ = "app_user_permissions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    function_id = Column(Integer, ForeignKey("app_func.id", ondelete="CASCADE"), nullable=False, index=True)

    permissions = Column(JSON, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relation with user and app function
    user = relationship("User", back_populates="user_permissions")
    function = relationship("AppFunction", back_populates="user_permission")

    @property
    def function_name(self) -> str | None:
        return self.function.name if self.function else None

    @property
    def app_code(self) -> str | None:
        return self.function.app_code if self.function else None
    
    