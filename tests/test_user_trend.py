from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.users.user import User
from app.schemas.users.user import UserTrendResponse
from app.services.app_user.users import UserService


def test_counter_user_trend_returns_monthly_counts_for_current_year():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    User.__table__.create(bind=engine)
    db = SessionLocal()
    year = datetime.now(ZoneInfo("Asia/Phnom_Penh")).year

    try:
        db.add_all(
            [
                User(
                    first_name="Alice",
                    last_name="One",
                    full_name="Alice One",
                    username="alice-one",
                    email="alice-one@example.com",
                    password_hashed="hashed",
                    phone="1234567890",
                    gender="female",
                    user_type="user",
                    user_role="guest",
                    profile="",
                    created_at=datetime(year, 1, 15),
                ),
                User(
                    first_name="Bob",
                    last_name="Two",
                    full_name="Bob Two",
                    username="bob-two",
                    email="bob-two@example.com",
                    password_hashed="hashed",
                    phone="1234567890",
                    gender="male",
                    user_type="user",
                    user_role="guest",
                    profile="",
                    created_at=datetime(year, 3, 15),
                ),
                User(
                    first_name="Carol",
                    last_name="Three",
                    full_name="Carol Three",
                    username="carol-three",
                    email="carol-three@example.com",
                    password_hashed="hashed",
                    phone="1234567890",
                    gender="female",
                    user_type="user",
                    user_role="guest",
                    profile="",
                    created_at=datetime(year, 3, 20),
                ),
            ]
        )
        db.commit()

        result = UserService(db).counter_user_trend()

        assert len(result) == 1
        trend = result[0]
        assert isinstance(trend, UserTrendResponse)
        assert trend.year == year
        assert len(trend.data) == 12
        assert [(trend.data[0].month, trend.data[0].count)] == [("Jan", 1)]
        assert [(trend.data[2].month, trend.data[2].count)] == [("Mar", 2)]
        assert all(item.count == 0 for item in trend.data[1:2] + trend.data[3:])
    finally:
        db.close()
