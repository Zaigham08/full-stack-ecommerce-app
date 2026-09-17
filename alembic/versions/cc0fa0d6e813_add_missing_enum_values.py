"""add missing enum values

Revision ID: cc0fa0d6e813
Revises: 8e9f9db327a9
Create Date: 2026-09-17 18:39:37.353315

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc0fa0d6e813'
down_revision: Union[str, Sequence[str], None] = '8e9f9db327a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(
            """
            ALTER TYPE inventory_reservation_status
            ADD VALUE IF NOT EXISTS 'RETURNED'
            """
        )

        op.execute(
            """
            ALTER TYPE payment_status
            ADD VALUE IF NOT EXISTS 'REFUND_PENDING'
            """
        )


def downgrade() -> None:
    """Downgrade schema."""
    pass
