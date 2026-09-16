import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.inventory.model import (
    InventoryReservation,
    InventoryReservationStatus,
)
from app.features.products.model import Product


class InventoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_product_for_update(
        self,
        product_id: uuid.UUID,
    ) -> Product | None:
        result = await self.db.execute(
            select(Product)
            .where(Product.id == product_id)
            .with_for_update()
        )

        return result.scalar_one_or_none()

    async def create_reservation(
        self,
        *,
        order_id: uuid.UUID,
        product_id: uuid.UUID,
        quantity: int,
    ) -> InventoryReservation:
        reservation = InventoryReservation(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            status=(
                InventoryReservationStatus.RESERVED
            ),
        )

        self.db.add(reservation)

        await self.db.flush()

        return reservation

    async def get_reservations_by_order(
        self,
        order_id: uuid.UUID,
    ) -> list[InventoryReservation]:
        result = await self.db.execute(
            select(InventoryReservation)
            .where(
                InventoryReservation.order_id
                == order_id
            )
        )

        return list(result.scalars().all())