"""Document lifecycle: new / open / save / export / print / recovery.

Sits between the UI and the model: it moves data between the editor, the
``Document`` model and the format adapters, and reports problems clearly.
"""
from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QFileDialog

from . import printing
from .dialogs import messages
from .document import Document
from .editor import PageEditor
from .formats import export_html, read_document, save_sri
from .formats.sri import SUFFIX
from .recovery import RecoveryManager
from .settings import RecentDocuments

log = logging.getLogger(__name__)
SRI_FILTER = "Sri's Writer Document (*.sri)"


class DocumentController(QObject):
    #: Emitted when the document name changes (new, open, save as).
    nameChanged = Signal()

    def __init__(self, window, editor: PageEditor, recent: RecentDocuments,
                 recovery: RecoveryManager) -> None:
        super().__init__(window)
        self._window, self._editor = window, editor
        self._recent, self._recovery = recent, recovery
        self.document = Document()

    # ---- state -----------------------------------------------------------
    @property
    def modified(self) -> bool:
        return self._editor.document().isModified()

    @property
    def display_name(self) -> str:
        return self.document.display_name

    def _install(self, document: Document) -> None:
        self.document = document
        self._editor.load_document(document)
        self.nameChanged.emit()

    # ---- unsaved-changes protection -----------------------------------------
    def maybe_save(self) -> bool:
        """True if it is safe to discard the current document."""
        if not self.modified:
            return True
        choice = messages.confirm_unsaved(self._window)
        if choice == messages.SAVE:
            return self.save()
        return choice == messages.DISCARD

    # ---- new / open / close ----------------------------------------------------
    def new(self) -> None:
        if self.maybe_save():
            self._install(Document())
            self._recovery.clear_session()

    close_document = new

    def open(self) -> None:
        start = str(self.document.path.parent) if self.document.path else str(Path.home())
        path, _ = QFileDialog.getOpenFileName(self._window, "Open", start, SRI_FILTER)
        if path:
            self.open_path(Path(path))

    def open_path(self, path: Path) -> None:
        if not self.maybe_save():
            return
        try:
            document = read_document(path)
        except Exception as exc:
            if not isinstance(exc, (OSError,)) and not hasattr(exc, "suggestion"):
                log.exception("Opening %s failed", path)
            messages.show_error(self._window, "open this document", exc)
            self._recent.remove(path)
            return
        self._install(document)
        self._recent.add(path)
        self._recovery.clear_session()

    # ---- save -------------------------------------------------------------------
    def save(self) -> bool:
        if self.document.path is None:
            return self.save_as()
        return self._write(self.document.path)

    def save_as(self) -> bool:
        start = self.document.path or (Path.home() / "Untitled.sri")
        chosen, _ = QFileDialog.getSaveFileName(self._window, "Save As", str(start), SRI_FILTER)
        if not chosen:
            return False
        path = Path(chosen)
        if path.suffix.lower() != SUFFIX:
            path = path.with_name(path.name + SUFFIX)
        return self._write(path)

    def _write(self, path: Path) -> bool:
        snapshot = self._editor.to_document(self.document)
        snapshot.path = path
        try:
            save_sri(snapshot, path)
        except Exception as exc:
            if not isinstance(exc, OSError):
                log.exception("Saving %s failed", path)
            messages.show_error(self._window, "save this document", exc)
            return False
        self.document = snapshot
        self._editor.document().setModified(False)
        self._recent.add(path)
        self._recovery.clear_session()
        self.nameChanged.emit()
        return True

    # ---- export / print -----------------------------------------------------------
    def export(self) -> None:
        stem = self.document.path.stem if self.document.path else "Untitled"
        start = str((self.document.path.parent if self.document.path else Path.home()) / f"{stem}.pdf")
        chosen, selected = QFileDialog.getSaveFileName(
            self._window, "Export", start, "PDF (*.pdf);;HTML (*.html)")
        if not chosen:
            return
        path = Path(chosen)
        want_html = path.suffix.lower() in (".html", ".htm") or (
            not path.suffix and selected.startswith("HTML"))
        if path.suffix.lower() not in (".pdf", ".html", ".htm"):
            path = path.with_name(path.name + (".html" if want_html else ".pdf"))
        self.export_to(path)

    def export_to(self, path: Path) -> bool:
        try:
            if path.suffix.lower() == ".pdf":
                printing.export_pdf(self._editor.document(), self._editor.page_layout, path,
                                    self.document.metadata.title or self.display_name)
            else:
                export_html(self._editor.to_document(self.document), path)
        except Exception as exc:
            if not isinstance(exc, OSError):
                log.exception("Export to %s failed", path)
            messages.show_error(self._window, "export this document", exc)
            return False
        return True

    def print_document(self) -> None:
        printing.print_with_dialog(self._window, self._editor.document(), self._editor.page_layout)

    def print_preview(self) -> None:
        printing.show_print_preview(self._window, self._editor.document(), self._editor.page_layout)

    # ---- autosave & recovery ----------------------------------------------------------
    def autosave(self) -> None:
        try:
            if self.modified:
                self._recovery.write(self._editor.to_document(self.document))
            else:
                self._recovery.clear_session()
        except Exception:
            log.exception("Autosave failed")

    def offer_recovery(self) -> None:
        for entry in self._recovery.pending():
            if messages.confirm_restore(self._window):
                try:
                    document = self._recovery.load(entry)
                except Exception:
                    log.exception("Could not load recovery file %s", entry.file)
                    self._recovery.discard(entry)
                    continue
                self._install(document)
                self._editor.document().setModified(True)   # must be saved explicitly
                self._recovery.discard(entry)
                return
            self._recovery.discard(entry)

    def shutdown(self) -> None:
        self._recovery.clear_session()
