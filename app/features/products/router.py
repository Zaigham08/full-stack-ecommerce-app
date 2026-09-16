from decimal import Decimal
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.features.products.dto import (
    ProductListQueryDto,
    ProductListResponseDto,
    ProductResponseDto,
)
from app.features.products.service import ProductService


router = APIRouter()


def get_product_service(
    db: AsyncSession = Depends(get_db),
) -> ProductService:
    return ProductService(db)


@router.get(
    "",
    response_model=ProductListResponseDto,
)
async def list_products(
    page: int = Query(
        default=1,
        ge=1,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),
    category_id: UUID | None = None,
    min_price: Decimal | None = Query(
        default=None,
        ge=0,
    ),
    max_price: Decimal | None = Query(
        default=None,
        ge=0,
    ),
    sort: Literal[
        "newest",
        "oldest",
        "price_asc",
        "price_desc",
        "name_asc",
        "name_desc",
    ] = "newest",
    service: ProductService = Depends(
        get_product_service,
    ),
) -> ProductListResponseDto:

    params = ProductListQueryDto(
        page=page,
        limit=limit,
        search=search,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
    )

    products, total, pages = (
        await service.list_products(params)
    )

    return ProductListResponseDto(
        items=products,
        page=params.page,
        limit=params.limit,
        total=total,
        pages=pages,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponseDto,
)
async def get_product(
    product_id: UUID,
    service: ProductService = Depends(
        get_product_service,
    ),
) -> ProductResponseDto:
    return await service.get_product(product_id)