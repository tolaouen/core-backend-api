from sqlalchemy import Column, Integer, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.databases.db import Base


class AppFuncPermission(Base):
    __tablename__="app_func_permissions"

    id = Column(Integer, primary_key=True, index=True)
    function_id = Column(Integer, ForeignKey("app_func.id", ondelete="CASCADE"), nullable=False)
    
    permission = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    function = relationship("AppFunction", back_populates="function_permissions")

    @property
    def permissions(self):
        return self.permission

    @permissions.setter
    def permissions(self, value):
        self.permission = value