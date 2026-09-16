from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.features.categories.dto import (
    CategoryResponseDto,
    CreateCategoryDto,
)
from app.features.categories.service import CategoryService

router = APIRouter()

def get_category_service(
    db: AsyncSession = Depends(get_db),
) -> CategoryService:
    return CategoryService(db)


@router.get(
    "",
    response_model=list[CategoryResponseDto],
)
async def get_all_categories(
    service: CategoryService = Depends(
        get_category_service
    ),
) -> list[CategoryResponseDto]:
    return await service.get_all_categories()


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
    return await service.get_category(category_id)

