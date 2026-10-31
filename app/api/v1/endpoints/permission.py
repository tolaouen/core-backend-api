from fastapi import Depends, HTTPException, status
from app.models.users.user import User
from app.auth.deps import get_current_user
from app.constants.constant import RoleEnum

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.user_type not in (RoleEnum.ADMIN.value, RoleEnum.SUPER_ADMIN.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user

async def service_disabled():
    raise HTTPException(status_code=503, detail="This service is disabled")

