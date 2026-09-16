from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidCredentialsError
from app.core.security import (
    create_access_token,
    verify_password,
)
from app.features.auth.dto import LoginDto
from app.features.users.repository import UserRepository

class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repository = UserRepository(db)

    async def login(
        self,
        data: LoginDto,
    ) -> str:
        user = await self.user_repository.get_by_email(
            data.email
        )

        if user is None:
            raise InvalidCredentialsError()

        password_is_valid = verify_password(
            data.password,
            user.password_hash,
        )

        if not password_is_valid:
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InvalidCredentialsError()

        return create_access_token(
            subject=str(user.id)
        )