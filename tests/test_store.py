"""
Basic tests for KeyValueStore. Run with: python -m pytest
(or just `python tests/test_store.py` for a quick manual run without pytest)
"""
import sys
import time
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from store import KeyValueStore


def test_basic_set_get():
    store = KeyValueStore(capacity=10)
    store.set("a", "1")
    assert store.get("a") == "1"
    assert store.get("missing") is None


def test_delete():
    store = KeyValueStore(capacity=10)
    store.set("a", "1")
    assert store.delete("a") is True
    assert store.get("a") is None
    assert store.delete("a") is False


def test_ttl_expiry():
    store = KeyValueStore(capacity=10)
    store.set("a", "1", ttl=0.05)
    assert store.get("a") == "1"
    time.sleep(0.1)
    assert store.get("a") is None


def test_lru_eviction():
    store = KeyValueStore(capacity=2)
    store.set("a", "1")
    store.set("b", "2")
    store.get("a")          # "a" is now most recently used; "b" is LRU
    store.set("c", "3")     # should evict "b", not "a"
    assert store.get("a") == "1"
    assert store.get("b") is None
    assert store.get("c") == "3"


def test_overwrite_updates_recency():
    store = KeyValueStore(capacity=2)
    store.set("a", "1")
    store.set("b", "2")
    store.set("a", "updated")  # overwriting "a" should mark it as recently used
    store.set("c", "3")        # should evict "b"
    assert store.get("a") == "updated"
    assert store.get("b") is None


if __name__ == "__main__":
    tests = [
        test_basic_set_get,
        test_delete,
        test_ttl_expiry,
        test_lru_eviction,
        test_overwrite_updates_recency,
    ]
    for t in tests:
        t()
        print(f"PASS: {t.__name__}")
    print("All tests passed.")
