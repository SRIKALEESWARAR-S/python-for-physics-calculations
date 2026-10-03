"""HTML export (write-only)."""
from __future__ import annotations

from html import escape
from pathlib import Path

from ..document import Document

_FALLBACK = "<!DOCTYPE html>\n<html><head><meta charset=\"utf-8\"><title>{title}</title></head><body>{body}</body></html>\n"


def export_html(document: Document, path: Path) -> None:
    """Write the document's HTML as a standalone UTF-8 file."""
    html = document.html
    if "<html" not in html.lower():
        html = _FALLBACK.format(title=escape(document.metadata.title or document.display_name),
                                body=html)
    elif "<meta charset" not in html.lower():
        html = html.replace("<head>", "<head><meta charset=\"utf-8\">", 1)
    Path(path).write_text(html, encoding="utf-8")
