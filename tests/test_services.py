import pytest

from inventory.exceptions import (
    DuplicateItemError,
    InsufficientStockError,
    ItemNotFoundError,
    ValidationError,
)


def test_add_item_validates(service):
    with pytest.raises(ValidationError):
        service.add_item("bad", "Thing", 1.0)
    with pytest.raises(DuplicateItemError):
        service.add_item("PEN-001", "Another Pen", 1.0)


def test_get_item_missing(service):
    with pytest.raises(ItemNotFoundError):
        service.get_item("ZZZ-999")


def test_list_and_search(service):
    assert len(service.list_items()) == 4
    assert len(service.list_items("stationery")) == 2
    assert [i.sku for i in service.search(" pen ")] == ["PEN-001", "PEN-002"]


def test_restock(service):
    assert service.restock("PEN-002", 10).quantity == 13
    assert service.get_item("PEN-002").quantity == 13


def test_sell_returns_revenue(service):
    assert service.sell("PEN-001", 10) == 15.0
    assert service.get_item("PEN-001").quantity == 90


def test_sell_too_many(service):
    with pytest.raises(InsufficientStockError):
        service.sell("PEN-002", 50)


def test_remove_item(service):
    service.remove_item("BAG-100")
    with pytest.raises(ItemNotFoundError):
        service.remove_item("BAG-100")


def test_low_stock(service):
    skus = [i.sku for i in service.low_stock_items()]
    assert skus == ["BAG-100", "PEN-002"]
    assert [i.sku for i in service.low_stock_items(threshold=0)] == ["BAG-100"]


def test_inventory_value(service):
    assert service.inventory_value() == 150.0 + 5.25 + 80.0


@pytest.mark.parametrize(
    "tier,rate", [("gold", 0.15), ("silver", 0.10), ("standard", 0.0), ("", 0.0)]
)
def test_discount_rate(service, tier, rate):
    assert service.discount_rate(tier) == rate


def test_create_order_applies_discount(service):
    order = service.create_order(1, "Ali", {"PEN-001": 10, "NOT-010": 2}, tier="gold")
    assert order.total() == round(10 * 1.27 + 2 * 3.40, 2)
    assert service.get_item("PEN-001").quantity == 90
    assert service.get_item("NOT-010").quantity == 18


def test_create_order_is_atomic(service):
    with pytest.raises(InsufficientStockError):
        service.create_order(2, "Ali", {"PEN-001": 5, "PEN-002": 99})
    assert service.get_item("PEN-001").quantity == 100


def test_create_order_rejects_bad_quantity(service):
    with pytest.raises(ValidationError):
        service.create_order(3, "Ali", {"PEN-001": 0})
