"""Built-in paragraph styles.

Styles are *semantic*: each block stores its style name as a custom block
property, so features like a table of contents can read real structure.
Headings additionally use Qt's heading level, which round-trips via HTML.
"""
from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QTextBlock, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextFormat

#: Custom QTextBlockFormat property holding the style name.
PROP_STYLE_NAME = int(QTextFormat.UserProperty) + 1
NORMAL = "Normal"
DEFAULT_SIZE_PT = 11.0


@dataclass(frozen=True)
class StyleDefinition:
    name: str
    size_pt: float = DEFAULT_SIZE_PT
    bold: bool = False
    italic: bool = False
    heading_level: int = 0            # 0 = not a heading
    alignment: Qt.AlignmentFlag = Qt.AlignLeft
    space_before: float = 0.0         # px
    space_after: float = 8.0          # px
    color: str | None = None
    left_indent: int = 0              # indent levels


BUILTIN_STYLES: dict[str, StyleDefinition] = {s.name: s for s in (
    StyleDefinition(NORMAL),
    StyleDefinition("Title", 26, bold=True, alignment=Qt.AlignHCenter, space_after=12),
    StyleDefinition("Subtitle", 15, italic=True, alignment=Qt.AlignHCenter, color="#7a7a7a", space_after=12),
    StyleDefinition("Heading 1", 18, bold=True, heading_level=1, space_before=16, space_after=8),
    StyleDefinition("Heading 2", 15, bold=True, heading_level=2, space_before=12, space_after=6),
    StyleDefinition("Heading 3", 13, bold=True, heading_level=3, space_before=10, space_after=4),
    StyleDefinition("Heading 4", 11.5, bold=True, italic=True, heading_level=4, space_before=8, space_after=4),
    StyleDefinition("Quote", 11, italic=True, color="#7a7a7a", left_indent=2, space_before=6, space_after=6),
    StyleDefinition("Caption", 9.5, italic=True, color="#7a7a7a", alignment=Qt.AlignHCenter),
)}

STYLE_NAMES = list(BUILTIN_STYLES)
#: After pressing Enter at the end of these, the next paragraph is Normal.
RESET_AFTER = {"Title", "Subtitle", "Heading 1", "Heading 2", "Heading 3", "Heading 4", "Caption"}


def style_name_of(block: QTextBlock) -> str:
    """Semantic style of a block; infers headings from Qt heading level."""
    value = block.blockFormat().property(PROP_STYLE_NAME)
    if isinstance(value, str) and value in BUILTIN_STYLES:
        return value
    level = block.blockFormat().headingLevel()
    if 1 <= level <= 4:
        return f"Heading {level}"
    return NORMAL


def all_style_names(document) -> list[str]:
    """Style name of every paragraph, in order."""
    names, block = [], document.begin()
    while block.isValid():
        names.append(style_name_of(block))
        block = block.next()
    return names


def restore_style_names(document, names: list[str]) -> None:
    """Re-attach stored style names after loading HTML (no-op if counts differ)."""
    if len(names) != document.blockCount():
        return
    block = document.begin()
    for name in names:
        if name in BUILTIN_STYLES and name != NORMAL and style_name_of(block) != name:
            cursor = QTextCursor(block)
            fmt = QTextBlockFormat()
            fmt.setProperty(PROP_STYLE_NAME, name)
            cursor.mergeBlockFormat(fmt)
        block = block.next()


def _char_format(style: StyleDefinition) -> QTextCharFormat:
    fmt = QTextCharFormat()
    fmt.setFontPointSize(style.size_pt)
    fmt.setFontWeight(QFont.Bold if style.bold else QFont.Normal)
    fmt.setFontItalic(style.italic)
    if style.color:
        fmt.setForeground(QColor(style.color))
    return fmt


def apply_style(cursor: QTextCursor, name: str) -> None:
    """Apply a built-in style to every paragraph touched by ``cursor``."""
    style = BUILTIN_STYLES.get(name)
    if style is None:
        return
    cursor.beginEditBlock()
    start, end = sorted((cursor.anchor(), cursor.position()))
    doc = cursor.document()
    block = doc.findBlock(start)
    while block.isValid() and block.position() <= end:
        _apply_to_block(block, style)
        block = block.next()
    cursor.endEditBlock()


def _apply_to_block(block: QTextBlock, style: StyleDefinition) -> None:
    cursor = QTextCursor(block)
    block_fmt = QTextBlockFormat()
    block_fmt.setHeadingLevel(style.heading_level)
    block_fmt.setAlignment(style.alignment)
    block_fmt.setTopMargin(style.space_before)
    block_fmt.setBottomMargin(style.space_after)
    block_fmt.setIndent(style.left_indent)
    block_fmt.setProperty(PROP_STYLE_NAME, style.name)
    cursor.mergeBlockFormat(block_fmt)
    char_fmt = _char_format(style)
    cursor.setBlockCharFormat(char_fmt)
    cursor.movePosition(QTextCursor.StartOfBlock)
    cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
    cursor.setCharFormat(char_fmt)   # applying a style resets direct character formatting
