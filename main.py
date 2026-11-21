"""Command line entry point for the inventory app."""
import argparse
import sys
from typing import List, Optional

from inventory.exceptions import InventoryError
from inventory.reports import (
    category_totals,
    export_csv,
    low_stock_report,
    render_table,
    summary,
)
from inventory.services import InventoryService
from inventory.storage import Storage
from inventory.utils import format_currency


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="inventory")
    parser.add_argument("--db", default="inventory.db", help="SQLite database path")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add a new item")
    add.add_argument("sku")
    add.add_argument("name")
    add.add_argument("price", type=float)
    add.add_argument("--quantity", type=int, default=0)
    add.add_argument("--category", default="general")

    listing = sub.add_parser("list", help="list items")
    listing.add_argument("--category")

    sell = sub.add_parser("sell", help="sell units of an item")
    sell.add_argument("sku")
    sell.add_argument("amount", type=int)

    restock = sub.add_parser("restock", help="add units to an item")
    restock.add_argument("sku")
    restock.add_argument("amount", type=int)

    search = sub.add_parser("search", help="search items by name")
    search.add_argument("term")

    sub.add_parser("report", help="show inventory summary")

    export = sub.add_parser("export", help="export items to CSV")
    export.add_argument("path")
    return parser


def run_command(args: argparse.Namespace, service: InventoryService) -> None:
    if args.command == "add":
        item = service.add_item(args.sku, args.name, args.price, args.quantity, args.category)
        print(f"Added {item.sku} ({item.name})")
    elif args.command == "list":
        print(render_table(service.list_items(args.category)))
    elif args.command == "sell":
        revenue = service.sell(args.sku, args.amount)
        print(f"Sold {args.amount} x {args.sku} for {format_currency(revenue)}")
    elif args.command == "restock":
        item = service.restock(args.sku, args.amount)
        print(f"{item.sku} now has {item.quantity} units")
    elif args.command == "search":
        print(render_table(service.search(args.term)))
    elif args.command == "report":
        items = service.list_items()
        stats = summary(items)
        print(f"Items: {stats['distinct_items']}  Units: {stats['total_units']}")
        print(f"Total value: {format_currency(stats['total_value'])}")
        for category, value in category_totals(items).items():
            print(f"  {category}: {format_currency(value)}")
        for line in low_stock_report(items):
            print(f"  LOW {line}")
    elif args.command == "export":
        count = export_csv(service.list_items(), args.path)
        print(f"Exported {count} items to {args.path}")


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    with Storage(args.db) as storage:
        try:
            run_command(args, InventoryService(storage))
        except InventoryError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
