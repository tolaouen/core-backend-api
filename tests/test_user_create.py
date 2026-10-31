import asyncio

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.v1.endpoints.users.user import create_user
from app.core.security import verify_password
from app.models.users.user import User
from app.schemas.users.user import UserCreate


def test_create_user_hashes_password_and_sets_full_name():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    User.__table__.create(bind=engine)

    db = SessionLocal()
    try:
        payload = UserCreate(
            first_name="Jane",
            last_name="Doe",
            username="janedoe",
            email="jane@example.com",
            phone="1234567890",
            gender="female",
            password="StrongPass1",
            verify_password="StrongPass1",
        )

        created = asyncio.run(create_user(payload, db))

        assert created.full_name == "Jane Doe"
        assert created.password_hashed != "StrongPass1"
        assert verify_password("StrongPass1", created.password_hashed) is True
    finally:
        db.close()
