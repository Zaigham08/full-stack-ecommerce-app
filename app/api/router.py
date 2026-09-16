from fastapi import APIRouter
from app.features.auth.router import router as auth_router
from app.features.users.router import router as users_router
from app.features.categories.router import router as categories_router
from app.features.products.router import router as products_router
from app.features.carts.router import router as carts_router
from app.features.addresses.router import router as addresses_router
from app.features.orders.router import router as orders_router
from app.features.payments.router import router as payments_router

router = APIRouter()

router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"],
)

router.include_router(
    users_router,
    prefix="/users",
    tags=["Users"],
)

router.include_router(
    categories_router,
    prefix="/categories",
    tags=["Categories"],
)

router.include_router(
    products_router,
    prefix="/products",
    tags=["Products"],
)

router.include_router(
    carts_router,
    prefix="/cart",
    tags=["Cart"],
)

router.include_router(
    addresses_router,
    prefix="/addresses",
    tags=["Addresses"],
)

router.include_router(
    orders_router,
    prefix="/orders",
    tags=["Orders"],
)

router.include_router(
    payments_router,
    prefix="/payments",
    tags=["Payments"],
)