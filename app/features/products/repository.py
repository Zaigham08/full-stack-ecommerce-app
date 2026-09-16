import uuid

from sqlalchemy import  func, or_, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.products.model import Product, ProductImage


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        category_id: uuid.UUID,
        name: str,
        slug: str,
        description: str | None,
        price,
        stock_quantity: int,
    ) -> Product:
        product = Product(
            category_id=category_id,
            name=name,
            slug=slug,
            description=description,
            price=price,
            stock_quantity=stock_quantity,
        )

        self.db.add(product)

        await self.db.flush()
        await self.db.refresh(product)

        return product


    async def get_active_by_id(
        self,
        product_id: uuid.UUID,
        ) -> Product | None:
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.images))
            .where(
                Product.id == product_id,
                Product.is_active.is_(True)
            )
        )

        return result.scalar_one_or_none()


    async def get_by_slug(
        self,
        slug: str,
    ) -> Product | None:
        result = await self.db.execute(
            select(Product).where(
                Product.slug == slug
            )
        )

        return result.scalar_one_or_none()


    async def create_image(
        self,
        *,
        product_id: uuid.UUID,
        image_url: str,
        alt_text: str | None,
        sort_order: int,
        is_primary: bool,
    ) -> ProductImage:
        image = ProductImage(
            product_id=product_id,
            image_url=image_url,
            alt_text=alt_text,
            sort_order=sort_order,
            is_primary=is_primary,
        )

        self.db.add(image)

        await self.db.flush()
        await self.db.refresh(image)

        return image


    async def list_products(
        self,
        *,
        page: int,
        limit: int,
        search: str | None = None,
        category_id: uuid.UUID | None = None,
        min_price=None,
        max_price=None,
        sort: str = "newest",
    ) -> tuple[list[Product], int]:
        query = (
            select(Product)
            .options(selectinload(Product.images))
            .where(Product.is_active.is_(True))
        )

        count_query = (
            select(func.count(Product.id))
            .where(Product.is_active.is_(True))
        )

        if search:
            search_pattern = f"%{search.strip()}%"

            search_filter = or_(
                Product.name.ilike(search_pattern),
                Product.description.ilike(search_pattern),
            )

            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        if category_id:
            category_filter = Product.category_id == category_id

            query = query.where(category_filter)
            count_query = count_query.where(category_filter)

        if min_price is not None:
            price_filter = Product.price >= min_price

            query = query.where(price_filter)
            count_query = count_query.where(price_filter)

        if max_price is not None:
            price_filter = Product.price <= max_price

            query = query.where(price_filter)
            count_query = count_query.where(price_filter)

        if sort == "newest":
            query = query.order_by(
                Product.created_at.desc()
            )

        elif sort == "oldest":
            query = query.order_by(
                Product.created_at.asc()
            )

        elif sort == "price_asc":
            query = query.order_by(
                Product.price.asc()
            )

        elif sort == "price_desc":
            query = query.order_by(
                Product.price.desc()
            )

        elif sort == "name_asc":
            query = query.order_by(
                Product.name.asc()
            )

        elif sort == "name_desc":
            query = query.order_by(
                Product.name.desc()
            )

        offset = (page - 1) * limit

        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)
        products = result.scalars().unique().all()

        count_result = await self.db.execute(count_query)
        total = count_result.scalar_one()

        return products, total


    async def update(
        self,
        product: Product,
        *,
        category_id: uuid.UUID | None = None,
        name: str | None = None,
        slug: str | None = None,
        description: str | None = None,
        price=None,
    ) -> Product:

        if category_id is not None:
            product.category_id = category_id

        if name is not None:
            product.name = name

        if slug is not None:
            product.slug = slug

        if description is not None:
            product.description = description

        if price is not None:
            product.price = price

        await self.db.flush()
        await self.db.refresh(product)

        return product


    async def update_stock(
        self,
        product: Product,
        quantity: int,
    ) -> Product:
        product.stock_quantity = quantity

        await self.db.flush()
        await self.db.refresh(product)

        return product


    async def get_image_by_id(
        self,
        image_id: uuid.UUID,
    ) -> ProductImage | None:
        result = await self.db.execute(
            select(ProductImage).where(
                ProductImage.id == image_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_id_for_update(
        self,
        product_id: uuid.UUID,
    ) -> Product | None:
        result = await self.db.execute(
            select(Product)
            .where(Product.id == product_id)
            .with_for_update()
        )

        return result.scalar_one_or_none()


    async def delete_image(
        self,
        image: ProductImage,
    ) -> None:
        await self.db.delete(image)
        await self.db.flush()