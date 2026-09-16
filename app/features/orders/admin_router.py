from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.features.orders.dto import OrderResponseDto
from app.features.orders.model import OrderStatus
from app.features.orders.service import OrderService


router = APIRouter()


def get_order_service(
    db: AsyncSession = Depends(get_db),
) -> OrderService:
    return OrderService(db)


@router.get(
    "",
    response_model=list[OrderResponseDto],
)
async def get_all_orders(
    service: OrderService = Depends(
        get_order_service
    ),
) -> list[OrderResponseDto]:
    return await service.get_all_orders()


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponseDto,
)
async def update_order_status(
    order_id: UUID,
    status: OrderStatus,
    service: OrderService = Depends(
        get_order_service
    ),
) -> OrderResponseDto:
    return await service.admin_update_status(
        order_id,
        status,
    )