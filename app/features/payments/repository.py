import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.payments.model import Payment


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_order_id(
        self,
        order_id: uuid.UUID,
    ) -> Payment | None:
        result = await self.db.execute(
            select(Payment).where(
                Payment.order_id == order_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> Payment | None:
        result = await self.db.execute(
            select(Payment).where(
                Payment.idempotency_key
                == idempotency_key
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        order_id: uuid.UUID,
        method,
        amount,
        idempotency_key: str,
    ) -> Payment:
        payment = Payment(
            order_id=order_id,
            method=method,
            amount=amount,
            idempotency_key=idempotency_key,
        )

        self.db.add(payment)

        await self.db.flush()
        await self.db.refresh(payment)

        return payment

    async def get_by_provider_payment_id(
        self,
        provider_payment_id: str,
    ) -> Payment | None:
        result = await self.db.execute(
            select(Payment).where(
                Payment.provider_payment_id
                == provider_payment_id
            )
        )

        return result.scalar_one_or_none()