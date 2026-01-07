"""Simple cache manager (skeleton).

Lightweight LRU-like cache used by indexer and context builder.
"""
from collections import OrderedDict
from typing import Any


class CacheManager:
    def __init__(self, capacity: int = 1024):
        self.capacity = capacity
        self._store = OrderedDict()

    def get(self, key: str) -> Any:
        value = self._store.get(key)
        if value is not None:
            # move to end (most recently used)
            self._store.move_to_end(key)
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value
        self._store.move_to_end(key)
        if len(self._store) > self.capacity:
            self._store.popitem(last=False)

    def clear(self) -> None:
        self._store.clear()
