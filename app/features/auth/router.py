from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.features.auth.dto import (
    LoginDto,
    RefreshTokenDto,
    TokenResponseDto,
)
from app.features.auth.service import AuthService


router = APIRouter()


def get_auth_service(
    db: AsyncSession = Depends(get_db),
) -> AuthService:
    return AuthService(db)


@router.post(
    "/login",
    response_model=TokenResponseDto,
)
async def login(
    data: LoginDto,
    service: AuthService = Depends(
        get_auth_service
    ),
) -> TokenResponseDto:
    return await service.login(data)


@router.post(
    "/refresh",
    response_model=TokenResponseDto,
)
async def refresh(
    data: RefreshTokenDto,
    service: AuthService = Depends(
        get_auth_service
    ),
) -> TokenResponseDto:
    return await service.refresh(data)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    data: RefreshTokenDto,
    service: AuthService = Depends(
        get_auth_service
    ),
) -> None:
    await service.logout(data)