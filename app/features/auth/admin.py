from fastapi import Depends

from app.core.exceptions import ForbiddenError
from app.features.auth.dependencies import get_current_user
from app.features.users.model import User


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise ForbiddenError()

    return current_user