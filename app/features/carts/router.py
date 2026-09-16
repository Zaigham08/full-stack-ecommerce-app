from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.features.auth.dependencies import get_current_user
from app.features.carts.dto import (
    AddCartItemDto,
    CartResponseDto,
    UpdateCartItemDto,
)
from app.features.carts.service import CartService
from app.features.users.model import User


router = APIRouter()

def get_cart_service(
    db: AsyncSession = Depends(get_db),
) -> CartService:
    return CartService(db)


@router.get(
    "",
    response_model=CartResponseDto,
)
async def get_cart(
    current_user: User = Depends(get_current_user),
    service: CartService = Depends(
        get_cart_service
    ),
) -> CartResponseDto:
    cart = await service.get_or_create_cart(
        current_user.id
    )

    return service.build_cart_response(cart)


@router.post(
    "/items",
    response_model=CartResponseDto,
    status_code=status.HTTP_201_CREATED,
)
async def add_cart_item(
    data: AddCartItemDto,
    current_user: User = Depends(get_current_user),
    service: CartService = Depends(
        get_cart_service
    ),
) -> CartResponseDto:
    cart = await service.add_item(
        current_user.id,
        data,
    )

    return service.build_cart_response(cart)


@router.patch(
    "/items/{item_id}",
    response_model=CartResponseDto,
)
async def update_cart_item(
    item_id: UUID,
    data: UpdateCartItemDto,
    current_user: User = Depends(get_current_user),
    service: CartService = Depends(
        get_cart_service
    ),
) -> CartResponseDto:
    cart = await service.update_item(
        current_user.id,
        item_id,
        data,
    )

    return service.build_cart_response(cart)


@router.delete(
    "/items/{item_id}",
    response_model=CartResponseDto,
)
async def remove_cart_item(
    item_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CartService = Depends(
        get_cart_service
    ),
) -> CartResponseDto:
    cart = await service.remove_item(
        current_user.id,
        item_id,
    )

    return service.build_cart_response(cart)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def clear_cart(
    current_user: User = Depends(get_current_user),
    service: CartService = Depends(
        get_cart_service
    ),
) -> None:
    await service.clear_cart(
        current_user.id
    )