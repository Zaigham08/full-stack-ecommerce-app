import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    CartEmptyError,
    CartItemNotFoundError,
    CartNotFoundError,
    InsufficientStockError,
    ProductNotFoundError,
    ProductUnavailableError,
)
from app.features.carts.dto import (
    AddCartItemDto,
    UpdateCartItemDto,
)
from app.features.carts.model import Cart
from app.features.carts.repository import CartRepository
from app.features.products.repository import ProductRepository


class CartService:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.cart_repository = CartRepository(db)
        self.product_repository = ProductRepository(db)

    async def get_or_create_cart(
        self,
        user_id: uuid.UUID,
    ) -> Cart:
        """
        Get the user's cart.

        If the user does not have a cart yet, create one.

        This method intentionally does not commit.
        The calling service operation owns the transaction.
        """
        cart = await self.cart_repository.get_by_user_id(
            user_id
        )

        if cart is not None:
            return cart

        return await self.cart_repository.create(
            user_id
        )

    async def add_item(
        self,
        user_id: uuid.UUID,
        data: AddCartItemDto,
    ) -> Cart:
        """
        Add a product to the user's cart.

        If the product already exists in the cart,
        increase its quantity instead of creating
        another cart item.
        """
        product = await self.product_repository.get_active_by_id(
            data.product_id
        )

        if product is None:
            raise ProductNotFoundError()

        if not product.is_active:
            raise ProductUnavailableError()

        if product.stock_quantity < data.quantity:
            raise InsufficientStockError()

        try:
            cart = await self.get_or_create_cart(
                user_id
            )

            existing_item = await self.cart_repository.get_item(
                cart.id,
                data.product_id,
            )

            if existing_item is not None:
                new_quantity = (
                    existing_item.quantity
                    + data.quantity
                )

                if new_quantity > product.stock_quantity:
                    raise InsufficientStockError()

                existing_item.quantity = new_quantity

                await self.db.flush()

            else:
                await self.cart_repository.create_item(
                    cart_id=cart.id,
                    product_id=data.product_id,
                    quantity=data.quantity,
                )

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        updated_cart = await self.cart_repository.get_by_user_id(
            user_id
        )

        if updated_cart is None:
            raise CartNotFoundError()

        return updated_cart

    async def update_item(
        self,
        user_id: uuid.UUID,
        item_id: uuid.UUID,
        data: UpdateCartItemDto,
    ) -> Cart:
        """
        Replace the quantity of an existing cart item.
        """
        cart = await self.cart_repository.get_by_user_id(
            user_id
        )

        if cart is None:
            raise CartNotFoundError()

        item = await self.cart_repository.get_item_by_id_and_user(
            item_id,
            user_id,
        )

        if item is None or item.cart_id != cart.id:
            raise CartItemNotFoundError()

        product = await self.product_repository.get_active_by_id(
            item.product_id
        )

        if product is None:
            raise ProductNotFoundError()

        if not product.is_active:
            raise ProductUnavailableError()

        if data.quantity > product.stock_quantity:
            raise InsufficientStockError()

        try:
            item.quantity = data.quantity

            await self.db.flush()
            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        updated_cart = await self.cart_repository.get_by_user_id(
            user_id
        )

        if updated_cart is None:
            raise CartNotFoundError()

        return updated_cart

    async def remove_item(
        self,
        user_id: uuid.UUID,
        item_id: uuid.UUID,
    ) -> Cart:
        """
        Remove a single item from the user's cart.
        """
        cart = await self.cart_repository.get_by_user_id(
            user_id
        )

        if cart is None:
            raise CartNotFoundError()

        item = await self.cart_repository.get_item_by_id_and_user(
            item_id,
            user_id,
        )

        if item is None or item.cart_id != cart.id:
            raise CartItemNotFoundError()

        try:
            await self.cart_repository.delete_item(item)

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        updated_cart = await self.cart_repository.get_by_user_id(
            user_id
        )

        if updated_cart is None:
            raise CartNotFoundError()

        return updated_cart

    async def clear_cart(
        self,
        user_id: uuid.UUID,
    ) -> None:
        """
        Remove all items from the user's cart.

        If the user has no cart, the operation is treated
        as idempotent and simply returns.
        """
        cart = await self.cart_repository.get_by_user_id(
            user_id
        )

        if cart is None:
            return

        try:
            await self.cart_repository.clear(
                cart.id
            )

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

    def build_cart_response(
        self,
        cart: Cart,
    ) -> dict:
        """
        Build the API response from the current cart state.

        Prices are always taken from the current Product
        record. The client never supplies or controls price.
        """
        items = []

        subtotal = Decimal("0.00")
        item_count = 0

        for item in cart.items:
            product = item.product

            primary_image = next(
                (
                    image
                    for image in product.images
                    if image.is_primary
                ),
                None,
            )

            item_subtotal = (
                product.price * item.quantity
            )

            items.append(
                {
                    "id": item.id,
                    "product_id": product.id,
                    "quantity": item.quantity,
                    "product_name": product.name,
                    "unit_price": product.price,
                    "subtotal": item_subtotal,
                    "image_url": (
                        primary_image.image_url
                        if primary_image is not None
                        else None
                    ),
                }
            )

            subtotal += item_subtotal
            item_count += item.quantity

        return {
            "id": cart.id,
            "items": items,
            "subtotal": subtotal,
            "item_count": item_count,
        }