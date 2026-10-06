from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any

_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()

def _get_lock(path: str) -> threading.Lock:
    with _locks_guard:
        if path not in _locks:
            _locks[path] = threading.Lock()
        return _locks[path]

class JsonStorage:

    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def path_for(self, filename: str) -> Path:
        if not filename.endswith(".json"):
            filename = f"{filename}.json"
        return self.data_dir / filename

    def load(self, filename: str, default: Any = None) -> Any:
        path = self.path_for(filename)
        lock = _get_lock(str(path))
        with lock:
            if not path.exists():
                if default is not None:
                    self._write_unlocked(path, default)
                    return default
                return [] if default is None else default
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return default if default is not None else []

    def save(self, filename: str, data: Any) -> None:
        path = self.path_for(filename)
        lock = _get_lock(str(path))
        with lock:
            self._write_unlocked(path, data)

    def _write_unlocked(self, path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)

    def next_id(self, filename: str) -> int:
        items = self.load(filename, default=[])
        if not items:
            return 1
        return max(int(item.get("id", 0)) for item in items) + 1
