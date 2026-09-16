from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.features.categories.dto import (
    CategoryResponseDto,
    CreateCategoryDto,
    UpdateCategoryDto,
)
from app.features.categories.service import CategoryService


router = APIRouter()


def get_category_service(
    db: AsyncSession = Depends(get_db),
) -> CategoryService:
    return CategoryService(db)


@router.post(
    "",
    response_model=CategoryResponseDto,
)
async def create_category(
    data: CreateCategoryDto,
    service: CategoryService = Depends(
        get_category_service
    ),
) -> CategoryResponseDto:
    return await service.create_category(data)


@router.get(
    "/{category_id}",
    response_model=CategoryResponseDto,
)
async def get_category(
    category_id: UUID,
    service: CategoryService = Depends(
        get_category_service
    ),
) -> CategoryResponseDto:
    return await service.get_category(
        category_id
    )


@router.patch(
    "/{category_id}",
    response_model=CategoryResponseDto,
)
async def update_category(
    category_id: UUID,
    data: UpdateCategoryDto,
    service: CategoryService = Depends(
        get_category_service
    ),
) -> CategoryResponseDto:
    return await service.update_category(
        category_id,
        data,
    )