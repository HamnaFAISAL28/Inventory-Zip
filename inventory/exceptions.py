"""Custom exceptions for the inventory package."""


class InventoryError(Exception):
    """Base class for all inventory errors."""


class ValidationError(InventoryError):
    """Raised when user input fails validation."""


class ItemNotFoundError(InventoryError):
    def __init__(self, sku: str) -> None:
        super().__init__(f"Item not found: {sku}")
        self.sku = sku


class DuplicateItemError(InventoryError):
    def __init__(self, sku: str) -> None:
        super().__init__(f"Item already exists: {sku}")
        self.sku = sku


class InsufficientStockError(InventoryError):
    def __init__(self, sku: str, requested: int, available: int) -> None:
        super().__init__(
            f"Insufficient stock for {sku}: requested {requested}, available {available}"
        )
        self.sku = sku
        self.requested = requested
        self.available = available


class AuthenticationError(InventoryError):
    """Raised when login or registration fails."""
