"""Small general-purpose helpers."""
import re
from typing import Iterator, List, Sequence, TypeVar

T = TypeVar("T")


def format_currency(amount: float, symbol: str = "$") -> str:
    return f"{symbol}{amount:,.2f}"


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return slug.strip("-")


def chunk(seq: Sequence[T], size: int) -> Iterator[List[T]]:
    if size <= 0:
        raise ValueError("Chunk size must be positive")
    for start in range(0, len(seq), size):
        yield list(seq[start:start + size])


def clamp(value: float, low: float, high: float) -> float:
    if low > high:
        raise ValueError("low must not exceed high")
    return max(low, min(value, high))


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in ("1", "true", "yes", "y", "on"):
        return True
    if normalized in ("0", "false", "no", "n", "off"):
        return False
    raise ValueError(f"Cannot interpret '{value}' as a boolean")


def truncate(text: str, length: int, suffix: str = "...") -> str:
    if len(text) <= length:
        return text
    return text[: max(length - len(suffix), 0)] + suffix
