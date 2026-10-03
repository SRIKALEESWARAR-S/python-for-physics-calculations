"""Autosave / crash recovery. Never touches the user's original file."""
from __future__ import annotations

import copy
import os
import uuid
from dataclasses import dataclass
from pathlib import Path

from .document import Document
from .formats.sri import load_sri, save_sri

_ORIGINAL_KEY = "recovery_original_path"
_PREFIX = "recovery-"
_SUFFIX = ".sri"


def default_recovery_dir() -> Path:
    base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return base / "sris-office" / "recovery"


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


@dataclass(frozen=True)
class RecoveryEntry:
    file: Path
    original_path: str | None


class RecoveryManager:
    """Writes one recovery file per running session."""

    def __init__(self, directory: Path | None = None, pid: int | None = None) -> None:
        self.directory = Path(directory) if directory else default_recovery_dir()
        self._pid = pid if pid is not None else os.getpid()
        self.session_file = self.directory / f"{_PREFIX}{self._pid}-{uuid.uuid4().hex[:8]}{_SUFFIX}"

    def write(self, document: Document) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        snapshot = Document(html=document.html, metadata=copy.deepcopy(document.metadata),
                            page=document.page, paragraph_styles=document.paragraph_styles,
                            media=document.media)
        snapshot.metadata.extra[_ORIGINAL_KEY] = str(document.path) if document.path else ""
        save_sri(snapshot, self.session_file)

    def clear_session(self) -> None:
        self.session_file.unlink(missing_ok=True)

    def pending(self) -> list[RecoveryEntry]:
        """Recovery files left behind by sessions that are no longer running."""
        entries: list[RecoveryEntry] = []
        if not self.directory.is_dir():
            return entries
        for file in sorted(self.directory.glob(f"{_PREFIX}*{_SUFFIX}")):
            if file == self.session_file:
                continue
            try:
                pid = int(file.name[len(_PREFIX):].split("-", 1)[0])
            except ValueError:
                continue
            if _pid_alive(pid):
                continue
            try:
                original = load_sri(file).metadata.extra.get(_ORIGINAL_KEY) or None
            except Exception:
                file.unlink(missing_ok=True)   # unreadable recovery file is useless
                continue
            entries.append(RecoveryEntry(file, original))
        return entries

    @staticmethod
    def load(entry: RecoveryEntry) -> Document:
        document = load_sri(entry.file)
        document.path = None          # restored text is a NEW document: no silent overwrite
        document.metadata.extra.pop(_ORIGINAL_KEY, None)
        return document

    @staticmethod
    def discard(entry: RecoveryEntry) -> None:
        entry.file.unlink(missing_ok=True)
