from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.features.auth.admin import get_current_admin
from app.features.products.dto import (
    CreateProductDto,
    ProductImageResponseDto,
    ProductResponseDto,
    UpdateProductDto,
    UpdateStockDto,
)
from app.features.products.service import ProductService
from app.features.users.model import User


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