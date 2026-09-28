import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    verify_password,
)
from app.features.auth.dto import (
    LoginDto,
    RefreshTokenDto,
    TokenResponseDto,
)
from app.features.auth.repository import (
    RefreshTokenRepository,
)
from app.features.users.repository import UserRepository


settings = get_settings()


class AuthService:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.user_repository = UserRepository(db)

        self.refresh_token_repository = (
            RefreshTokenRepository(db)
        )

    async def login(
        self,
        data: LoginDto,
    ) -> TokenResponseDto:
        user = await self.user_repository.get_by_email(
            data.email
        )

        if user is None:
            raise InvalidCredentialsError()

        password_is_valid = verify_password(
            data.password,
            user.password_hash,
        )

        if not password_is_valid:
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InvalidCredentialsError()

        access_token = create_access_token(
            subject=str(user.id)
        )

        refresh_token = create_refresh_token()

        refresh_token_hash = hash_refresh_token(
            refresh_token
        )

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(
                days=settings.refresh_token_expire_days
            )
        )

        family_id = uuid.uuid4()

        try:
            await self.refresh_token_repository.create(
                user_id=user.id,
                family_id=family_id,
                token_hash=refresh_token_hash,
                expires_at=expires_at,
            )

            await self.db.commit()

            return TokenResponseDto(
                access_token=access_token,
                refresh_token=refresh_token,
            )

        except Exception:
            await self.db.rollback()
            raise

    async def refresh(
        self,
        data: RefreshTokenDto,
    ) -> TokenResponseDto:
        now = datetime.now(timezone.utc)

        token_hash = hash_refresh_token(
            data.refresh_token
        )

        refresh_token = (
            await self.refresh_token_repository
            .get_by_hash_for_update(token_hash)
        )

        if refresh_token is None:
            raise InvalidTokenError()

        try:
            # Old/revoked/used refresh token was presented.
            # This can indicate token reuse.
            if (
                refresh_token.revoked_at is not None
                or refresh_token.used_at is not None
            ):
                await (
                    self.refresh_token_repository
                    .revoke_family(
                        refresh_token.family_id,
                        now,
                    )
                )

                await self.db.commit()

                raise InvalidTokenError()

            if refresh_token.expires_at <= now:
                await self.refresh_token_repository.revoke(
                    refresh_token,
                    now,
                )

                await self.db.commit()

                raise InvalidTokenError()

            user = await self.user_repository.get_by_id(
                refresh_token.user_id
            )

            if user is None or not user.is_active:
                await self.refresh_token_repository.revoke(
                    refresh_token,
                    now,
                )

                await self.db.commit()

                raise InvalidTokenError()

            new_access_token = create_access_token(
                subject=str(user.id)
            )

            new_refresh_token = create_refresh_token()

            new_refresh_token_hash = (
                hash_refresh_token(
                    new_refresh_token
                )
            )

            new_expires_at = (
                now
                + timedelta(
                    days=settings.refresh_token_expire_days
                )
            )

            # The old token can never be used again.
            await self.refresh_token_repository.mark_used(
                refresh_token,
                now,
            )

            new_token_record = (
                await self.refresh_token_repository.create(
                    user_id=user.id,
                    family_id=refresh_token.family_id,
                    token_hash=new_refresh_token_hash,
                    expires_at=new_expires_at,
                )
            )

            refresh_token.replaced_by_id = (
                new_token_record.id
            )

            await self.db.commit()

            return TokenResponseDto(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
            )

        except InvalidTokenError:
            raise

        except Exception:
            await self.db.rollback()
            raise

    async def logout(
        self,
        data: RefreshTokenDto,
    ) -> None:
        token_hash = hash_refresh_token(
            data.refresh_token
        )

        refresh_token = (
            await self.refresh_token_repository
            .get_by_hash_for_update(token_hash)
        )

        if refresh_token is None:
            # Logout is intentionally idempotent.
            return

        try:
            if refresh_token.revoked_at is None:
                await self.refresh_token_repository.revoke(
                    refresh_token,
                    datetime.now(timezone.utc),
                )

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise