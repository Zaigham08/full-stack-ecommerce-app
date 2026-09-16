import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.features.carts.model import Cart, CartItem
from app.features.products.model import Product


class CartRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(
        self,
        user_id: uuid.UUID,
    ) -> Cart | None:
        result = await self.db.execute(
            select(Cart)
            .options(
                selectinload(Cart.items)
                .selectinload(CartItem.product)
                .selectinload(Product.images)
            )
            .execution_options(
                populate_existing=True
            )
            .where(
                Cart.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: uuid.UUID,
    ) -> Cart:
        cart = Cart(
            user_id=user_id,
        )

        self.db.add(cart)

        await self.db.flush()
        await self.db.refresh(cart)

        return cart

    async def get_item(
        self,
        cart_id: uuid.UUID,
        product_id: uuid.UUID,
    ) -> CartItem | None:
        result = await self.db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart_id,
                CartItem.product_id == product_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_item_by_id(
        self,
        item_id: uuid.UUID,
    ) -> CartItem | None:
        result = await self.db.execute(
            select(CartItem).where(
                CartItem.id == item_id
            )
        )

        return result.scalar_one_or_none()

    async def get_item_by_id_and_user(
        self,
        item_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> CartItem | None:
        result = await self.db.execute(
            select(CartItem)
            .join(
                Cart,
                Cart.id == CartItem.cart_id,
            )
            .where(
                CartItem.id == item_id,
                Cart.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def create_item(
        self,
        *,
        cart_id: uuid.UUID,
        product_id: uuid.UUID,
        quantity: int,
    ) -> CartItem:
        item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
        )

        self.db.add(item)

        await self.db.flush()
        await self.db.refresh(item)

        return item

    async def delete_item(
        self,
        item: CartItem,
    ) -> None:
        await self.db.delete(item)
        await self.db.flush()

    async def clear(
        self,
        cart_id: uuid.UUID,
    ) -> None:
        await self.db.execute(
            delete(CartItem).where(
                CartItem.cart_id == cart_id
            )
        )

        await self.db.flush()

    async def get_by_user_id_for_update(
        self,
        user_id: uuid.UUID,
    ) -> Cart | None:
        result = await self.db.execute(
            select(Cart)
            .where(Cart.user_id == user_id)
            .with_for_update()
        )

        return result.scalar_one_or_none()