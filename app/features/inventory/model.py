import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class InventoryReservationStatus(
    str,
    enum.Enum,
):
    RESERVED = "reserved"
    CONSUMED = "consumed"
    RELEASED = "released"
    RETURNED = "returned"


class InventoryReservation(Base):
    __tablename__ = "inventory_reservations"

    __table_args__ = (
        UniqueConstraint(
            "order_id",
            "product_id",
            name="uq_inventory_reservation_order_product",
        ),
        CheckConstraint(
            "quantity > 0",
            name="ck_inventory_reservation_quantity_positive",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "orders.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "products.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[InventoryReservationStatus] = (
        mapped_column(
            Enum(
                InventoryReservationStatus,
                name="inventory_reservation_status",
            ),
            nullable=False,
            default=InventoryReservationStatus.RESERVED,
            index=True,
        )
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )