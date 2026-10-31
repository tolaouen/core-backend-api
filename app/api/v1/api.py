from fastapi import APIRouter, Depends
from app.api.v1.endpoints.auth import auth, roles, permission, app_user_permission
from app.api.v1.endpoints.users import user, user_app as app_apis, apps, user_app_access
from app.api.v1.endpoints.app_function import app_func, app_func_permission
from app.api.v1.endpoints.app_group import app_group, app_role_group
from app.api.v1.endpoints.permission import require_admin, service_disabled

api_route = APIRouter()

# Authorization route
api_route.include_router(auth.auth_router, prefix="/auth", tags=["Authorization"])
api_route.include_router(roles.app_role_router, prefix="/auth/roles", tags=["Roles"], dependencies=[Depends(require_admin)])
api_route.include_router(permission.permission_router, prefix="/auth/permissions", tags=["Permissions"], dependencies=[Depends(require_admin)])
api_route.include_router(app_user_permission.app_user_permission_router, prefix="/auth/user-permissions", tags=["User Permissions"], dependencies=[Depends(require_admin)])

# users
api_route.include_router(user.router, prefix="/auth/users", tags=["User"], dependencies=[Depends(require_admin)])

api_route.include_router(app_apis.app_user_router, prefix="/auth/user-apps", tags=["User Apps"], dependencies=[Depends(require_admin)])
api_route.include_router(apps.app_router, prefix="/auth/apps", tags=["Apps"], dependencies=[Depends(require_admin)])
api_route.include_router(user_app_access.access_router, prefix="/auth/access_app", tags=["User Access App"], dependencies=[Depends(service_disabled)])

# App function
api_route.include_router(app_func.app_func_router, prefix="/auth/app-functions", tags=["App Functions"], dependencies=[Depends(require_admin)])
api_route.include_router(app_func_permission.app_func_permission_router, prefix="/auth/function-permissions", tags=["App Function Permission"], dependencies=[Depends(require_admin)])

# App group
api_route.include_router(app_group.app_group_router, prefix="/auth/app-groups", tags=["App Groups"], dependencies=[Depends(service_disabled)])
api_route.include_router(app_role_group.app_role_group_router, prefix="/auth/app-role-groups", tags=["App Role Groups"], dependencies=[Depends(service_disabled)])
