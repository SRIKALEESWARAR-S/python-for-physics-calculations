"""Format adapters: ``File <-> Document``. No Qt widgets in here."""
from __future__ import annotations

from pathlib import Path

from ..document import Document
from .errors import (CorruptDocumentError, FeatureNotAvailableError,  # noqa: F401
                     FormatError, UnsupportedVersionError)
from .html import export_html
from .sri import SUFFIX as SRI_SUFFIX, load_sri, save_sri


def read_document(path: Path) -> Document:
    """Open a document, choosing the adapter by file extension."""
    path = Path(path)
    if path.suffix.lower() == SRI_SUFFIX:
        return load_sri(path)
    if path.suffix.lower() in (".docx", ".odt"):
        from .planned import DocxAdapter, OdtAdapter
        adapter = DocxAdapter() if path.suffix.lower() == ".docx" else OdtAdapter()
        return adapter.read(path)
    raise CorruptDocumentError(f"Unsupported file type '{path.suffix}'.")


def write_document(document: Document, path: Path) -> None:
    """Save/export a document, choosing the adapter by file extension."""
    suffix = Path(path).suffix.lower()
    if suffix == SRI_SUFFIX:
        save_sri(document, path)
    elif suffix in (".html", ".htm"):
        export_html(document, path)
    else:
        raise FeatureNotAvailableError(f"Cannot write '{suffix}' files yet.")
