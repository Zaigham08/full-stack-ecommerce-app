from datetime import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.features.payments.model import (
    PaymentMethod,
    PaymentStatus,
)


class CreatePaymentDto(BaseModel):
    order_id: uuid.UUID

    method: PaymentMethod

    idempotency_key: str = Field(
        min_length=10,
        max_length=255,
    )


class PaymentResponseDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_id: uuid.UUID
    method: PaymentMethod
    status: PaymentStatus
    amount: Decimal
    provider: str | None
    provider_payment_id: str | None
    provider_refund_id: str | None
    created_at: datetime
    updated_at: datetime

class PaymentWebhookDto(BaseModel):
    provider_payment_id: str
    status: str