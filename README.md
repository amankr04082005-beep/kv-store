# In-Memory Key-Value Store

A small Redis-like key-value store built from scratch in Python: O(1) get/set,
TTL-based expiry, and LRU (Least Recently Used) eviction when the store is full.

## Features
- `SET key value [ttl]` — store a value, optionally with a time-to-live in seconds
- `GET key` — fetch a value (returns nothing if missing or expired)
- `DEL key` — remove a key
- `EXISTS key` — check if a key is present and not expired
- `KEYS` — list all current (non-expired) keys
- LRU eviction: when the store hits its capacity, the least recently used key is dropped automatically
- A small CLI (`cli.py`) to interact with it like `redis-cli`

## Tech
Pure Python standard library — no external dependencies, no database.

## Run
```bash
python cli.py
```
Example session:
```
kv> SET name Aman
OK
kv> GET name
Aman
kv> SET temp "expires soon" 2
OK
kv> GET temp
expires soon
... (wait 2+ seconds)
kv> GET temp
(nil)
```

## Run the tests
```bash
python tests/test_store.py
```

## How it works
- **O(1) get/set**: values are kept in a Python `dict` (technically an
  `OrderedDict`), so lookups and writes are constant time.
- **TTL**: each entry stores an `expires_at` timestamp. On every read or
  write, we check if the current time has passed it, and treat the key as
  gone if so (lazy expiry — no background thread needed).
- **LRU eviction**: the `OrderedDict` keeps keys in the order they were last
  touched. Every `get` or `set` moves that key to the end (`move_to_end`).
  When the store is full and a new key needs space, we pop from the front
  (`popitem(last=False)`) — that's always the least recently used key. Both
  operations are O(1), so eviction never scans the whole store.
