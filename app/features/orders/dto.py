import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.features.orders.model import OrderStatus


class CreateOrderDto(BaseModel):
    address_id: uuid.UUID

    shipping_cost: Decimal = Field(
        default=Decimal(0),
        ge=0,
        max_digits=12,
        decimal_places=2,
    )


class OrderItemResponseDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal


class OrderResponseDto(BaseModel):
    id: uuid.UUID
    status: OrderStatus

    subtotal: Decimal
    shipping_cost: Decimal
    total: Decimal

    shipping_name: str
    shipping_phone: str
    shipping_address: str
    shipping_city: str
    shipping_postal_code: str | None

    items: list[OrderItemResponseDto]

    created_at: datetime
    updated_at: datetime