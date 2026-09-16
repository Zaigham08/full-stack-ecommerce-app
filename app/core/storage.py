import uuid
from pathlib import Path

from fastapi import UploadFile


BASE_UPLOAD_DIR = Path("uploads")
PRODUCT_UPLOAD_DIR = BASE_UPLOAD_DIR / "products"


ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


async def save_product_image(
    file: UploadFile,
) -> str:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError(
            "Only JPEG, PNG and WebP images are allowed."
        )

    extension = ALLOWED_IMAGE_TYPES[file.content_type]

    PRODUCT_UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = f"{uuid.uuid4()}{extension}"

    file_path = PRODUCT_UPLOAD_DIR / filename

    content = await file.read()

    file_path.write_bytes(content)

    return f"/uploads/products/{filename}"


def delete_product_image_file(
    image_url: str,
) -> None:
    filename = Path(image_url).name
    file_path = PRODUCT_UPLOAD_DIR / filename

    if file_path.exists():
        file_path.unlink()