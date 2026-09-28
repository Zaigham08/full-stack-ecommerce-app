from fastapi import FastAPI

from app.api.router import router
from app.api.admin_router import router as admin_router
from app.core.handlers import register_exception_handlers

app = FastAPI(
    title="Ecommerce API",
    version="1.0.0",
)

register_exception_handlers(app)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

app.include_router(
    router,
    prefix="/api/v1",
)

app.include_router(
    admin_router,
    prefix="/api/v1",
)
