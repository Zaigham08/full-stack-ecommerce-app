from app.core.exceptions import InvalidOrderStateError
from app.features.orders.model import OrderStatus


ALLOWED_TRANSITIONS = {
    OrderStatus.PENDING: {
        OrderStatus.CONFIRMED,
        OrderStatus.CANCELLED,
    },

    OrderStatus.CONFIRMED: {
        OrderStatus.PROCESSING,
        OrderStatus.CANCELLED,
    },

    OrderStatus.PROCESSING: {
        OrderStatus.SHIPPED,
        OrderStatus.CANCELLED,
    },

    OrderStatus.SHIPPED: {
        OrderStatus.DELIVERED,
    },

    OrderStatus.DELIVERED: set(),

    OrderStatus.CANCELLED: set(),
}


def validate_order_transition(
    current_status: OrderStatus,
    new_status: OrderStatus,
) -> None:
    allowed_statuses = ALLOWED_TRANSITIONS[
        current_status
    ]

    if new_status not in allowed_statuses:
        raise InvalidOrderStateError()