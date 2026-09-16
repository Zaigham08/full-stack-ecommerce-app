from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import OrderNotFoundError
from app.database.session import get_db
from app.features.auth.dependencies import get_current_user
from app.features.orders.dto import (
    CreateOrderDto,
    OrderResponseDto,
)
from app.features.orders.service import OrderService
from app.features.users.model import User


router = APIRouter()


def get_order_service(
    db: AsyncSession = Depends(get_db),
) -> OrderService:
    return OrderService(db)


@router.post(
    "",
    response_model=OrderResponseDto,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    data: CreateOrderDto,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> OrderResponseDto:
    return await service.create_order(
        current_user.id,
        data,
    )


@router.get(
    "",
    response_model=list[OrderResponseDto],
)
async def get_user_orders(
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> list[OrderResponseDto]:
    return await service.get_user_orders(
        current_user.id
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponseDto,
)
async def get_order(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> OrderResponseDto:
    return await service.get_order(
        current_user.id,
        order_id,
    )