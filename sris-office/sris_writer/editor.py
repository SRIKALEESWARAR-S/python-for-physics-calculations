"""The page-style rich text editor widget (a thin layer over QTextEdit)."""
from __future__ import annotations

import copy
import math

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPalette, QPen, QTextFrameFormat
from PySide6.QtWidgets import QFrame, QTextEdit

from .document import Document, PageLayout
from .styles import NORMAL, RESET_AFTER, all_style_names, apply_style, restore_style_names, style_name_of

ZOOM_STEPS = (50, 75, 100, 125, 150, 200)
DEFAULT_FONT_PT = 11.0
_DESK_GAP_PX = 18


def mm_to_px(mm: float, dpi: float) -> float:
    return mm / 25.4 * dpi


class PageEditor(QTextEdit):
    """Rich text editor drawn as a white page on a grey desk.

    It knows about ``Document`` only through ``load_document`` and
    ``to_document``; it never touches files or formats.
    """

    zoomChanged = Signal(int)
    pageLayoutChanged = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._layout = PageLayout()
        self._zoom = 100
        self._base_dpi = float(self.logicalDpiY()) or 96.0
        self._dpi_device = QImage(1, 1, QImage.Format_ARGB32)
        self.setAcceptRichText(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.setAutoFillBackground(True)
        self.setAccessibleName("Document editor")
        self.setTabChangesFocus(False)
        font = QFont(self.document().defaultFont())
        font.setPointSizeF(DEFAULT_FONT_PT)
        self.document().setDefaultFont(font)
        self.document().setDocumentMargin(0)
        self.apply_colors(dark=False)
        self._apply_geometry()

    # ---- document <-> model ----------------------------------------------
    @property
    def page_layout(self) -> PageLayout:
        return copy.deepcopy(self._layout)

    def load_document(self, model: Document) -> None:
        doc = self.document()
        doc.setUndoRedoEnabled(False)
        self.setHtml(model.html)
        restore_style_names(doc, model.paragraph_styles)
        doc.setUndoRedoEnabled(True)
        self._layout = copy.deepcopy(model.page)
        self._apply_geometry()
        doc.setModified(False)
        self.moveCursor(self.textCursor().Start)

    def to_document(self, base: Document) -> Document:
        """Snapshot the editor into a model; ``base`` supplies metadata/media."""
        metadata = copy.deepcopy(base.metadata)
        metadata.touch()
        return Document(html=self.toHtml(), metadata=metadata, page=self.page_layout,
                        paragraph_styles=all_style_names(self.document()),
                        media=dict(base.media), path=base.path)

    # ---- page geometry ------------------------------------------------------
    def set_page_layout(self, layout: PageLayout) -> None:
        self._layout = copy.deepcopy(layout)
        self._apply_geometry()
        self.document().setModified(True)
        self.pageLayoutChanged.emit()

    def _dpi(self) -> float:
        return self._base_dpi * self._zoom / 100.0

    def _page_size_px(self) -> tuple[float, float]:
        width_mm, height_mm = self._layout.effective_size_mm
        return mm_to_px(width_mm, self._dpi()), mm_to_px(height_mm, self._dpi())

    def _apply_geometry(self) -> None:
        # Scale fonts by giving the layout a paint device with zoomed DPI.
        self._dpi_device.setDotsPerMeterX(int(self._dpi() / 0.0254))
        self._dpi_device.setDotsPerMeterY(int(self._dpi() / 0.0254))
        self.document().documentLayout().setPaintDevice(self._dpi_device)
        page_w, _ = self._page_size_px()
        self.setLineWrapColumnOrWidth(int(page_w))
        frame_fmt = QTextFrameFormat(self.document().rootFrame().frameFormat())
        dpi = self._dpi()
        frame_fmt.setLeftMargin(mm_to_px(self._layout.margin_left_mm, dpi))
        frame_fmt.setRightMargin(mm_to_px(self._layout.margin_right_mm, dpi))
        frame_fmt.setTopMargin(mm_to_px(self._layout.margin_top_mm, dpi))
        frame_fmt.setBottomMargin(mm_to_px(self._layout.margin_bottom_mm, dpi))
        self.document().rootFrame().setFrameFormat(frame_fmt)
        self._recenter()
        self.viewport().update()

    def _recenter(self) -> None:
        page_w, _ = self._page_size_px()
        side = max(_DESK_GAP_PX, int((self.width() - page_w) / 2))
        self.setViewportMargins(side, _DESK_GAP_PX, side, _DESK_GAP_PX)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._recenter()

    # ---- pages (approximate until real pagination lands; see ROADMAP) -----
    def page_count(self) -> int:
        _, page_h = self._page_size_px()
        return max(1, math.ceil(self.document().size().height() / page_h))

    def current_page(self) -> int:
        _, page_h = self._page_size_px()
        y = self.cursorRect().top() + self.verticalScrollBar().value()
        return min(self.page_count(), max(1, int(y // page_h) + 1))

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        _, page_h = self._page_size_px()
        if page_h <= 0:
            return
        painter = QPainter(self.viewport())
        painter.setPen(QPen(QColor(128, 128, 128, 140), 1, Qt.DashLine))
        offset = self.verticalScrollBar().value()
        pages = self.page_count()
        for index in range(1, pages):
            y = int(index * page_h - offset)
            if 0 <= y <= self.viewport().height():
                painter.drawLine(0, y, self.viewport().width(), y)
        painter.end()

    # ---- zoom ---------------------------------------------------------------
    @property
    def zoom(self) -> int:
        return self._zoom

    def set_zoom(self, percent: int) -> None:
        percent = max(25, min(400, int(percent)))
        if percent == self._zoom:
            return
        self._zoom = percent
        self._apply_geometry()
        self.zoomChanged.emit(percent)

    def zoom_step(self, direction: int) -> None:
        steps = list(ZOOM_STEPS)
        if direction > 0:
            self.set_zoom(next((s for s in steps if s > self._zoom), steps[-1]))
        else:
            self.set_zoom(next((s for s in reversed(steps) if s < self._zoom), steps[0]))

    def wheelEvent(self, event) -> None:
        if event.modifiers() & Qt.ControlModifier:
            self.zoom_step(1 if event.angleDelta().y() > 0 else -1)
            event.accept()
            return
        super().wheelEvent(event)

    # ---- behaviour ------------------------------------------------------------
    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not (event.modifiers() & Qt.ShiftModifier):
            cursor = self.textCursor()
            reset = cursor.atBlockEnd() and style_name_of(cursor.block()) in RESET_AFTER
            super().keyPressEvent(event)
            if reset:
                apply_style(self.textCursor(), NORMAL)
            return
        super().keyPressEvent(event)

    def apply_colors(self, dark: bool) -> None:
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor("#202124" if dark else "#ffffff"))
        palette.setColor(QPalette.Text, QColor("#e8eaed" if dark else "#1a1a1a"))
        palette.setColor(QPalette.Window, QColor("#3c4043" if dark else "#c9ccd1"))
        self.setPalette(palette)
