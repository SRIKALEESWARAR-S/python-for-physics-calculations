"""PDF export, printing and print preview (Qt only; model-independent)."""
from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import QMarginsF, QSizeF
from PySide6.QtGui import QPageLayout, QPageSize, QPdfWriter, QTextDocument, QTextFrameFormat
from PySide6.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog

from .document import LANDSCAPE, PageLayout


def to_qpage_layout(layout: PageLayout) -> QPageLayout:
    """Convert our page model to Qt's. Orientation is applied by Qt."""
    size = QPageSize(QSizeF(layout.width_mm, layout.height_mm), QPageSize.Millimeter)
    orientation = QPageLayout.Landscape if layout.orientation == LANDSCAPE else QPageLayout.Portrait
    margins = QMarginsF(layout.margin_left_mm, layout.margin_top_mm,
                        layout.margin_right_mm, layout.margin_bottom_mm)
    return QPageLayout(size, orientation, margins, QPageLayout.Millimeter)


def output_clone(document: QTextDocument) -> QTextDocument:
    """Copy of the editor document prepared for paged output.

    The editor draws page margins as frame margins; real output uses the
    device's page margins instead, so the clone has none of its own.
    """
    clone = document.clone()
    clone.setDocumentMargin(0)
    root = clone.rootFrame()
    fmt = QTextFrameFormat(root.frameFormat())
    for setter in (fmt.setLeftMargin, fmt.setRightMargin, fmt.setTopMargin, fmt.setBottomMargin):
        setter(0)
    root.setFrameFormat(fmt)
    return clone


def export_pdf(document: QTextDocument, layout: PageLayout, path: Path, title: str = "") -> None:
    """Write a multi-page PDF. Raises ``OSError`` if the file cannot be written."""
    path = Path(path)
    temp = path.with_name(path.name + ".tmp")
    with open(temp, "wb"):          # raises the real PermissionError etc. up front
        pass
    try:
        writer = QPdfWriter(str(temp))
        writer.setPageLayout(to_qpage_layout(layout))
        writer.setTitle(title)
        writer.setCreator("Sri's Writer")
        output_clone(document).print_(writer)
        del writer                   # flush and close the file
        if temp.stat().st_size == 0:
            raise OSError("The PDF file could not be written.")
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def print_with_dialog(parent, document: QTextDocument, layout: PageLayout) -> bool:
    """Show the print dialog (printer, page range, copies) and print."""
    printer = QPrinter(QPrinter.HighResolution)
    printer.setPageLayout(to_qpage_layout(layout))
    dialog = QPrintDialog(printer, parent)
    dialog.setOption(QPrintDialog.PrintPageRange, True)
    if dialog.exec() != QPrintDialog.Accepted:
        return False
    output_clone(document).print_(printer)
    return True


def show_print_preview(parent, document: QTextDocument, layout: PageLayout) -> None:
    printer = QPrinter(QPrinter.HighResolution)
    printer.setPageLayout(to_qpage_layout(layout))
    clone = output_clone(document)
    preview = QPrintPreviewDialog(printer, parent)
    preview.paintRequested.connect(clone.print_)
    preview.resize(900, 700)
    preview.exec()
