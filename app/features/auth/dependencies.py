from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidTokenError
from app.core.security import decode_access_token
from app.database.session import get_db
from app.features.users.model import User
from app.features.users.repository import UserRepository


security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials

    subject = decode_access_token(token)

    try:
        user_id = UUID(subject)
    except ValueError as exc:
        raise InvalidTokenError() from exc

    repository = UserRepository(db)

    user = await repository.get_by_id(user_id)

    if user is None:
        raise InvalidTokenError()

    if not user.is_active:
        raise InvalidTokenError()

    return user