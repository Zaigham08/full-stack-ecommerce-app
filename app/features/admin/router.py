from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.features.admin.dto import (
    AdminDashboardResponseDto,
)
from app.features.admin.service import AdminService


router = APIRouter()


def get_admin_service(
    db: AsyncSession = Depends(get_db),
) -> AdminService:
    return AdminService(db)


@router.get(
    "/dashboard",
    response_model=AdminDashboardResponseDto,
)
async def get_dashboard(
    service: AdminService = Depends(
        get_admin_service
    ),
) -> AdminDashboardResponseDto:
    return await service.get_dashboard()