import pytest
import os
from inventory.auth import AuthService
from inventory.services import InventoryService
from inventory.storage import Storage


import os
os.environ.setdefault("ADMIN_PASSWORD", "test-admin-pass")

@pytest.fixture
def storage():
    store = Storage(":memory:")
    yield store
    store.close()


@pytest.fixture
def service(storage):
    svc = InventoryService(storage)
    svc.add_item("PEN-001", "Blue Pen", 1.50, 100, "stationery")
    svc.add_item("PEN-002", "Red Pen", 1.75, 3, "stationery")
    svc.add_item("NOT-010", "Notebook", 4.00, 20, "paper")
    svc.add_item("BAG-100", "School Bag", 25.00, 0, "bags")
    return svc


@pytest.fixture
def auth(monkeypatch):
    monkeypatch.setattr(AuthService, "ITERATIONS", 1_000)
    return AuthService()
