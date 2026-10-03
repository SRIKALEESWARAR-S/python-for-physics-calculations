"""Native ``.sri`` container (ZIP). See docs/file-format.md."""
from __future__ import annotations

import json
import os
import zipfile
from pathlib import Path
from typing import Any

from ..document import Document, Metadata, PageLayout
from .errors import CorruptDocumentError, UnsupportedVersionError

APPLICATION = "Sri's Office"
FORMAT_NAME = "sri"
FORMAT_VERSION = 1
SUFFIX = ".sri"

_MANIFEST = "manifest.json"
_HTML = "document.html"
_METADATA = "metadata.json"
_STYLES = "styles.json"
_MEDIA_PREFIX = "media/"


def _dumps(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def save_sri(document: Document, path: Path) -> None:
    """Write ``document`` to ``path`` atomically (temp file + rename)."""
    path = Path(path)
    manifest = {"application": APPLICATION, "format": FORMAT_NAME,
                "version": FORMAT_VERSION}
    styles = {"version": 1, "paragraph_styles": document.paragraph_styles,
              "page": document.page.to_dict()}
    temp = path.with_name(path.name + ".tmp")
    try:
        with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(_MANIFEST, _dumps(manifest))
            archive.writestr(_HTML, document.html)
            archive.writestr(_METADATA, _dumps(document.metadata.to_dict()))
            archive.writestr(_STYLES, _dumps(styles))
            for name, blob in document.media.items():
                archive.writestr(_MEDIA_PREFIX + name, blob)
        os.replace(temp, path)
    except BaseException:
        temp.unlink(missing_ok=True)
        raise


def _read_json(archive: zipfile.ZipFile, name: str) -> dict[str, Any]:
    try:
        data = json.loads(archive.read(name).decode("utf-8"))
    except KeyError:
        raise CorruptDocumentError(f"The file is missing '{name}'.") from None
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise CorruptDocumentError(f"'{name}' inside the file is unreadable.") from None
    if not isinstance(data, dict):
        raise CorruptDocumentError(f"'{name}' inside the file is malformed.")
    return data


def load_sri(path: Path) -> Document:
    """Read a ``.sri`` file. Raises a ``FormatError`` subclass on any problem."""
    path = Path(path)
    try:
        archive = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        raise CorruptDocumentError("This is not a valid Sri's Office document.") from None
    with archive:
        manifest = _read_json(archive, _MANIFEST)
        if manifest.get("format") != FORMAT_NAME:
            raise CorruptDocumentError("This is not a Sri's Office document.")
        version = manifest.get("version")
        if not isinstance(version, int) or version < 1:
            raise CorruptDocumentError("The file has an invalid version number.")
        if version > FORMAT_VERSION:
            raise UnsupportedVersionError(
                f"This file uses format version {version}, but this program "
                f"only understands up to version {FORMAT_VERSION}.")
        try:
            html = archive.read(_HTML).decode("utf-8")
        except KeyError:
            raise CorruptDocumentError(f"The file is missing '{_HTML}'.") from None
        except UnicodeDecodeError:
            raise CorruptDocumentError("The document text is unreadable.") from None
        metadata = Metadata.from_dict(_read_json(archive, _METADATA))
        styles = _read_json(archive, _STYLES)
        media = {
            name[len(_MEDIA_PREFIX):]: archive.read(name)
            for name in archive.namelist()
            if name.startswith(_MEDIA_PREFIX) and not name.endswith("/")
            and ".." not in Path(name).parts
        }
    paragraph_styles = styles.get("paragraph_styles", [])
    if not (isinstance(paragraph_styles, list)
            and all(isinstance(item, str) for item in paragraph_styles)):
        paragraph_styles = []
    page = PageLayout.from_dict(styles.get("page", {}) if isinstance(styles.get("page"), dict) else {})
    return Document(html=html, metadata=metadata, page=page,
                    paragraph_styles=paragraph_styles, media=media, path=path)
