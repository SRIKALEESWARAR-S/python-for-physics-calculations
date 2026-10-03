"""Small building blocks for the ribbon-style toolbar."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton, QVBoxLayout, QWidget


class RibbonGroup(QFrame):
    """A titled group of controls: big buttons plus stacked rows of widgets."""

    def __init__(self, title: str) -> None:
        super().__init__()
        self._content = QHBoxLayout()
        self._content.setSpacing(2)
        label = QLabel(title)
        label.setObjectName("groupTitle")
        label.setAlignment(Qt.AlignHCenter)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(6, 2, 6, 0)
        outer.setSpacing(0)
        outer.addLayout(self._content, 1)
        outer.addWidget(label)

    def add_big(self, widget: QWidget) -> None:
        self._content.addWidget(widget)

    def add_rows(self, *rows: list[QWidget]) -> None:
        column = QVBoxLayout()
        column.setSpacing(2)
        for row in rows:
            line = QHBoxLayout()
            line.setSpacing(1)
            for widget in row:
                line.addWidget(widget)
            line.addStretch(1)
            column.addLayout(line)
        column.addStretch(1)
        self._content.addLayout(column)


def make_page(*groups: RibbonGroup) -> QWidget:
    page = QWidget()
    layout = QHBoxLayout(page)
    layout.setContentsMargins(2, 2, 2, 0)
    layout.setSpacing(0)
    for group in groups:
        layout.addWidget(group)
    layout.addStretch(1)
    return page


def tool_button(action: QAction, big: bool = False, bold: bool = False,
                italic: bool = False, underline: bool = False) -> QToolButton:
    """Keyboard-focusable (Tab) but not focus-stealing on click."""
    button = QToolButton()
    button.setDefaultAction(action)
    button.setFocusPolicy(Qt.TabFocus)
    button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon if big else Qt.ToolButtonTextOnly)
    if not big:
        font = button.font()
        font.setBold(bold)
        font.setItalic(italic)
        font.setUnderline(underline)
        button.setFont(font)
        button.setMinimumWidth(28)
    else:
        button.setMinimumWidth(52)
    button.setAccessibleName(action.toolTip() or action.text())
    return button
