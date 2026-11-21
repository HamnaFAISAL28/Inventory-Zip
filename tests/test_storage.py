import pytest

from inventory.exceptions import DuplicateItemError, ItemNotFoundError
from inventory.models import Item


def item(sku="ABC-100", **kw):
    return Item(sku=sku, name=kw.pop("name", "Widget"), price=2.0, **kw)


def test_add_and_get(storage):
    storage.add_item(item(quantity=4))
    assert storage.get_item("ABC-100").quantity == 4
    assert storage.count() == 1


def test_get_missing(storage):
    assert storage.get_item("NOPE-000") is None


def test_duplicate(storage):
    storage.add_item(item())
    with pytest.raises(DuplicateItemError):
        storage.add_item(item())


def test_list_and_filter(storage):
    storage.add_item(item("ABC-100", category="a"))
    storage.add_item(item("ABC-200", category="b"))
    assert [i.sku for i in storage.list_items()] == ["ABC-100", "ABC-200"]
    assert [i.sku for i in storage.list_items("b")] == ["ABC-200"]


def test_search(storage):
    storage.add_item(item("ABC-100", name="Blue Pen"))
    storage.add_item(item("ABC-200", name="Notebook"))
    assert [i.sku for i in storage.search_by_name("pen")] == ["ABC-100"]
    assert storage.search_by_name("zzz") == []


def test_update_quantity(storage):
    storage.add_item(item())
    storage.update_quantity("ABC-100", 9)
    assert storage.get_item("ABC-100").quantity == 9
    with pytest.raises(ItemNotFoundError):
        storage.update_quantity("NOPE-000", 1)


def test_delete(storage):
    storage.add_item(item())
    assert storage.delete_item("ABC-100") is True
    assert storage.delete_item("ABC-100") is False


def test_context_manager(tmp_path):
    from inventory.storage import Storage

    db = tmp_path / "test.db"
    with Storage(str(db)) as store:
        store.add_item(item())
    with Storage(str(db)) as store:
        assert store.count() == 1
