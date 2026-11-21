"""Data models used across the inventory package."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

from inventory.exceptions import InsufficientStockError

VALID_STATUSES = ("pending", "paid", "cancelled")


@dataclass
class Item:
    """A product held in stock."""

    sku: str
    name: str
    price: float
    quantity: int = 0
    category: str = "general"

    def is_in_stock(self) -> bool:
        return self.quantity > 0

    def total_value(self) -> float:
        return round(self.price * self.quantity, 2)

    def restock(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Restock amount must be positive")
        self.quantity += amount

    def remove_stock(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self.quantity:
            raise InsufficientStockError(self.sku, amount, self.quantity)
        self.quantity -= amount

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sku": self.sku,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Item":
        return cls(
            sku=data["sku"],
            name=data["name"],
            price=float(data["price"]),
            quantity=int(data.get("quantity", 0)),
            category=data.get("category", "general"),
        )


@dataclass
class OrderLine:
    """One line of an order."""

    sku: str
    quantity: int
    unit_price: float

    def subtotal(self) -> float:
        return round(self.quantity * self.unit_price, 2)


@dataclass
class Order:
    """A customer order made of one or more lines."""

    order_id: int
    customer: str
    lines: List[OrderLine] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"

    def add_line(self, sku: str, quantity: int, unit_price: float) -> OrderLine:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        line = OrderLine(sku, quantity, unit_price)
        self.lines.append(line)
        return line

    def total(self) -> float:
        return round(sum(line.subtotal() for line in self.lines), 2)

    def item_count(self) -> int:
        return sum(line.quantity for line in self.lines)

    def mark_paid(self) -> None:
        if self.status != "pending":
            raise ValueError(f"Cannot pay an order that is {self.status}")
        self.status = "paid"

    def cancel(self) -> None:
        if self.status == "paid":
            raise ValueError("Paid orders cannot be cancelled")
        self.status = "cancelled"
