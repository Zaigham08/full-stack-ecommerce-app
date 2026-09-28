import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.model import RefreshToken


class RefreshTokenRepository:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        family_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            family_id=family_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        self.db.add(refresh_token)

        await self.db.flush()

        return refresh_token

    async def get_by_hash_for_update(
        self,
        token_hash: str,
    ) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken)
            .where(
                RefreshToken.token_hash == token_hash
            )
            .with_for_update()
        )

        return result.scalar_one_or_none()

    async def revoke(
        self,
        refresh_token: RefreshToken,
        now: datetime,
    ) -> None:
        refresh_token.revoked_at = now

        await self.db.flush()

    async def mark_used(
        self,
        refresh_token: RefreshToken,
        now: datetime,
    ) -> None:
        refresh_token.used_at = now
        refresh_token.revoked_at = now

        await self.db.flush()

    async def revoke_family(
        self,
        family_id: uuid.UUID,
        now: datetime,
    ) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.family_id == family_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(
                revoked_at=now,
            )
        )

        await self.db.flush()