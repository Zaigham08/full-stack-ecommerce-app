from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.categories.model import Category
from app.features.orders.model import Order, OrderStatus
from app.features.products.model import Product
from app.features.users.model import User


class AdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def count_users(self) -> int:
        result = await self.db.execute(
            select(func.count(User.id))
        )

        return result.scalar_one()

    async def count_products(self) -> int:
        result = await self.db.execute(
            select(func.count(Product.id))
            .where(Product.is_active.is_(True))
        )

        return result.scalar_one()

    async def count_categories(self) -> int:
        result = await self.db.execute(
            select(func.count(Category.id))
        )

        return result.scalar_one()

    async def count_orders(self) -> int:
        result = await self.db.execute(
            select(func.count(Order.id))
        )

        return result.scalar_one()

    async def count_orders_by_status(
        self,
        status: OrderStatus,
    ) -> int:
        result = await self.db.execute(
            select(func.count(Order.id))
            .where(Order.status == status)
        )

        return result.scalar_one()

    async def calculate_revenue(self):
        result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(Order.total),
                    0,
                )
            )
            .where(
                Order.status.in_(
                    [
                        OrderStatus.CONFIRMED,
                        OrderStatus.PROCESSING,
                        OrderStatus.SHIPPED,
                        OrderStatus.DELIVERED,
                    ]
                )
            )
        )

        return result.scalar_one()

    async def count_low_stock_products(
        self,
        threshold: int = 10,
    ) -> int:
        result = await self.db.execute(
            select(func.count(Product.id))
            .where(
                Product.is_active.is_(True),
                Product.stock_quantity <= threshold,
            )
        )

        return result.scalar_one()