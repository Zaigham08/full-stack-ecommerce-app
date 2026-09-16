from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.features.auth.dependencies import get_current_user
from app.features.payments.dto import (
    CreatePaymentDto,
    PaymentResponseDto,
    PaymentWebhookDto,
)
from app.features.payments.service import PaymentService
from app.features.users.model import User


router = APIRouter()


def get_payment_service(
    db: AsyncSession = Depends(get_db),
) -> PaymentService:
    return PaymentService(db)


@router.post(
    "",
    response_model=PaymentResponseDto,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment(
    data: CreatePaymentDto,
    current_user: User = Depends(
        get_current_user
    ),
    service: PaymentService = Depends(
        get_payment_service
    ),
) -> PaymentResponseDto:
    return await service.create_payment(
        current_user.id,
        data,
    )

@router.post(
    "/webhook",
    response_model=PaymentResponseDto,
)
async def payment_webhook(
    data: PaymentWebhookDto,
    service: PaymentService = Depends(
        get_payment_service
    ),
) -> PaymentResponseDto:
    return await service.process_webhook(
        data.provider_payment_id,
        data.status,
    )