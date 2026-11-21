import pytest

from inventory.exceptions import InsufficientStockError
from inventory.models import Item, Order


def make_item(**overrides):
    data = {"sku": "ABC-100", "name": "Widget", "price": 2.5, "quantity": 10}
    data.update(overrides)
    return Item(**data)


def test_item_stock_flags():
    assert make_item().is_in_stock()
    assert not make_item(quantity=0).is_in_stock()


def test_total_value():
    assert make_item(price=2.5, quantity=4).total_value() == 10.0


def test_restock_and_remove():
    item = make_item(quantity=5)
    item.restock(5)
    item.remove_stock(3)
    assert item.quantity == 7


@pytest.mark.parametrize("amount", [0, -1])
def test_restock_rejects_non_positive(amount):
    with pytest.raises(ValueError):
        make_item().restock(amount)


@pytest.mark.parametrize("amount", [0, -4])
def test_remove_rejects_non_positive(amount):
    with pytest.raises(ValueError):
        make_item().remove_stock(amount)


def test_remove_more_than_available():
    with pytest.raises(InsufficientStockError) as info:
        make_item(quantity=2).remove_stock(5)
    assert info.value.available == 2
    assert info.value.requested == 5


def test_item_dict_round_trip():
    item = make_item(category="tools")
    assert Item.from_dict(item.to_dict()) == item


def test_from_dict_defaults():
    item = Item.from_dict({"sku": "ABC-100", "name": "Widget", "price": "3"})
    assert item.quantity == 0
    assert item.category == "general"
    assert item.price == 3.0


def test_order_totals():
    order = Order(order_id=1, customer="Ali")
    order.add_line("ABC-100", 2, 1.5)
    order.add_line("ABC-200", 1, 4.0)
    assert order.total() == 7.0
    assert order.item_count() == 3


def test_order_rejects_bad_quantity():
    with pytest.raises(ValueError):
        Order(order_id=1, customer="Ali").add_line("ABC-100", 0, 1.0)


def test_order_status_flow():
    order = Order(order_id=1, customer="Ali")
    order.mark_paid()
    assert order.status == "paid"
    with pytest.raises(ValueError):
        order.mark_paid()
    with pytest.raises(ValueError):
        order.cancel()


def test_order_cancel():
    order = Order(order_id=2, customer="Sara")
    order.cancel()
    assert order.status == "cancelled"
