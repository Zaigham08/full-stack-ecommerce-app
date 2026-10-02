from decimal import Decimal
from typing import Literal
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.features.products.dto import (
    CreateProductDto,
    ProductImageResponseDto,
    ProductListQueryDto,
    ProductListResponseDto,
    ProductListResponseDto,
    ProductResponseDto,
    UpdateProductDto,
    UpdateStockDto,
)
from app.features.products.service import ProductService

router = APIRouter()


def get_product_service(
    db: AsyncSession = Depends(get_db),
) -> ProductService:
    return ProductService(db)


@router.post(
    "",
    response_model=ProductResponseDto,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    data: CreateProductDto,
    service: ProductService = Depends(
        get_product_service,
    ),
) -> ProductResponseDto:
    return await service.create_product(data)

@router.get(
    "",
    response_model=ProductListResponseDto,
)
async def list_products_admin(
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
        await service.list_products_admin(params)
    )

    return ProductListResponseDto(
        items=products,
        page=params.page,
        limit=params.limit,
        total=total,
        pages=pages,
    )

@router.patch(
    "/{product_id}",
    response_model=ProductResponseDto,
)
async def update_product(
    product_id: UUID,
    data: UpdateProductDto,
    service: ProductService = Depends(
        get_product_service,
    ),
) -> ProductResponseDto:
    return await service.update_product(
        product_id,
        data,
    )


@router.patch(
    "/{product_id}/stock",
    response_model=ProductResponseDto,
)
async def update_stock(
    product_id: UUID,
    data: UpdateStockDto,
    service: ProductService = Depends(
        get_product_service,
    ),
) -> ProductResponseDto:
    return await service.update_stock(
        product_id,
        data,
    )


@router.delete(
    "/{product_id}",
    response_model=ProductResponseDto,
)
async def deactivate_product(
    product_id: UUID,
    service: ProductService = Depends(
        get_product_service,
    ),
) -> ProductResponseDto:
    return await service.deactivate_product(
        product_id,
    )

@router.patch(
    "/{product_id}/activate",
    response_model=ProductResponseDto,
)
async def activate_product(
    product_id: UUID,
    service: ProductService = Depends(
        get_product_service,
    ),
) -> ProductResponseDto:
    return await service.activate_product(
        product_id
    )

@router.post(
    "/{product_id}/images",
    response_model=ProductImageResponseDto,
    status_code=status.HTTP_201_CREATED,
)
async def add_product_image(
    product_id: UUID,
    file: UploadFile = File(...),
    alt_text: str | None = Form(None),
    sort_order: int = Form(0),
    is_primary: bool = Form(False),
    service: ProductService = Depends(
        get_product_service,
    ),
) -> ProductImageResponseDto:
    return await service.add_product_image(
        product_id=product_id,
        file=file,
        alt_text=alt_text,
        sort_order=sort_order,
        is_primary=is_primary,
    )


@router.delete(
    "/{product_id}/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product_image(
    product_id: UUID,
    image_id: UUID,
    service: ProductService = Depends(
        get_product_service,
    ),
) -> None:
    await service.delete_product_image(
        product_id,
        image_id,
    )