"""Input validation helpers."""
import re

from inventory.exceptions import ValidationError

SKU_PATTERN = re.compile(r"^[A-Z]{2,4}-\d{3,6}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_PRICE = 1_000_000


def validate_sku(sku: str) -> str:
    if not isinstance(sku, str) or not SKU_PATTERN.match(sku):
        raise ValidationError(f"Invalid SKU '{sku}'. Expected format like ABC-1234")
    return sku


def validate_name(name: str) -> str:
    if not isinstance(name, str):
        raise ValidationError("Name must be a string")
    cleaned = name.strip()
    if len(cleaned) < 2 or len(cleaned) > 60:
        raise ValidationError("Name must be between 2 and 60 characters")
    return cleaned


def validate_price(price: float) -> float:
    try:
        value = float(price)
    except (TypeError, ValueError) as exc:
        raise ValidationError("Price must be a number") from exc
    if value <= 0 or value > MAX_PRICE:
        raise ValidationError(f"Price must be between 0 and {MAX_PRICE}")
    return round(value, 2)


def validate_quantity(quantity: int) -> int:
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise ValidationError("Quantity must be an integer")
    if quantity < 0:
        raise ValidationError("Quantity cannot be negative")
    return quantity


def validate_category(category: str) -> str:
    if not isinstance(category, str) or not category.strip():
        raise ValidationError("Category cannot be empty")
    return category.strip().lower()


def validate_email(email: str) -> str:
    if not isinstance(email, str) or not EMAIL_PATTERN.match(email):
        raise ValidationError(f"Invalid email address: {email}")
    return email.lower()


def validate_password(password: str) -> str:
    if not isinstance(password, str) or len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    return password
