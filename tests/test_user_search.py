
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.users.user import User


def test_search_user_filters_by_query():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    User.__table__.create(bind=engine)

    db = SessionLocal()
    try:
        db.add_all(
            [
                User(
                    first_name="Alice",
                    last_name="Jones",
                    full_name="Alice Jones",
                    username="alicejones",
                    email="alice@example.com",
                    password_hashed="hashed1",
                    phone="1234567890",
                    gender="female",
                    user_type="user",
                    user_role="guest",
                    profile="",
                    is_active=True,
                    email_verified=False,
                ),
                User(
                    first_name="Bob",
                    last_name="Miller",
                    full_name="Bob Miller",
                    username="bobmiller",
                    email="bob@example.com",
                    password_hashed="hashed2",
                    phone="0987654321",
                    gender="male",
                    user_type="user",
                    user_role="guest",
                    profile="",
                    is_active=True,
                    email_verified=False,
                ),
            ]
        )
        db.commit()

    finally:
        db.close()
