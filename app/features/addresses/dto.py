import uuid

from pydantic import BaseModel, ConfigDict, Field


class CreateAddressDto(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=150,
    )

    phone: str = Field(
        min_length=7,
        max_length=30,
    )

    address_line: str = Field(
        min_length=5,
        max_length=500,
    )

    city: str = Field(
        min_length=2,
        max_length=100,
    )

    postal_code: str | None = Field(
        default=None,
        max_length=20,
    )

    is_default: bool = False


class AddressResponseDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    phone: str
    address_line: str
    city: str
    postal_code: str | None
    is_default: bool