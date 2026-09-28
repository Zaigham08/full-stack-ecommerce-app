import asyncio
import uuid
from io import BytesIO

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError
from supabase import AsyncClient, acreate_client

from app.core.config import get_settings
from app.core.exceptions import (
    InvalidImageError,
    StorageError,
)


settings = get_settings()

_supabase_client: AsyncClient | None = None
_supabase_lock = asyncio.Lock()


ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024


async def get_supabase_client() -> AsyncClient:
    global _supabase_client

    if _supabase_client is None:
        async with _supabase_lock:
            if _supabase_client is None:
                _supabase_client = await acreate_client(
                    settings.supabase_url,
                    settings.supabase_secret_key,
                )

    return _supabase_client


async def upload_product_image(
    file: UploadFile,
    product_id: uuid.UUID,
) -> tuple[str, str]:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise InvalidImageError()

    content = await file.read(
        MAX_IMAGE_SIZE + 1
    )

    if len(content) > MAX_IMAGE_SIZE:
        raise InvalidImageError()

    try:
        image = Image.open(
            BytesIO(content)
        )

        image.verify()

    except (
        UnidentifiedImageError,
        OSError,
    ) as exc:
        raise InvalidImageError() from exc

    extension = ALLOWED_IMAGE_TYPES[
        file.content_type
    ]

    filename = (
        f"{uuid.uuid4().hex}{extension}"
    )

    storage_path = (
        f"products/{product_id}/{filename}"
    )

    supabase = await get_supabase_client()

    try:
        await (
            supabase.storage
            .from_(settings.supabase_storage_bucket)
            .upload(
                storage_path,
                content,
                {
                    "content-type": file.content_type,
                    "cache-control": "31536000",
                    "upsert": "false",
                },
            )
        )

    except Exception as exc:
        raise StorageError() from exc

    public_url = (
        f"{settings.supabase_url.rstrip('/')}"
        f"/storage/v1/object/public/"
        f"{settings.supabase_storage_bucket}"
        f"/{storage_path}"
    )

    return storage_path, public_url


async def delete_product_image(
    storage_path: str,
) -> None:
    supabase = await get_supabase_client()

    try:
        await (
            supabase.storage
            .from_(settings.supabase_storage_bucket)
            .remove(
                [storage_path]
            )
        )

    except Exception as exc:
        raise StorageError() from exc