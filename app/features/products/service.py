import math
import uuid

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    CategoryNotFoundError,
    ProductAlreadyExistsError,
    ProductImageNotFoundError,
    ProductNotFoundError,
)
from app.features.categories.repository import CategoryRepository

from app.features.products.dto import ( 
    CreateProductDto, 
    ProductListQueryDto,
    UpdateProductDto,
    UpdateStockDto,
)
from app.features.products.repository import ProductRepository

from app.core.storage import (
    save_product_image,
    delete_product_image_file,
)


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.product_repository = ProductRepository(db)
        self.category_repository = CategoryRepository(db)

    async def create_product(
        self,
        data: CreateProductDto,
    ):
        existing_product = await self.product_repository.get_by_slug(
            data.slug
        )

        if existing_product:
            raise ProductAlreadyExistsError()

        category = await self.category_repository.get_by_id(
            data.category_id
        )

        if category is None:
            raise CategoryNotFoundError()

        try:
            product = await self.product_repository.create(
                category_id=data.category_id,
                name=data.name,
                slug=data.slug,
                description=data.description,
                price=data.price,
                stock_quantity=data.stock_quantity,
            )

            await self.db.commit()

            return product

        except Exception:
            await self.db.rollback()
            raise

    async def get_product(
        self,
        product_id: uuid.UUID,
    ):
        product = await self.product_repository.get_active_by_id(
            product_id
        )

        if product is None:
            raise ProductNotFoundError()

        return product

    async def add_product_image(
        self,
        product_id: uuid.UUID,
        file: UploadFile,
        *,
        alt_text: str | None = None,
        sort_order: int = 0,
        is_primary: bool = False,
    ):
        product = await self.product_repository.get_active_by_id(
            product_id
        )

        if product is None:
            raise ProductNotFoundError()

        image_url = await save_product_image(file)

        try:
            image = await self.product_repository.create_image(
                product_id=product_id,
                image_url=image_url,
                alt_text=alt_text,
                sort_order=sort_order,
                is_primary=is_primary,
            )

            await self.db.commit()

            return image

        except Exception:
            await self.db.rollback()
            raise

    async def list_products(
        self,
        params: ProductListQueryDto,
    ):
        products, total = await self.product_repository.list_products(
            page=params.page,
            limit=params.limit,
            search=params.search,
            category_id=params.category_id,
            min_price=params.min_price,
            max_price=params.max_price,
            sort=params.sort,
        )

        pages = math.ceil(total / params.limit)

        return products, total, pages


    async def update_product(
        self,
        product_id: uuid.UUID,
        data: UpdateProductDto,
    ):
        product = await self.product_repository.get_active_by_id(
            product_id
        )

        if product is None:
            raise ProductNotFoundError()

        if data.slug is not None:
            existing_product = await self.product_repository.get_by_slug(
                data.slug
            )

            if (
                existing_product is not None
                and existing_product.id != product.id
            ):
                raise ProductAlreadyExistsError()

        if data.category_id is not None:
            category = await self.category_repository.get_by_id(
                data.category_id
            )

            if category is None:
                raise CategoryNotFoundError()

        try:
            product = await self.product_repository.update(
                product,
                category_id=data.category_id,
                name=data.name,
                slug=data.slug,
                description=data.description,
                price=data.price,
            )

            await self.db.commit()

            return product

        except Exception:
            await self.db.rollback()
            raise


    async def update_stock(
        self,
        product_id: uuid.UUID,
        data: UpdateStockDto,
    ):
        product = await self.product_repository.get_active_by_id(
            product_id
        )

        if product is None:
            raise ProductNotFoundError()

        try:
            product = await self.product_repository.update_stock(
                product,
                data.quantity,
            )

            await self.db.commit()

            return product

        except Exception:
            await self.db.rollback()
            raise


    async def deactivate_product(
        self,
        product_id: uuid.UUID,
    ):
        product = await self.product_repository.get_active_by_id(
            product_id
        )

        if product is None:
            raise ProductNotFoundError()

        try:
            product.is_active = False

            await self.db.commit()
            await self.db.refresh(product)

            return product

        except Exception:
            await self.db.rollback()
            raise


    async def delete_product_image(
        self,
        image_id: uuid.UUID,
    ):
        image = await self.product_repository.get_image_by_id(
            image_id
        )

        if image is None:   
            raise ProductImageNotFoundError()

        try:
            delete_product_image_file(image.image_url)
            
            await self.product_repository.delete_image(image)
            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise