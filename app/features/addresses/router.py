import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.features.addresses.dto import (
    AddressResponseDto,
    CreateAddressDto,
)
from app.features.addresses.service import AddressService
from app.features.auth.dependencies import get_current_user
from app.features.users.model import User


router = APIRouter()


def get_address_service(
    db: AsyncSession = Depends(get_db),
) -> AddressService:
    return AddressService(db)


@router.post(
    "",
    response_model=AddressResponseDto,
    status_code=status.HTTP_201_CREATED,
)
async def create_address(
    data: CreateAddressDto,
    current_user: User = Depends(get_current_user),
    service: AddressService = Depends(
        get_address_service
    ),
) -> AddressResponseDto:
    return await service.create_address(
        current_user.id,
        data,
    )


@router.get(
    "",
    response_model=list[AddressResponseDto],
)
async def get_all_addresses(
    current_user: User = Depends(get_current_user),
    service: AddressService = Depends(
        get_address_service
    ),
) -> list[AddressResponseDto]:
    return await service.repository.get_by_user(
        current_user.id
    )