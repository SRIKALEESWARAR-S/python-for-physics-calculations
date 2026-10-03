"""PLANNED adapters. They exist so the architecture has a place for them.

DOCX and ODT will convert to/from ``Document`` (never touch the editor).
"""
from __future__ import annotations

from pathlib import Path

from ..document import Document
from .errors import FeatureNotAvailableError


class _PlannedAdapter:
    name = ""

    def read(self, path: Path) -> Document:
        raise FeatureNotAvailableError(f"{self.name} import is PLANNED and not available yet.")

    def write(self, document: Document, path: Path) -> None:
        raise FeatureNotAvailableError(f"{self.name} export is PLANNED and not available yet.")


class DocxAdapter(_PlannedAdapter):
    """PLANNED. Likely built on python-docx. Compatibility will be partial."""
    name = "DOCX"


class OdtAdapter(_PlannedAdapter):
    """PLANNED. Likely built on odfpy. Compatibility will be partial."""
    name = "ODT"
