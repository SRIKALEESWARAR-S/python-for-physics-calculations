"""Inline find / replace bar shown above the status bar."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QTextCursor, QTextDocument
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QWidget

_FLAG = QTextDocument.FindFlag


class FindBar(QWidget):
    closed = Signal()

    def __init__(self, editor: QTextEdit, parent=None) -> None:
        super().__init__(parent)
        self._editor = editor
        self._find = QLineEdit(placeholderText="Find")
        self._replace = QLineEdit(placeholderText="Replace with")
        self._case = QCheckBox("Match case")
        self._status = QLabel()
        self._find.setAccessibleName("Find text")
        self._replace.setAccessibleName("Replacement text")
        buttons = {
            "Next": lambda: self.find_next(), "Previous": lambda: self.find_next(backwards=True),
            "Replace": self.replace_current, "Replace All": self.replace_all, "Close": self.close_bar}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.addWidget(self._find, 2)
        self._widgets_replace = [self._replace]
        layout.addWidget(self._replace, 2)
        for text, slot in buttons.items():
            button = QPushButton(text)
            button.clicked.connect(slot)
            layout.addWidget(button)
            if text in ("Replace", "Replace All"):
                self._widgets_replace.append(button)
        layout.addWidget(self._case)
        layout.addWidget(self._status)
        self._find.returnPressed.connect(lambda: self.find_next())
        self.hide()

    def show_bar(self, replace: bool = False) -> None:
        for widget in self._widgets_replace:
            widget.setVisible(replace)
        selected = self._editor.textCursor().selectedText()
        if selected and "\u2029" not in selected:
            self._find.setText(selected)
        self.show()
        self._find.setFocus()
        self._find.selectAll()

    def close_bar(self) -> None:
        self.hide()
        self._status.clear()
        self.closed.emit()
        self._editor.setFocus()

    def _flags(self, backwards: bool = False):
        flags = _FLAG(0)
        if backwards:
            flags |= _FLAG.FindBackward
        if self._case.isChecked():
            flags |= _FLAG.FindCaseSensitively
        return flags

    def find_next(self, backwards: bool = False) -> bool:
        text = self._find.text()
        if not text:
            return False
        flags = self._flags(backwards)
        if self._editor.find(text, flags):
            self._status.clear()
            return True
        saved = self._editor.textCursor()
        self._editor.moveCursor(QTextCursor.End if backwards else QTextCursor.Start)
        if self._editor.find(text, flags):
            self._status.setText("Wrapped around")
            return True
        self._editor.setTextCursor(saved)
        self._status.setText("Not found")
        return False

    def replace_current(self) -> None:
        text, cursor = self._find.text(), self._editor.textCursor()
        selected = cursor.selectedText()
        same = selected == text if self._case.isChecked() else selected.lower() == text.lower()
        if text and same:
            cursor.insertText(self._replace.text())
        self.find_next()

    def replace_all(self) -> None:
        text = self._find.text()
        if not text:
            return
        document, count = self._editor.document(), 0
        cursor = QTextCursor(document)
        cursor.beginEditBlock()
        search = QTextCursor(document)
        while True:
            search = document.find(text, search, self._flags())
            if search.isNull():
                break
            search.insertText(self._replace.text())
            count += 1
        cursor.endEditBlock()
        self._status.setText(f"{count} replaced")
