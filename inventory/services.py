"""Business logic built on top of the storage layer."""
from typing import Dict, List, Optional

from inventory.exceptions import (
    InsufficientStockError,
    ItemNotFoundError,
    ValidationError,
)
from inventory.models import Item, Order
from inventory.storage import Storage
from inventory.validators import (
    validate_category,
    validate_name,
    validate_price,
    validate_quantity,
    validate_sku,
)


class InventoryService:
    """High level operations on inventory items and orders."""

    LOW_STOCK_THRESHOLD = 5

    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    def add_item(
        self,
        sku: str,
        name: str,
        price: float,
        quantity: int = 0,
        category: str = "general",
    ) -> Item:
        item = Item(
            sku=validate_sku(sku),
            name=validate_name(name),
            price=validate_price(price),
            quantity=validate_quantity(quantity),
            category=validate_category(category),
        )
        self.storage.add_item(item)
        return item

    def get_item(self, sku: str) -> Item:
        item = self.storage.get_item(sku)
        if item is None:
            raise ItemNotFoundError(sku)
        return item

    def list_items(self, category: Optional[str] = None) -> List[Item]:
        return self.storage.list_items(category)

    def search(self, term: str) -> List[Item]:
        return self.storage.search_by_name(term.strip())

    def restock(self, sku: str, amount: int) -> Item:
        item = self.get_item(sku)
        item.restock(amount)
        self.storage.update_quantity(sku, item.quantity)
        return item

    def sell(self, sku: str, amount: int) -> float:
        item = self.get_item(sku)
        item.remove_stock(amount)
        self.storage.update_quantity(sku, item.quantity)
        return round(item.price * amount, 2)

    def remove_item(self, sku: str) -> None:
        if not self.storage.delete_item(sku):
            raise ItemNotFoundError(sku)

    def low_stock_items(self, threshold: Optional[int] = None) -> List[Item]:
        limit = self.LOW_STOCK_THRESHOLD if threshold is None else threshold
        return [item for item in self.list_items() if item.quantity <= limit]

    def inventory_value(self) -> float:
        return round(sum(item.total_value() for item in self.list_items()), 2)
        
    def discount_rate(self, tier: str) -> float:
        rate = 0.0
        if tier == "gold":
            rate = 0.15
        elif tier == "silver":
            rate = 0.10
        elif tier == "gold":  # BUG 2 (S1862): duplicate condition, branch is dead code
            rate = 0.20
        return rate

    def create_order(
        self,
        order_id: int,
        customer: str,
        items: Dict[str, int],
        tier: str = "standard",
    ) -> Order:
        resolved = []
        for sku, qty in items.items():
            if qty <= 0:
                raise ValidationError(f"Quantity for {sku} must be positive")
            item = self.get_item(sku)
            if qty > item.quantity:
                raise InsufficientStockError(sku, qty, item.quantity)
            resolved.append((item, qty))

        rate = self.discount_rate(tier)
        order = Order(order_id=order_id, customer=customer)
        for item, qty in resolved:
            item.remove_stock(qty)
            self.storage.update_quantity(item.sku, item.quantity)
            order.add_line(item.sku, qty, round(item.price * (1 - rate), 2))
        return order
