import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InsufficientStockError,
    InventoryStateError,
    ProductUnavailableError,
)
from app.features.inventory.model import (
    InventoryReservationStatus,
)
from app.features.inventory.repository import (
    InventoryRepository,
)


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = InventoryRepository(db)

    async def reserve_for_order(
        self,
        order_id: uuid.UUID,
        items: list[tuple[uuid.UUID, int]],
        locked_products: dict[uuid.UUID, object],
    ):
        for product_id, quantity in items:
            product = locked_products[product_id]

            if product.stock_quantity < quantity:
                raise InsufficientStockError()

            product.stock_quantity -= quantity

            await self.repository.create_reservation(
                order_id=order_id,
                product_id=product.id,
                quantity=quantity,
            )

        await self.db.flush()

    async def consume_for_order(
        self,
        order_id: uuid.UUID,
    ) -> None:
        reservations = (
            await self.repository
            .get_reservations_by_order(order_id)
        )

        for reservation in reservations:
            if (
                reservation.status
                == InventoryReservationStatus.CONSUMED
            ):
                continue

            if (
                reservation.status
                != InventoryReservationStatus.RESERVED
            ):
                raise InventoryStateError()

            reservation.status = (
                InventoryReservationStatus.CONSUMED
            )

        await self.db.flush()

    async def release_for_order(
        self,
        order_id: uuid.UUID,
    ) -> None:
        reservations = (
            await self.repository
            .get_reservations_by_order(order_id)
        )

        for reservation in reservations:
            if (
                reservation.status
                == InventoryReservationStatus.RELEASED
            ):
                continue

            if (
                reservation.status
                != InventoryReservationStatus.RESERVED
            ):
                raise InventoryStateError()

            product = (
                await self.repository
                .get_product_for_update(
                    reservation.product_id
                )
            )

            if product is None:
                raise ProductUnavailableError()

            product.stock_quantity += (
                reservation.quantity
            )

            reservation.status = (
                InventoryReservationStatus.RELEASED
            )

        await self.db.flush()


    async def return_for_order(
        self,
        order_id: uuid.UUID,
    ) -> None:
        reservations = (
            await self.repository
            .get_reservations_by_order(order_id)
        )

        for reservation in reservations:
            if (
                reservation.status
                == InventoryReservationStatus.RETURNED
            ):
                continue

            if (
                reservation.status
                != InventoryReservationStatus.CONSUMED
            ):
                raise InventoryStateError()

            product = (
                await self.repository
                .get_product_for_update(
                    reservation.product_id
                )
            )

            if product is None:
                raise ProductUnavailableError()

            product.stock_quantity += (
                reservation.quantity
            )

            reservation.status = (
                InventoryReservationStatus.RETURNED
            )

        await self.db.flush()