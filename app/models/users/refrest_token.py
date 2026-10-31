from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.databases.db import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    token = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="refresh_tokens")
