from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.features.auth.dependencies import get_current_user
from app.features.users.dto import (
    CreateUserDto,
    UserResponseDto,
)
from app.features.users.model import User
from app.features.users.service import UserService

router = APIRouter()


def get_user_service(
    db: AsyncSession = Depends(get_db),
) -> UserService:
    return UserService(db)


@router.post(
    "",
    response_model=UserResponseDto,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    data: CreateUserDto,
    service: UserService = Depends(get_user_service),
) -> UserResponseDto:
    return await service.create_user(data)

@router.get(
    "/me",
    response_model=UserResponseDto,
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponseDto:
    return current_user

@router.get(
    "/{user_id}",
    response_model=UserResponseDto,
)
async def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
) -> UserResponseDto:
    return await service.get_user(user_id)