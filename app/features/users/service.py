import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import UserAlreadyExistsError, UserNotFoundError

from app.core.security import hash_password
from app.features.users.dto import CreateUserDto
from app.features.users.repository import UserRepository


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)

    async def create_user(
    self,
    data: CreateUserDto,
    ):
        existing_user = await self.user_repository.get_by_email(
            data.email
        )

        if existing_user:
            raise UserAlreadyExistsError()

        try:
            password_hash = hash_password(data.password)

            user = await self.user_repository.create(
                email=data.email,
                password_hash=password_hash,
            )

            await self.db.commit()

            return user

        except Exception:
            await self.db.rollback()
            raise

    async def get_user(
        self,
        user_id: uuid.UUID,
    ):
        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError()

        return user