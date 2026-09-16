import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
)
from app.features.categories.dto import CreateCategoryDto, UpdateCategoryDto
from app.features.categories.repository import CategoryRepository


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = CategoryRepository(db)

    async def create_category(
        self,
        data: CreateCategoryDto,
    ):
        existing_category = await self.repository.get_by_slug(
            data.slug
        )

        if existing_category:
            raise CategoryAlreadyExistsError()

        try:
            category = await self.repository.create(
                name=data.name,
                slug=data.slug,
                description=data.description,
            )

            await self.db.commit()

            return category

        except Exception:
            await self.db.rollback()
            raise


    async def get_category(
        self,
        category_id: uuid.UUID,
    ):
        category = await self.repository.get_by_id(
            category_id
        )

        if category is None:
            raise CategoryNotFoundError()

        return category

    async def get_all_categories(self):
        return await self.repository.get_all()


    async def update_category(
        self,
        category_id: uuid.UUID,
        data: UpdateCategoryDto,
    ):
        category = await self.repository.get_by_id(
            category_id
        )

        if category is None:
            raise CategoryNotFoundError()

        try:
            category = await self.repository.update(
                category,
                name=data.name,
                slug=data.slug,
                description=data.description,
            )

            await self.db.commit()

            return category

        except Exception:
            await self.db.rollback()
            raise