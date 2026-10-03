"""Qt-free document model.

This is the single source of truth that every format adapter reads and
writes. Nothing in this module imports Qt, so it can be tested anywhere.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

#: Portrait dimensions in millimetres.
PAGE_SIZES_MM: dict[str, tuple[float, float]] = {
    "A4": (210.0, 297.0),
    "A5": (148.0, 210.0),
    "Letter": (215.9, 279.4),
    "Legal": (215.9, 355.6),
}
PORTRAIT = "portrait"
LANDSCAPE = "landscape"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class PageLayout:
    """Physical page description. Width/height are always portrait values."""

    size_name: str = "A4"
    width_mm: float = 210.0
    height_mm: float = 297.0
    orientation: str = PORTRAIT
    margin_top_mm: float = 25.4
    margin_bottom_mm: float = 25.4
    margin_left_mm: float = 25.4
    margin_right_mm: float = 25.4

    @classmethod
    def named(cls, size_name: str, orientation: str = PORTRAIT) -> "PageLayout":
        width, height = PAGE_SIZES_MM[size_name]
        return cls(size_name=size_name, width_mm=width, height_mm=height,
                   orientation=orientation)

    @property
    def effective_size_mm(self) -> tuple[float, float]:
        """(width, height) after applying orientation."""
        if self.orientation == LANDSCAPE:
            return self.height_mm, self.width_mm
        return self.width_mm, self.height_mm

    @property
    def text_width_mm(self) -> float:
        return self.effective_size_mm[0] - self.margin_left_mm - self.margin_right_mm

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PageLayout":
        """Build from untrusted data, ignoring unknown keys and bad values."""
        base = cls()
        for key, default in base.__dict__.items():
            value = data.get(key, default)
            try:
                setattr(base, key, type(default)(value))
            except (TypeError, ValueError):
                pass
        if base.orientation not in (PORTRAIT, LANDSCAPE):
            base.orientation = PORTRAIT
        return base


@dataclass
class Metadata:
    title: str = ""
    author: str = ""
    language: str = "en"
    created: str = field(default_factory=_now)
    modified: str = field(default_factory=_now)
    #: Free-form extension point for future features.
    extra: dict[str, Any] = field(default_factory=dict)

    def touch(self) -> None:
        self.modified = _now()

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Metadata":
        meta = cls()
        for key in ("title", "author", "language", "created", "modified"):
            if isinstance(data.get(key), str):
                setattr(meta, key, data[key])
        if isinstance(data.get("extra"), dict):
            meta.extra = data["extra"]
        return meta


@dataclass
class Document:
    """A Sri's Writer document, independent of any file format or widget."""

    html: str = ""
    metadata: Metadata = field(default_factory=Metadata)
    page: PageLayout = field(default_factory=PageLayout)
    #: Semantic style name of each paragraph, in document order.
    paragraph_styles: list[str] = field(default_factory=list)
    #: Embedded resources, keyed by path inside ``media/`` (future images).
    media: dict[str, bytes] = field(default_factory=dict)
    #: Where the document lives on disk; ``None`` for a new document.
    path: Path | None = None

    @property
    def display_name(self) -> str:
        if self.path is not None:
            return self.path.name
        return "Untitled"
