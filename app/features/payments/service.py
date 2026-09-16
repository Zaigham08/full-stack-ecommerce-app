import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InvalidPaymentStateError,
    OrderNotFoundError,
    PaymentAlreadyExistsError,
    PaymentNotFoundError,
)
from app.features.inventory.service import InventoryService
from app.features.orders.model import OrderStatus
from app.features.orders.repository import OrderRepository
from app.features.orders.state import (
    validate_order_transition,
)
from app.features.payments.dto import CreatePaymentDto
from app.features.payments.fake_provider import (
    FakePaymentProvider,
)
from app.features.payments.model import PaymentStatus
from app.features.payments.repository import (
    PaymentRepository,
)


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db

        self.payment_repository = PaymentRepository(db)
        self.order_repository = OrderRepository(db)
        self.inventory_service = InventoryService(db)

        self.provider = FakePaymentProvider()

    async def create_payment(
        self,
        user_id: uuid.UUID,
        data: CreatePaymentDto,
    ):
        existing_payment = (
            await self.payment_repository
            .get_by_idempotency_key(
                data.idempotency_key
            )
        )

        if existing_payment:
            return existing_payment

        order = await self.order_repository.get_by_id(
            data.order_id
        )

        if order is None or order.user_id != user_id:
            raise OrderNotFoundError()

        if order.status != OrderStatus.PENDING:
            raise InvalidPaymentStateError()

        existing_payment = (
            await self.payment_repository
            .get_by_order_id(order.id)
        )

        if existing_payment:
            raise PaymentAlreadyExistsError()

        try:
            payment = await self.payment_repository.create(
                order_id=order.id,
                method=data.method,
                amount=order.total,
                idempotency_key=data.idempotency_key,
            )

            payment.status = PaymentStatus.PROCESSING

            provider_result = (
                await self.provider.create_payment(
                    amount=order.total,
                    currency="PKR",
                    idempotency_key=data.idempotency_key,
                )
            )

            payment.provider = provider_result.provider
            payment.provider_payment_id = (
                provider_result.provider_payment_id
            )

            await self.db.commit()
            await self.db.refresh(payment)

            return payment

        except Exception:
            await self.db.rollback()
            raise

    async def mark_refund_pending(
        self,
        order_id: uuid.UUID,
    ):
        payment = await self.payment_repository.get_by_order_id(
            order_id
        )

        if payment is None:
            raise PaymentNotFoundError()

        if payment.status == PaymentStatus.REFUNDED:
            return payment

        if payment.status != PaymentStatus.PAID:
            raise InvalidPaymentStateError()

        payment.status = PaymentStatus.REFUND_PENDING

        await self.db.flush()

        return payment

    async def refund_payment(
        self,
        order_id: uuid.UUID,
    ):
        payment = await self.payment_repository.get_by_order_id(
            order_id
        )

        if payment is None:
            raise PaymentNotFoundError()

        if payment.status == PaymentStatus.REFUNDED:
            return payment

        if payment.status != PaymentStatus.REFUND_PENDING:
            raise InvalidPaymentStateError()

        if not payment.provider_payment_id:
            raise InvalidPaymentStateError()

        try:
            result = await self.provider.refund_payment(
                provider_payment_id=(
                    payment.provider_payment_id
                ),
                amount=payment.amount,
                idempotency_key=f"refund-{payment.id}",
            )

            if result.status != "refunded":
                raise InvalidPaymentStateError()

            payment.status = PaymentStatus.REFUNDED
            payment.provider_refund_id = (
                result.provider_refund_id
            )

            await self.db.commit()
            await self.db.refresh(payment)

            return payment

        except Exception:
            await self.db.rollback()
            raise

    async def process_webhook(
        self,
        provider_payment_id: str,
        status: str,
    ):
        payment = (
            await self.payment_repository
            .get_by_provider_payment_id(
                provider_payment_id
            )
        )

        if payment is None:
            raise PaymentNotFoundError()

        if payment.status in {
            PaymentStatus.PAID,
            PaymentStatus.FAILED,
            PaymentStatus.REFUND_PENDING,
            PaymentStatus.REFUNDED,
        }:
            return payment

        order = await self.order_repository.get_by_id(
            payment.order_id
        )

        if order is None:
            raise OrderNotFoundError()

        try:
            if status == "paid":
                validate_order_transition(
                    order.status,
                    OrderStatus.CONFIRMED,
                )

                await self.inventory_service.consume_for_order(
                    order.id
                )

                payment.status = PaymentStatus.PAID
                order.status = OrderStatus.CONFIRMED

            elif status == "failed":
                validate_order_transition(
                    order.status,
                    OrderStatus.CANCELLED,
                )

                await self.inventory_service.release_for_order(
                    order.id
                )

                payment.status = PaymentStatus.FAILED
                order.status = OrderStatus.CANCELLED

            else:
                raise InvalidPaymentStateError()

            await self.db.commit()
            await self.db.refresh(payment)

            return payment

        except Exception:
            await self.db.rollback()
            raise