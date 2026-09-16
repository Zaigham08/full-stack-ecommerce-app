import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.features.orders.model import Order, OrderStatus


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        subtotal,
        shipping_cost: Decimal,
        total,
        shipping_name: str,
        shipping_phone: str,
        shipping_address: str,
        shipping_city: str,
        shipping_postal_code: str | None,
    ) -> Order:
        order = Order(
            user_id=user_id,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            total=total,
            shipping_name=shipping_name,
            shipping_phone=shipping_phone,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_postal_code=shipping_postal_code,
        )

        self.db.add(order)

        await self.db.flush()

        return order

    async def create_item(
        self,
        *,
        order_id: uuid.UUID,
        product_id: uuid.UUID,
        product_name: str,
        unit_price,
        quantity: int,
        subtotal,
    ):
        from app.features.orders.model import OrderItem

        item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            product_name=product_name,
            unit_price=unit_price,
            quantity=quantity,
            subtotal=subtotal,
        )

        self.db.add(item)

        await self.db.flush()

        return item

    async def get_by_id(
        self,
        order_id: uuid.UUID,
    ) -> Order | None:
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items)
            )
            .where(Order.id == order_id)
        )

        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: uuid.UUID,
    ) -> list[Order]:
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items)
            )
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )

        return list(result.scalars().unique().all())

    async def update_status(
        self,
        order: Order,
        status: OrderStatus,
    ) -> Order:
        order.status = status

        await self.db.flush()
        await self.db.refresh(order)

        return order


    async def get_all(
        self,
    ) -> list[Order]:
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items)
            )
            .order_by(Order.created_at.desc())
        )

        return list(result.scalars().unique().all())