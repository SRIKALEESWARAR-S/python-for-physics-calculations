"""Page setup dialog: size, orientation and margins."""
from __future__ import annotations

from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox,
                               QFormLayout, QVBoxLayout)

from ..document import LANDSCAPE, PAGE_SIZES_MM, PORTRAIT, PageLayout

CUSTOM = "Custom"


def _spin(value: float, low: float = 0.0, high: float = 1000.0) -> QDoubleSpinBox:
    box = QDoubleSpinBox()
    box.setRange(low, high)
    box.setDecimals(1)
    box.setSuffix(" mm")
    box.setValue(value)
    return box


class PageSetupDialog(QDialog):
    def __init__(self, layout: PageLayout, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Page Setup")
        self._size = QComboBox()
        self._size.addItems([*PAGE_SIZES_MM, CUSTOM])
        self._size.setCurrentText(layout.size_name if layout.size_name in PAGE_SIZES_MM else CUSTOM)
        self._orientation = QComboBox()
        self._orientation.addItems(["Portrait", "Landscape"])
        self._orientation.setCurrentText(layout.orientation.capitalize())
        self._width = _spin(layout.width_mm, 50)
        self._height = _spin(layout.height_mm, 50)
        self._margins = {name: _spin(getattr(layout, f"margin_{name}_mm"), 0, 100)
                         for name in ("top", "bottom", "left", "right")}
        form = QFormLayout()
        form.addRow("Paper size:", self._size)
        form.addRow("Width:", self._width)
        form.addRow("Height:", self._height)
        form.addRow("Orientation:", self._orientation)
        for name, box in self._margins.items():
            form.addRow(f"{name.capitalize()} margin:", box)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(buttons)
        self._size.currentTextChanged.connect(self._on_size)
        self._on_size(self._size.currentText())

    def _on_size(self, name: str) -> None:
        custom = name == CUSTOM
        self._width.setEnabled(custom)
        self._height.setEnabled(custom)
        if not custom:
            width, height = PAGE_SIZES_MM[name]
            self._width.setValue(width)
            self._height.setValue(height)

    def result_layout(self) -> PageLayout:
        return PageLayout(
            size_name=self._size.currentText(), width_mm=self._width.value(),
            height_mm=self._height.value(),
            orientation=LANDSCAPE if self._orientation.currentText() == "Landscape" else PORTRAIT,
            margin_top_mm=self._margins["top"].value(), margin_bottom_mm=self._margins["bottom"].value(),
            margin_left_mm=self._margins["left"].value(), margin_right_mm=self._margins["right"].value())
