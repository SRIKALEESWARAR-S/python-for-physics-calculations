"""Formatting commands. UI code calls these; they only touch the editor API."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextListFormat
from PySide6.QtWidgets import QTextEdit

_ALIGNMENTS = {
    "left": Qt.AlignLeft | Qt.AlignAbsolute,
    "center": Qt.AlignHCenter,
    "right": Qt.AlignRight | Qt.AlignAbsolute,
    "justify": Qt.AlignJustify,
}
_BULLETS = [QTextListFormat.ListDisc, QTextListFormat.ListCircle, QTextListFormat.ListSquare]
_NUMBERS = [QTextListFormat.ListDecimal, QTextListFormat.ListLowerAlpha, QTextListFormat.ListLowerRoman]
MAX_LIST_LEVEL = 6


def _enum_value(member) -> int:
    return int(getattr(member, "value", member))


# ---- character formatting -------------------------------------------------

def _merge(editor: QTextEdit, fmt: QTextCharFormat) -> None:
    editor.mergeCurrentCharFormat(fmt)


def set_font_family(editor: QTextEdit, family: str) -> None:
    fmt = QTextCharFormat()
    fmt.setFontFamilies([family])
    _merge(editor, fmt)


def set_font_size(editor: QTextEdit, size_pt: float) -> None:
    if size_pt <= 0:
        return
    fmt = QTextCharFormat()
    fmt.setFontPointSize(size_pt)
    _merge(editor, fmt)


def toggle_bold(editor: QTextEdit) -> None:
    fmt = QTextCharFormat()
    is_bold = editor.currentCharFormat().fontWeight() > QFont.Normal
    fmt.setFontWeight(QFont.Normal if is_bold else QFont.Bold)
    _merge(editor, fmt)


def toggle_italic(editor: QTextEdit) -> None:
    fmt = QTextCharFormat()
    fmt.setFontItalic(not editor.currentCharFormat().fontItalic())
    _merge(editor, fmt)


def toggle_underline(editor: QTextEdit) -> None:
    fmt = QTextCharFormat()
    fmt.setFontUnderline(not editor.currentCharFormat().fontUnderline())
    _merge(editor, fmt)


def toggle_strikethrough(editor: QTextEdit) -> None:
    fmt = QTextCharFormat()
    fmt.setFontStrikeOut(not editor.currentCharFormat().fontStrikeOut())
    _merge(editor, fmt)


def set_text_color(editor: QTextEdit, color: QColor) -> None:
    fmt = QTextCharFormat()
    fmt.setForeground(QBrush(color))
    _merge(editor, fmt)


def set_highlight(editor: QTextEdit, color: QColor | None) -> None:
    """Highlight with ``color``; ``None`` removes highlighting."""
    fmt = QTextCharFormat()
    fmt.setBackground(QBrush(color) if color else QBrush(Qt.NoBrush))
    _merge(editor, fmt)


# ---- paragraph formatting -------------------------------------------------

def set_alignment(editor: QTextEdit, name: str) -> None:
    editor.setAlignment(_ALIGNMENTS[name])


def set_line_spacing(editor: QTextEdit, percent: int) -> None:
    fmt = QTextBlockFormat()
    fmt.setLineHeight(float(percent), _enum_value(QTextBlockFormat.ProportionalHeight))
    editor.textCursor().mergeBlockFormat(fmt)


def set_paragraph_spacing(editor: QTextEdit, before_px: float, after_px: float) -> None:
    fmt = QTextBlockFormat()
    fmt.setTopMargin(before_px)
    fmt.setBottomMargin(after_px)
    editor.textCursor().mergeBlockFormat(fmt)


def change_indent(editor: QTextEdit, delta: int) -> None:
    """Indent/outdent. Inside a list this nests/unnests the list level."""
    cursor = editor.textCursor()
    current = cursor.currentList()
    if current is not None:
        fmt = current.format()
        level = max(1, min(MAX_LIST_LEVEL, fmt.indent() + delta))
        fmt.setIndent(level)
        sequence = _NUMBERS if _is_numbered(fmt.style()) else _BULLETS
        fmt.setStyle(sequence[(level - 1) % len(sequence)])
        cursor.createList(fmt)
        return
    block_fmt = cursor.blockFormat()
    new_fmt = QTextBlockFormat()
    new_fmt.setIndent(max(0, block_fmt.indent() + delta))
    cursor.mergeBlockFormat(new_fmt)


def _is_numbered(style) -> bool:
    return style in _NUMBERS


def toggle_list(editor: QTextEdit, numbered: bool) -> None:
    cursor = editor.textCursor()
    wanted = QTextListFormat.ListDecimal if numbered else QTextListFormat.ListDisc
    current = cursor.currentList()
    cursor.beginEditBlock()
    if current is not None and _is_numbered(current.format().style()) == numbered:
        _remove_from_list(cursor)
    else:
        fmt = QTextListFormat()
        fmt.setStyle(wanted)
        fmt.setIndent(1)
        cursor.createList(fmt)
    cursor.endEditBlock()


def _remove_from_list(cursor: QTextCursor) -> None:
    doc = cursor.document()
    start, end = sorted((cursor.anchor(), cursor.position()))
    block = doc.findBlock(start)
    while block.isValid() and block.position() <= end:
        item_list = QTextCursor(block).currentList()
        if item_list is not None:
            item_list.remove(block)
        fmt = QTextBlockFormat()
        fmt.setIndent(0)
        QTextCursor(block).mergeBlockFormat(fmt)
        block = block.next()
