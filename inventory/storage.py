"""SQLite persistence layer."""
import sqlite3
from typing import List, Optional

from inventory.exceptions import DuplicateItemError, ItemNotFoundError
from inventory.models import Item

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    sku TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    category TEXT NOT NULL DEFAULT 'general'
)
"""


class Storage:
    """Thin wrapper around a SQLite connection."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._conn.execute(SCHEMA)
        self._conn.commit()

    def __enter__(self) -> "Storage":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    @staticmethod
    def _row_to_item(row: tuple) -> Item:
        sku, name, price, quantity, category = row
        return Item(sku=sku, name=name, price=price, quantity=quantity, category=category)

    def add_item(self, item: Item) -> None:
        try:
            self._conn.execute(
                "INSERT INTO items (sku, name, price, quantity, category) VALUES (?, ?, ?, ?, ?)",
                (item.sku, item.name, item.price, item.quantity, item.category),
            )
            self._conn.commit()
        except sqlite3.IntegrityError as exc:
            raise DuplicateItemError(item.sku) from exc

    def get_item(self, sku: str) -> Optional[Item]:
        row = self._conn.execute(
            "SELECT sku, name, price, quantity, category FROM items WHERE sku = ?", (sku,)
        ).fetchone()
        return self._row_to_item(row) if row else None

    def list_items(self, category: Optional[str] = None) -> List[Item]:
        if category:
            rows = self._conn.execute(
                "SELECT sku, name, price, quantity, category FROM items WHERE category = ? ORDER BY sku",
                (category,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT sku, name, price, quantity, category FROM items ORDER BY sku"
            ).fetchall()
        return [self._row_to_item(row) for row in rows]

    def search_by_name(self, term: str) -> List[Item]:
        rows = self._conn.execute(
            "SELECT sku, name, price, quantity, category FROM items WHERE name LIKE ? ORDER BY name",
            (f"%{term}%",),
        ).fetchall()
        return [self._row_to_item(row) for row in rows]

    def update_quantity(self, sku: str, quantity: int) -> None:
        cursor = self._conn.execute(
            "UPDATE items SET quantity = ? WHERE sku = ?", (quantity, sku)
        )
        self._conn.commit()
        if cursor.rowcount == 0:
            raise ItemNotFoundError(sku)

    def delete_item(self, sku: str) -> bool:
        cursor = self._conn.execute("DELETE FROM items WHERE sku = ?", (sku,))
        self._conn.commit()
        return cursor.rowcount > 0

    def count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]

    def close(self) -> None:
        self._conn.close()
