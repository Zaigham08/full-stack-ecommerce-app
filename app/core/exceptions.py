class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int,
    ):
        self.message = message
        self.status_code = status_code

        super().__init__(message)

class UserAlreadyExistsError(AppException):
    def __init__(self):
        super().__init__(
            message="A user with this email already exists.",
            status_code=409,
        )

class UserNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message="User not found.",
            status_code=404,
        )

class InvalidCredentialsError(AppException):
    def __init__(self):
        super().__init__(
            message="Invalid email or password.",
            status_code=401,
        )

class InvalidTokenError(AppException):
    def __init__(self):
        super().__init__(
            message="Invalid or expired token.",
            status_code=401,
        )

class ForbiddenError(AppException):
    def __init__(self):
        super().__init__(
            message="You do not have permission to perform this action.",
            status_code=403,
        )

class CategoryAlreadyExistsError(AppException):
    def __init__(self):
        super().__init__(
            message="A category with this name or slug already exists.",
            status_code=409,
        )

class CategoryNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message="Category not found.",
            status_code=404,
        )

class ProductAlreadyExistsError(AppException):
    def __init__(self):
        super().__init__(
            message="A product with this slug already exists.",
            status_code=409,
        )

class ProductNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message="Product not found.",
            status_code=404,
        )

class ProductImageNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message="Product image not found.",
            status_code=404,
        )

class InvalidImageError(AppException):
    def __init__(self):
        super().__init__(
            message=(
                "Invalid image. "
                "Only JPEG, PNG and WebP images "
                "up to 5 MB are allowed."
            ),
            status_code=400,
        )

class StorageError(AppException):
    def __init__(self):
        super().__init__(
            message="File storage operation failed.",
            status_code=500,
        )

class CartNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message="Cart not found.",
            status_code=404,
        )

class CartItemNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message="Cart item not found.",
            status_code=404,
        )

class CartEmptyError(AppException):
    def __init__(self):
        super().__init__(
            message="Cart is empty.",
            status_code=400,
        )

class ProductUnavailableError(AppException):
    def __init__(self):
        super().__init__(
            message="Product is unavailable.",
            status_code=400,
        )

class InsufficientStockError(AppException):
    def __init__(self):
        super().__init__(
            message="Insufficient stock.",
            status_code=409,
        )

class AddressNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message="Shipping address not found.",
            status_code=404,
        )

class OrderNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message="Order not found.",
            status_code=404,
        )

class PaymentAlreadyExistsError(AppException):
    def __init__(self):
        super().__init__(
            message="A payment already exists for this order.",
            status_code=409,
        )

class PaymentNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message="Payment not found.",
            status_code=404,
        )

class InvalidPaymentStateError(AppException):
    def __init__(self):
        super().__init__(
            message="Payment cannot be processed in its current state.",
            status_code=409,
        )

class InventoryReservationNotFoundError(
    AppException
):
    def __init__(self):
        super().__init__(
            message="Inventory reservation not found.",
            status_code=404,
        )

class InventoryStateError(AppException):
    def __init__(self):
        super().__init__(
            message="Inventory reservation is in an invalid state.",
            status_code=409,
        )

class InvalidOrderStateError(AppException):
    def __init__(self):
        super().__init__(
            message="Invalid order status transition.",
            status_code=409,
        )