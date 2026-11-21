"""Report generation helpers."""
import csv
from collections import defaultdict
from typing import Dict, List

from inventory.models import Item
from inventory.utils import format_currency, truncate


def summary(items: List[Item]) -> Dict[str, float]:
    total_units = sum(item.quantity for item in items)
    total_value = round(sum(item.total_value() for item in items), 2)
    out_of_stock = sum(1 for item in items if not item.is_in_stock())
    return {
        "distinct_items": len(items),
        "total_units": total_units,
        "total_value": total_value,
        "out_of_stock": out_of_stock,
    }


def category_totals(items: List[Item]) -> Dict[str, float]:
    totals: Dict[str, float] = defaultdict(float)
    for item in items:
        totals[item.category] += item.total_value()
    return {category: round(value, 2) for category, value in sorted(totals.items())}


def top_valued(items: List[Item], count: int = 3) -> List[Item]:
    return sorted(items, key=lambda item: item.total_value(), reverse=True)[:count]


def low_stock_report(items: List[Item], threshold: int = 5) -> List[str]:
    lines = []
    for item in items:
        if item.quantity <= threshold:
            lines.append(f"{item.sku} {truncate(item.name, 20)}: {item.quantity} left")
    return lines


def render_table(items: List[Item]) -> str:
    header = f"{'SKU':<10}{'Name':<24}{'Price':>10}{'Qty':>6}  Category"
    rows = [header, "-" * len(header)]
    for item in items:
        rows.append(
            f"{item.sku:<10}{truncate(item.name, 22):<24}"
            f"{format_currency(item.price):>10}{item.quantity:>6}  {item.category}"
        )
    return "\n".join(rows)


def export_csv(items: List[Item], path: str) -> int:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["sku", "name", "price", "quantity", "category"]
        )
        writer.writeheader()
        for item in items:
            writer.writerow(item.to_dict())
    return len(items)
