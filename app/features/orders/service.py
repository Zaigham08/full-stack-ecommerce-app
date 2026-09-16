import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AddressNotFoundError,
    CartItemNotFoundError,
    InsufficientStockError,
    OrderNotFoundError,
    ProductUnavailableError,
)
from app.features.addresses.repository import AddressRepository
from app.features.carts.repository import CartRepository
from app.features.inventory.service import InventoryService
from app.features.orders.dto import CreateOrderDto
from app.features.orders.model import OrderStatus
from app.features.orders.repository import OrderRepository
from app.features.orders.state import validate_order_transition
from app.features.payments.model import PaymentStatus
from app.features.payments.service import PaymentService
from app.features.products.repository import ProductRepository


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

        self.order_repository = OrderRepository(db)
        self.cart_repository = CartRepository(db)
        self.product_repository = ProductRepository(db)
        self.address_repository = AddressRepository(db)
        self.inventory_service = InventoryService(db)
        self.payment_service = PaymentService(db)

    async def create_order(
        self,
        user_id: uuid.UUID,
        data: CreateOrderDto,
    ):
        cart = await self.cart_repository.get_by_user_id(
            user_id
        )

        if cart is None or not cart.items:
            raise CartItemNotFoundError()

        address = await self.address_repository.get_by_id(
            data.address_id
        )

        if address is None or address.user_id != user_id:
            raise AddressNotFoundError()

        try:
            order_items = []

            subtotal = Decimal("0")

            # First lock products and calculate authoritative
            # prices.
            locked_products = []

            for cart_item in sorted(
                cart.items,
                key=lambda item: str(item.product_id),
            ):
                product = (
                    await self.product_repository
                    .get_by_id_for_update(
                        cart_item.product_id
                    )
                )

                if product is None:
                    raise ProductUnavailableError()

                if not product.is_active:
                    raise ProductUnavailableError()

                if (
                    product.stock_quantity
                    < cart_item.quantity
                ):
                    raise InsufficientStockError()

                locked_products.append(
                    (cart_item, product)
                )

                item_subtotal = (
                    product.price
                    * cart_item.quantity
                )

                subtotal += item_subtotal

            total = subtotal + data.shipping_cost

            order = await self.order_repository.create(
                user_id=user_id,
                subtotal=subtotal,
                shipping_cost=data.shipping_cost,
                total=total,
                shipping_name=address.full_name,
                shipping_phone=address.phone,
                shipping_address=address.address_line,
                shipping_city=address.city,
                shipping_postal_code=address.postal_code,
            )

            for cart_item, product in locked_products:
                item_subtotal = (
                    product.price
                    * cart_item.quantity
                )

                await self.order_repository.create_item(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    unit_price=product.price,
                    quantity=cart_item.quantity,
                    subtotal=item_subtotal,
                )

                order_items.append(
                    (
                        product.id,
                        cart_item.quantity,
                    )
                )

            # Reserve inventory.
            locked_products_by_id = {
                product.id: product
                for _, product in locked_products
            }
            
            await self.inventory_service.reserve_for_order(
                order.id,
                order_items,
                locked_products_by_id,
            )

            await self.cart_repository.clear(cart.id)

            await self.db.commit()

            return await self.order_repository.get_by_id(
                order.id
            )

        except Exception:
            await self.db.rollback()
            raise

    async def get_user_orders(
        self,
        user_id: uuid.UUID,
    ):
        return await self.order_repository.get_by_user(
            user_id
        )

    async def get_order(
        self,
        user_id: uuid.UUID,
        order_id: uuid.UUID,
    ):
        order = await self.order_repository.get_by_id(
            order_id
        )

        if order is None or order.user_id != user_id:
            raise OrderNotFoundError()

        return order

    async def transition_order_status(
        self,
        order,
        new_status: OrderStatus,
    ):
        validate_order_transition(
            order.status,
            new_status,
        )

        return await self.order_repository.update_status(
            order,
            new_status,
        )

    async def get_all_orders(self):
        return await self.order_repository.get_all()


    async def admin_update_status(
        self,
        order_id: uuid.UUID,
        new_status: OrderStatus,
    ):
        order = await self.order_repository.get_by_id(
            order_id
        )

        if order is None:
            raise OrderNotFoundError()

        old_status = order.status

        try:
            validate_order_transition(
                old_status,
                new_status,
            )

            if new_status == OrderStatus.CANCELLED:

                if old_status == OrderStatus.PENDING:
                    await self.inventory_service.release_for_order(
                        order.id
                    )

                elif old_status in {
                    OrderStatus.CONFIRMED,
                    OrderStatus.PROCESSING,
                }:
                    await self.inventory_service.return_for_order(
                        order.id
                    )

                    payment = (
                        await self.payment_service.payment_repository
                        .get_by_order_id(order.id)
                    )

                    if payment is not None:
                        if payment.status == PaymentStatus.PAID:
                            await self.payment_service.mark_refund_pending(
                                order.id
                            )

            await self.order_repository.update_status(
                order,
                new_status,
            )

            await self.db.commit()

            return await self.order_repository.get_by_id(
                order.id
            )

        except Exception:
            await self.db.rollback()
            raise