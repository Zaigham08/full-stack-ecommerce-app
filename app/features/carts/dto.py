import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AddCartItemDto(BaseModel):
    product_id: uuid.UUID

    quantity: int = Field(
        ge=1,
        le=100,
    )


class UpdateCartItemDto(BaseModel):
    quantity: int = Field(
        ge=1,
        le=100,
    )


class CartItemResponseDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    quantity: int

    product_name: str
    unit_price: Decimal
    subtotal: Decimal

    image_url: str | None


class CartResponseDto(BaseModel):
    id: uuid.UUID
    items: list[CartItemResponseDto]

    subtotal: Decimal
    item_count: int