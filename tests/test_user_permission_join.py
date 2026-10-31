from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.databases.db import Base
from app.models.app_function.app_func import AppFunction
from app.models.app_permissions.app_user_permissions import AppUserPermission
from app.models.users.app_user import Apps
from app.models.users.user import User
from app.schemas.app_permission.app_user_permission import UserPermissionResponse
from app.services.app_permission.app_user_permisson import UserPermissionService


def test_user_permission_join_function_name():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = SessionLocal()

    try:
        user = User(
            first_name="John",
            last_name="Doe",
            full_name="John Doe",
            username="johndoe",
            email="john@example.com",
            password_hashed="secret",
            phone="123456",
            gender="male",
        )
        app = Apps(
            name="Core App",
            base_url="https://core.example.com",
            app_code="CORE",
            status="ACT",
        )
        db.add_all([user, app])
        db.commit()
        db.refresh(user)
        db.refresh(app)

        func = AppFunction(
            app_id=app.id,
            name="Dashboard Management",
            code="DASHBOARD_MGMT",
            type="MENU",
            app_code=app.app_code,
            status="ACT",
        )
        db.add(func)
        db.commit()
        db.refresh(func)

        perm = AppUserPermission(
            user_id=user.id,
            function_id=func.id,
            permissions=["READ", "UPDATE"],
        )
        db.add(perm)
        db.commit()
        db.refresh(perm)

        # 1. Model property test
        assert perm.function_name == "Dashboard Management"
        assert perm.app_code == "CORE"

        # 2. Service query test
        service = UserPermissionService(db)
        fetched_perm = service.get_user_permission_by_id(perm.id)
        assert fetched_perm is not None
        assert fetched_perm.function_name == "Dashboard Management"
        assert fetched_perm.app_code == "CORE"

        # 3. Pydantic serialization test
        response_data = UserPermissionResponse.model_validate(fetched_perm)
        assert response_data.function_name == "Dashboard Management"
        assert response_data.app_code == "CORE"
        assert response_data.user_id == user.id
        assert response_data.function_id == func.id

        # 4. get_permissions_by_user_id
        user_perms = service.get_permissions_by_user_id(user.id)
        assert len(user_perms) == 1
        assert user_perms[0].function_name == "Dashboard Management"
        assert user_perms[0].app_code == "CORE"

    finally:
        db.close()
