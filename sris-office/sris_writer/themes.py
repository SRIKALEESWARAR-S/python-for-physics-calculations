"""Light / dark / system themes."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

THEMES = ("light", "dark", "system")
RESOURCES = Path(__file__).resolve().parent.parent / "resources"


def _palette(dark: bool) -> QPalette:
    p = QPalette()
    if dark:
        window, base, text, button, highlight = "#2b2d30", "#1e1f22", "#e6e6e6", "#3a3c40", "#3d7ec7"
    else:
        window, base, text, button, highlight = "#eceff3", "#ffffff", "#1c1c1c", "#f4f5f7", "#2b6cb0"
    for role, value in ((QPalette.Window, window), (QPalette.Base, base), (QPalette.AlternateBase, window),
                        (QPalette.WindowText, text), (QPalette.Text, text), (QPalette.ButtonText, text),
                        (QPalette.Button, button), (QPalette.ToolTipBase, base), (QPalette.ToolTipText, text),
                        (QPalette.Highlight, highlight), (QPalette.HighlightedText, "#ffffff")):
        p.setColor(role, QColor(value))
    p.setColor(QPalette.Disabled, QPalette.WindowText, QColor("#8a8a8a"))
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#8a8a8a"))
    p.setColor(QPalette.Disabled, QPalette.Text, QColor("#8a8a8a"))
    return p


def system_is_dark(app: QApplication) -> bool:
    scheme = getattr(app.styleHints(), "colorScheme", None)
    return bool(scheme and scheme() == Qt.ColorScheme.Dark)


def is_dark(app: QApplication, mode: str) -> bool:
    return mode == "dark" or (mode == "system" and system_is_dark(app))


def apply_theme(app: QApplication, mode: str) -> bool:
    """Apply a theme; returns True if the resulting theme is dark."""
    if mode not in THEMES:
        mode = "light"
    dark = is_dark(app, mode)
    app.setStyle("Fusion")
    app.setPalette(_palette(dark))
    qss = RESOURCES / "themes" / "ribbon.qss"
    app.setStyleSheet(qss.read_text(encoding="utf-8") if qss.is_file() else "")
    return dark
