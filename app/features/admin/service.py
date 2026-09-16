from app.features.admin.repository import AdminRepository
from app.features.orders.model import OrderStatus


class AdminService:
    def __init__(self, db):
        self.repository = AdminRepository(db)

    async def get_dashboard(self):
        return {
            "total_users": (
                await self.repository.count_users()
            ),
            "total_products": (
                await self.repository.count_products()
            ),
            "total_categories": (
                await self.repository.count_categories()
            ),
            "total_orders": (
                await self.repository.count_orders()
            ),
            "pending_orders": (
                await self.repository.count_orders_by_status(
                    OrderStatus.PENDING
                )
            ),
            "confirmed_orders": (
                await self.repository.count_orders_by_status(
                    OrderStatus.CONFIRMED
                )
            ),
            "delivered_orders": (
                await self.repository.count_orders_by_status(
                    OrderStatus.DELIVERED
                )
            ),
            "cancelled_orders": (
                await self.repository.count_orders_by_status(
                    OrderStatus.CANCELLED
                )
            ),
            "total_revenue": (
                await self.repository.calculate_revenue()
            ),
            "low_stock_products": (
                await self.repository.count_low_stock_products()
            ),
        }