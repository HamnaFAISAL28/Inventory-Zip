import pytest

from inventory.exceptions import ValidationError
from inventory import validators as v


def test_valid_sku():
    assert v.validate_sku("ABC-1234") == "ABC-1234"


@pytest.mark.parametrize("sku", ["abc-123", "A-123", "ABC123", "", None, "ABCDE-123"])
def test_invalid_sku(sku):
    with pytest.raises(ValidationError):
        v.validate_sku(sku)


def test_name_is_trimmed():
    assert v.validate_name("  Pen  ") == "Pen"


@pytest.mark.parametrize("name", ["a", "x" * 61, 42])
def test_invalid_name(name):
    with pytest.raises(ValidationError):
        v.validate_name(name)


def test_price_rounding():
    assert v.validate_price("1.456") == 1.46


@pytest.mark.parametrize("price", [0, -5, "abc", None, 2_000_000])
def test_invalid_price(price):
    with pytest.raises(ValidationError):
        v.validate_price(price)


def test_quantity_valid():
    assert v.validate_quantity(0) == 0


@pytest.mark.parametrize("qty", [-1, 1.5, "3", True])
def test_quantity_invalid(qty):
    with pytest.raises(ValidationError):
        v.validate_quantity(qty)


def test_category_normalised():
    assert v.validate_category("  Paper ") == "paper"


@pytest.mark.parametrize("category", ["", "   ", None])
def test_category_invalid(category):
    with pytest.raises(ValidationError):
        v.validate_category(category)


def test_email():
    assert v.validate_email("User@Example.com") == "user@example.com"
    with pytest.raises(ValidationError):
        v.validate_email("not-an-email")


def test_password_length():
    assert v.validate_password("longenough") == "longenough"
    with pytest.raises(ValidationError):
        v.validate_password("short")
