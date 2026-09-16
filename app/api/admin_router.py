from fastapi import APIRouter, Depends

from app.features.auth.admin import get_current_admin

from app.features.orders.admin_router import router as admin_orders_router
from app.features.categories.admin_router import router as admin_categories_router
from app.features.products.admin_router import router as admin_products_router
from app.features.admin.router import router as admin_dashboard_router


router = APIRouter(
    prefix="/admin",
    dependencies=[
        Depends(get_current_admin),
    ],
)

router.include_router(
    admin_dashboard_router,
    prefix="",
    tags=["Admin - Dashboard"],
)

router.include_router(
    admin_categories_router,
    prefix="/categories",
    tags=["Admin - Categories"],
)

router.include_router(
    admin_products_router,
    prefix="/products",
    tags=["Admin - Products"],
)

router.include_router(
    admin_orders_router,
    prefix="/orders",
    tags=["Admin - Orders"],
)
