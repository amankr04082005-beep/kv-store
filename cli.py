"""
A simple REPL (read-eval-print loop) around KeyValueStore, so you can play
with it directly from a terminal -- similar to redis-cli.

Commands:
  SET key value [TTL seconds]
  GET key
  DEL key
  EXISTS key
  KEYS
  HELP
  EXIT
"""

import shlex

from store import KeyValueStore

HELP_TEXT = """\
Commands:
  SET key value [ttl_seconds]   store a value, optional expiry in seconds
  GET key                       fetch a value (None if missing/expired)
  DEL key                       delete a key
  EXISTS key                    check if a key exists (and isn't expired)
  KEYS                          list all current keys
  HELP                          show this message
  EXIT                          quit
"""


def main():
    store = KeyValueStore(capacity=50)
    print("Mini Key-Value Store (capacity=50, LRU eviction). Type HELP for commands.")

    while True:
        try:
            raw = input("kv> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not raw:
            continue

        try:
            parts = shlex.split(raw)
        except ValueError as e:
            print(f"(error) could not parse input: {e}")
            continue

        cmd = parts[0].upper()

        if cmd == "SET" and len(parts) >= 3:
            key, value = parts[1], parts[2]
            ttl = None
            if len(parts) >= 4:
                try:
                    ttl = float(parts[3])
                except ValueError:
                    print("(error) ttl must be a number")
                    continue
            store.set(key, value, ttl=ttl)
            print("OK")

        elif cmd == "GET" and len(parts) == 2:
            value = store.get(parts[1])
            print(value if value is not None else "(nil)")

        elif cmd == "DEL" and len(parts) == 2:
            removed = store.delete(parts[1])
            print("(integer) 1" if removed else "(integer) 0")

        elif cmd == "EXISTS" and len(parts) == 2:
            print("(integer) 1" if store.exists(parts[1]) else "(integer) 0")

        elif cmd == "KEYS" and len(parts) == 1:
            keys = store.keys()
            if not keys:
                print("(empty)")
            else:
                for i, k in enumerate(keys, 1):
                    print(f"{i}) {k}")

        elif cmd == "HELP":
            print(HELP_TEXT)

        elif cmd == "EXIT":
            break

        else:
            print("(error) unknown command or wrong number of arguments. Type HELP.")


if __name__ == "__main__":
    main()
