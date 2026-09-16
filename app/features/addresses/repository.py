import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.addresses.model import Address


class AddressRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        full_name: str,
        phone: str,
        address_line: str,
        city: str,
        postal_code: str | None,
        is_default: bool,
    ) -> Address:
        address = Address(
            user_id=user_id,
            full_name=full_name,
            phone=phone,
            address_line=address_line,
            city=city,
            postal_code=postal_code,
            is_default=is_default,
        )

        self.db.add(address)

        await self.db.flush()
        await self.db.refresh(address)

        return address

    async def get_by_id(
        self,
        address_id: uuid.UUID,
    ) -> Address | None:
        result = await self.db.execute(
            select(Address).where(
                Address.id == address_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: uuid.UUID,
    ) -> list[Address]:
        result = await self.db.execute(
            select(Address)
            .where(Address.user_id == user_id)
            .order_by(Address.created_at.desc())
        )

        return list(result.scalars().all())