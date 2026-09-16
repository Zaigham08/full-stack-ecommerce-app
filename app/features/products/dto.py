from typing import Literal
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from app.features.categories.dto import CategorySummaryDto


class CreateProductDto(BaseModel):
    category_id: uuid.UUID

    name: str = Field(
        min_length=2,
        max_length=200,
    )

    slug: str = Field(
        min_length=2,
        max_length=220,
    )

    description: str | None = None

    price: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
    )

    stock_quantity: int = Field(
        ge=0,
    )


class ProductImageResponseDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    image_url: str
    alt_text: str | None
    sort_order: int
    is_primary: bool
    created_at: datetime


class ProductResponseDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID
    category: CategorySummaryDto
    name: str
    slug: str
    description: str | None
    price: Decimal
    stock_quantity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    images: list[ProductImageResponseDto] = []

    model_config = ConfigDict(from_attributes=True)


class ProductListQueryDto(BaseModel):
    page: int = Field(
        default=1,
        ge=1,
    )

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )

    search: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    category_id: uuid.UUID | None = None

    min_price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    max_price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    sort: Literal[
        "newest",
        "oldest",
        "price_asc",
        "price_desc",
        "name_asc",
        "name_desc",
    ] = "newest"


class ProductListResponseDto(BaseModel):
    items: list[ProductResponseDto]

    page: int
    limit: int
    total: int
    pages: int


class UpdateProductDto(BaseModel):
    category_id: uuid.UUID | None = None

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=220,
    )

    description: str | None = None

    price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=10,
        decimal_places=2,
    )


class UpdateStockDto(BaseModel):
    quantity: int = Field(
        ge=0,
        le=1_000_000,
    )