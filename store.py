"""
An in-memory key-value store with:
  - TTL (time-to-live): a key can expire after N seconds
  - LRU eviction: when the store is full, the Least Recently Used key is
    dropped to make room for a new one

Design: a dict gives O(1) lookup by key. To track "least recently used"
in O(1) as well, we keep the keys in an OrderedDict -- every time a key is
read or written, it's moved to the end. The front of the OrderedDict is
then always the least recently used key, so eviction is O(1): just pop
the first item.
"""

import time
from collections import OrderedDict


class KeyValueStore:
    def __init__(self, capacity: int = 100):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._data: "OrderedDict[str, tuple]" = OrderedDict()  # key -> (value, expires_at)

    def _is_expired(self, expires_at) -> bool:
        return expires_at is not None and time.time() >= expires_at

    def _purge_if_expired(self, key: str) -> bool:
        """Remove key if it has expired. Returns True if it was removed."""
        entry = self._data.get(key)
        if entry is None:
            return False
        _, expires_at = entry
        if self._is_expired(expires_at):
            del self._data[key]
            return True
        return False

    def set(self, key: str, value, ttl: float | None = None) -> None:
        """
        Store key -> value. ttl is seconds until expiry, or None to never expire.
        If the store is at capacity and this is a new key, evict the least
        recently used key first.
        """
        self._purge_if_expired(key)

        expires_at = time.time() + ttl if ttl is not None else None

        if key in self._data:
            # Overwriting an existing key: update it and mark as most recently used.
            self._data[key] = (value, expires_at)
            self._data.move_to_end(key)
            return

        if len(self._data) >= self.capacity:
            self._evict_lru()

        self._data[key] = (value, expires_at)

    def get(self, key: str):
        """Return the value for key, or None if missing/expired. Marks key as recently used."""
        if self._purge_if_expired(key):
            return None
        if key not in self._data:
            return None
        value, expires_at = self._data[key]
        self._data.move_to_end(key)  # reading counts as "used"
        return value

    def delete(self, key: str) -> bool:
        """Remove key. Returns True if it existed."""
        self._purge_if_expired(key)
        if key in self._data:
            del self._data[key]
            return True
        return False

    def exists(self, key: str) -> bool:
        if self._purge_if_expired(key):
            return False
        return key in self._data

    def keys(self) -> list[str]:
        """All non-expired keys, in least-recently-used to most-recently-used order."""
        # Purge any expired keys first so the list returned is accurate.
        for key in list(self._data.keys()):
            self._purge_if_expired(key)
        return list(self._data.keys())

    def _evict_lru(self) -> None:
        if self._data:
            self._data.popitem(last=False)  # pop the front = least recently used

    def __len__(self) -> int:
        return len(self.keys())
