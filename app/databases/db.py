import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

if engine:
    print("✅ connected is successfully.")
else:
    print("❌ connected is false.")

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()