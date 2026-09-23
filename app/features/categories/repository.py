import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.categories.model import Category


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        name: str,
        slug: str,
        description: str | None,
    ) -> Category:
        category = Category(
            name=name,
            slug=slug,
            description=description,
        )

        self.db.add(category)

        await self.db.flush()
        await self.db.refresh(category)

        return category

    async def get_by_id(
        self,
        category_id: uuid.UUID,
    ) -> Category | None:
        result = await self.db.execute(
            select(Category).where(
                Category.id == category_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_slug(
        self,
        slug: str,
    ) -> Category | None:
        result = await self.db.execute(
            select(Category).where(
                Category.slug == slug
            )
        )

        return result.scalar_one_or_none()

    async def get_by_name_or_slug(
        self,
        *,
        name: str,
        slug: str,
    ) -> Category | None:
        result = await self.db.execute(
            select(Category).where(
                or_(
                    Category.name == name,
                    Category.slug == slug,
                )
            )
        )

        return result.scalar_one_or_none()

    async def get_by_name_or_slug_excluding(
        self,
        *,
        name: str | None,
        slug: str | None,
        category_id: uuid.UUID,
    ) -> Category | None:
        conditions = []

        if name is not None:
            conditions.append(Category.name == name)

        if slug is not None:
            conditions.append(Category.slug == slug)

        if not conditions:
            return None

        result = await self.db.execute(
            select(Category).where(
                or_(*conditions),
                Category.id != category_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_all(self) -> list[Category]:
        result = await self.db.execute(
            select(Category).order_by(
                Category.created_at.desc()
            )
        )

        return list(result.scalars().all())

    async def update(
        self,
        category: Category,
        *,
        name: str | None = None,
        slug: str | None = None,
        description: str | None = None,
    ) -> Category:

        if name is not None:
            category.name = name

        if slug is not None:
            category.slug = slug

        if description is not None:
            category.description = description

        await self.db.flush()
        await self.db.refresh(category)

        return category