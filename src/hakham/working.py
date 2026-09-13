from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass


@dataclass(frozen=True)
class WorkingItem:
    key: str
    value: str


class WorkingMemory:
    """Small volatile task context. It is intentionally not durable."""

    def __init__(self, max_items: int = 12) -> None:
        if max_items < 1:
            raise ValueError("max_items must be positive")
        self.max_items = max_items
        self._items: OrderedDict[str, str] = OrderedDict()

    def set(self, key: str, value: str) -> None:
        key = key.strip()
        value = value.strip()
        if not key or not value:
            raise ValueError("working memory key and value are required")
        if key in self._items:
            del self._items[key]
        self._items[key] = value
        while len(self._items) > self.max_items:
            self._items.popitem(last=False)

    def get(self, key: str) -> str | None:
        return self._items.get(key)

    def snapshot(self) -> list[WorkingItem]:
        return [WorkingItem(key, value) for key, value in self._items.items()]

    def clear(self) -> None:
        self._items.clear()
