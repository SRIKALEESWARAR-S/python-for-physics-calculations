"""Persistent settings and the recent-documents list.

``SettingsStore`` talks to any backend with ``value``/``setValue`` (QSettings
in the app, a dict-backed fake in tests). Values are stored as JSON strings
to avoid QSettings' type-guessing quirks.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol


class Backend(Protocol):
    def value(self, key: str, default: Any = None) -> Any: ...
    def setValue(self, key: str, value: Any) -> None: ...


class MemoryBackend:
    """Dict-backed backend for tests."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def value(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def setValue(self, key: str, value: Any) -> None:
        self._data[key] = value


DEFAULTS: dict[str, Any] = {
    "appearance/theme": "light",      # light | dark | system
    "editor/default_font": "",        # empty = system default
    "editor/default_size": 11,
    "saving/autosave_seconds": 60,
    "view/zoom": 100,
}


class SettingsStore:
    def __init__(self, backend: Backend) -> None:
        self._backend = backend

    def get(self, key: str, default: Any = None) -> Any:
        fallback = DEFAULTS.get(key) if default is None else default
        raw = self._backend.value(key, None)
        if raw is None:
            return fallback
        try:
            return json.loads(raw)
        except (TypeError, ValueError):
            return fallback

    def set(self, key: str, value: Any) -> None:
        self._backend.setValue(key, json.dumps(value))


def qt_settings_store() -> SettingsStore:
    """Store backed by the platform's QSettings (``~/.config`` on Linux)."""
    from PySide6.QtCore import QSettings
    return SettingsStore(QSettings("SrisOffice", "SrisWriter"))


class RecentDocuments:
    """Most-recent-first list of document paths."""

    KEY = "files/recent"

    def __init__(self, store: SettingsStore, limit: int = 10) -> None:
        self._store = store
        self._limit = limit

    def _load(self) -> list[str]:
        items = self._store.get(self.KEY, [])
        return [item for item in items if isinstance(item, str)] if isinstance(items, list) else []

    def add(self, path: Path) -> None:
        entry = str(Path(path).expanduser().resolve())
        items = [item for item in self._load() if item != entry]
        self._store.set(self.KEY, [entry, *items][: self._limit])

    def remove(self, path: Path | str) -> None:
        self._store.set(self.KEY, [item for item in self._load() if item != str(path)])

    def existing(self) -> list[Path]:
        """Recent files that still exist; missing ones are dropped silently."""
        items = self._load()
        alive = [item for item in items if Path(item).is_file()]
        if alive != items:
            self._store.set(self.KEY, alive)
        return [Path(item) for item in alive]

    def clear(self) -> None:
        self._store.set(self.KEY, [])
