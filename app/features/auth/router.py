from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.features.auth.dto import (
    LoginDto,
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
    service: AuthService = Depends(get_auth_service),
) -> TokenResponseDto:
    access_token = await service.login(data)

    return TokenResponseDto(
        access_token=access_token,
    )