from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass
class PaymentCreationResult:
    provider: str
    provider_payment_id: str
    status: str
    checkout_url: str | None = None


@dataclass
class PaymentRefundResult:
    provider: str
    provider_refund_id: str
    status: str


class PaymentProvider(Protocol):
    async def create_payment(
        self,
        *,
        amount: Decimal,
        currency: str,
        idempotency_key: str,
    ) -> PaymentCreationResult:
        ...

    async def verify_payment(
        self,
        provider_payment_id: str,
    ) -> str:
        ...

    async def refund_payment(
        self,
        *,
        provider_payment_id: str,
        amount: Decimal,
        idempotency_key: str,
    ) -> PaymentRefundResult:
        ...