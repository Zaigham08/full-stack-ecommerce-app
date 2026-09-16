from fastapi import FastAPI

from app.api.router import router
from app.api.admin_router import router as admin_router
from app.core.handlers import register_exception_handlers
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Ecommerce API",
    version="1.0.0",
)

register_exception_handlers(app)

app.include_router(
    router,
    prefix="/api/v1",
)

app.include_router(
    admin_router,
    prefix="/api/v1",
)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)