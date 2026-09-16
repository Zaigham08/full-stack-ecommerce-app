import uuid
from decimal import Decimal

from app.features.payments.provider import (
    PaymentCreationResult,
    PaymentRefundResult,
)


class FakePaymentProvider:
    async def create_payment(
        self,
        *,
        amount: Decimal,
        currency: str,
        idempotency_key: str,
    ) -> PaymentCreationResult:
        return PaymentCreationResult(
            provider="fake",
            provider_payment_id=str(uuid.uuid4()),
            status="pending",
            checkout_url="https://example.com/pay",
        )

    async def verify_payment(
        self,
        provider_payment_id: str,
    ) -> str:
        return "paid"

    async def refund_payment(
        self,
        *,
        provider_payment_id: str,
        amount: Decimal,
        idempotency_key: str,
    ) -> PaymentRefundResult:
        return PaymentRefundResult(
            provider="fake",
            provider_refund_id=str(uuid.uuid4()),
            status="refunded",
        )