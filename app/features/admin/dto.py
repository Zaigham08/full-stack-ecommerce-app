from decimal import Decimal

from pydantic import BaseModel


class AdminDashboardResponseDto(BaseModel):
    total_users: int
    total_products: int
    total_categories: int
    total_orders: int

    pending_orders: int
    confirmed_orders: int
    delivered_orders: int
    cancelled_orders: int

    total_revenue: Decimal
    low_stock_products: int