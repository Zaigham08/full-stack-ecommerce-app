import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.features.addresses.dto import CreateAddressDto
from app.features.addresses.repository import AddressRepository


class AddressService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = AddressRepository(db)

    async def create_address(
        self,
        user_id: uuid.UUID,
        data: CreateAddressDto,
    ):
        try:
            current_default = await self.repository.get_default_by_user(
                user_id
            )

            # First address automatically becomes default.
            # If user explicitly selects this address as default,
            # replace the existing default.
            should_be_default = (
                data.is_default or current_default is None
            )

            if should_be_default:
                await self.repository.clear_default_by_user(user_id)

            address = await self.repository.create(
                user_id=user_id,
                full_name=data.full_name,
                phone=data.phone,
                address_line=data.address_line,
                city=data.city,
                postal_code=data.postal_code,
                is_default=should_be_default,
            )

            await self.db.commit()

            return address

        except Exception:
            await self.db.rollback()
            raise