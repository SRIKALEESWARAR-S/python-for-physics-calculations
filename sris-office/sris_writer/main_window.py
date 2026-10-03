"""Main window: menus, ribbon, editor, find bar and status bar."""
from __future__ import annotations

import re
from pathlib import Path

from PySide6.QtCore import QSignalBlocker, Qt, QTimer
from PySide6.QtGui import QAction, QActionGroup, QColor, QFont, QKeySequence
from PySide6.QtWidgets import (QApplication, QColorDialog, QComboBox, QFontComboBox, QMainWindow,
                               QMenu, QMessageBox, QStyle, QTabWidget, QToolButton, QVBoxLayout, QWidget)

from . import APP_NAME, SUITE_NAME, __version__, commands, themes
from .controller import DocumentController
from .dialogs.page_setup import PageSetupDialog
from .document import LANDSCAPE, PAGE_SIZES_MM, PORTRAIT
from .editor import ZOOM_STEPS, PageEditor
from .recovery import RecoveryManager
from .settings import RecentDocuments, SettingsStore
from .styles import NORMAL, STYLE_NAMES, apply_style, style_name_of
from .widgets.find_bar import FindBar
from .widgets.ribbon import RibbonGroup, make_page, tool_button

FONT_SIZES = [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 36, 48, 72]
HIGHLIGHTS = {"Yellow": "#ffff66", "Green": "#80ff80", "Cyan": "#80ffff", "Pink": "#ffb0e0"}
PLANNED_TIP = "PLANNED: not available in this version."


class MainWindow(QMainWindow):
    def __init__(self, settings: SettingsStore, recovery: RecoveryManager | None = None) -> None:
        super().__init__()
        self._settings = settings
        self._recent = RecentDocuments(settings)
        self.editor = PageEditor()
        self.controller = DocumentController(self, self.editor, self._recent,
                                             recovery or RecoveryManager())
        self.find_bar = FindBar(self.editor)
        self._syncing = False
        self._build_actions()
        self._build_menus()
        self._build_central()
        self._build_status_bar()
        self._connect_signals()
        self.resize(1100, 800)
        self._update_title()
        self._update_stats()
        self._sync_controls()
        self._autosave_timer = QTimer(self, interval=max(10, int(settings.get("saving/autosave_seconds"))) * 1000)
        self._autosave_timer.timeout.connect(self.controller.autosave)
        self._autosave_timer.start()
        QTimer.singleShot(0, self.controller.offer_recovery)

    # ------------------------------------------------------------------ actions
    def _action(self, text: str, slot, shortcut=None, tip: str = "", icon: QStyle.StandardPixmap | None = None,
                checkable: bool = False, editor_only: bool = False) -> QAction:
        action = QAction(text, self)
        action.setToolTip(f"{tip or text}" + (f" ({_shortcut_text(shortcut)})" if shortcut else ""))
        action.setCheckable(checkable)
        if icon is not None:
            action.setIcon(self.style().standardIcon(icon))
        if shortcut is not None:
            seqs = shortcut if isinstance(shortcut, list) else [shortcut]
            action.setShortcuts([QKeySequence(s) for s in seqs])
        if editor_only:   # keep native Qt behaviour: only active while the editor has focus
            action.setShortcutContext(Qt.WidgetShortcut)
            self.editor.addAction(action)
        action.triggered.connect(lambda *_: slot())
        return action

    def _format(self, fn, *args):
        """Return a slot that runs a formatting command and refocuses the editor."""
        def run(*_ignored):
            fn(self.editor, *args)
            self.editor.setFocus()
        return run

    def _build_actions(self) -> None:
        S, a, e = QStyle.StandardPixmap, self._action, self.editor
        self.act_new = a("New", self.controller.new, QKeySequence.New, icon=S.SP_FileIcon)
        self.act_open = a("Open…", self.controller.open, QKeySequence.Open, icon=S.SP_DialogOpenButton)
        self.act_save = a("Save", self.controller.save, QKeySequence.Save, icon=S.SP_DialogSaveButton)
        self.act_save_as = a("Save As…", self.controller.save_as, QKeySequence.SaveAs)
        self.act_export = a("Export PDF / HTML…", self.controller.export, tip="Export")
        self.act_preview = a("Print Preview", self.controller.print_preview)
        self.act_print = a("Print…", self.controller.print_document, QKeySequence.Print)
        self.act_close = a("Close", self.controller.close_document, QKeySequence.Close, tip="Close document")
        self.act_exit = a("Exit", self.close, QKeySequence.Quit)
        self.act_undo = a("Undo", e.undo, QKeySequence.Undo, editor_only=True)
        redo_keys = [k.toString() for k in QKeySequence.keyBindings(QKeySequence.Redo)]
        self.act_redo = a("Redo", e.redo, list({*redo_keys, "Ctrl+Y"}), editor_only=True)
        self.act_cut = a("Cut", e.cut, QKeySequence.Cut, editor_only=True)
        self.act_copy = a("Copy", e.copy, QKeySequence.Copy, editor_only=True)
        self.act_paste = a("Paste", e.paste, QKeySequence.Paste, editor_only=True)
        self.act_select_all = a("Select All", e.selectAll, QKeySequence.SelectAll, editor_only=True)
        self.act_find = a("Find…", lambda: self.find_bar.show_bar(False), QKeySequence.Find)
        self.act_replace = a("Replace…", lambda: self.find_bar.show_bar(True), QKeySequence("Ctrl+H"))
        self.act_find_next = a("Find Next", lambda: self.find_bar.find_next(), QKeySequence.FindNext)
        self.act_find_prev = a("Find Previous", lambda: self.find_bar.find_next(True), QKeySequence.FindPrevious)
        self.act_bold = a("B", self._format(commands.toggle_bold), "Ctrl+B", "Bold", checkable=True)
        self.act_italic = a("I", self._format(commands.toggle_italic), "Ctrl+I", "Italic", checkable=True)
        self.act_underline = a("U", self._format(commands.toggle_underline), "Ctrl+U", "Underline", checkable=True)
        self.act_strike = a("S", self._format(commands.toggle_strikethrough), tip="Strikethrough", checkable=True)
        self.act_bullets = a("• List", self._format(commands.toggle_list, False), tip="Bulleted list", checkable=True)
        self.act_numbers = a("1. List", self._format(commands.toggle_list, True), tip="Numbered list", checkable=True)
        self.act_indent = a("Indent →", self._format(commands.change_indent, 1), tip="Increase indent")
        self.act_outdent = a("← Outdent", self._format(commands.change_indent, -1), tip="Decrease indent")
        self.act_text_color = a("A Colour", self._pick_text_color, tip="Text colour")
        self.align_group = QActionGroup(self)
        self.act_align = {}
        for key, label, keys in (("left", "Left", "Ctrl+L"), ("center", "Centre", "Ctrl+E"),
                                 ("right", "Right", "Ctrl+R"), ("justify", "Justify", "Ctrl+J")):
            act = a(label, self._format(commands.set_alignment, key), keys, f"Align {label.lower()}", checkable=True)
            self.align_group.addAction(act)
            self.act_align[key] = act
        self.act_zoom_in = a("Zoom In", lambda: e.zoom_step(1), [QKeySequence("Ctrl++"), QKeySequence("Ctrl+=")])
        self.act_zoom_out = a("Zoom Out", lambda: e.zoom_step(-1), QKeySequence("Ctrl+-"))
        self.act_zoom_reset = a("100%", lambda: e.set_zoom(100), QKeySequence("Ctrl+0"), "Reset zoom")
        self.act_page_setup = a("Page Setup…", self._page_setup)
        self.act_about = a("About Sri's Writer", self._about)
        self.heading_actions = []
        for level in (1, 2, 3):
            act = a(f"Heading {level}", lambda n=level: self._apply_style(f"Heading {n}"), f"Ctrl+Alt+{level}")
            self.addAction(act)
            self.heading_actions.append(act)
        normal = a("Normal style", lambda: self._apply_style(NORMAL), "Ctrl+Alt+0")
        self.addAction(normal)
        self.heading_actions.append(normal)

    # -------------------------------------------------------------------- menus
    def _build_menus(self) -> None:
        bar = self.menuBar()
        file_menu = bar.addMenu("&File")
        for act in (self.act_new, self.act_open, self.act_save, self.act_save_as):
            file_menu.addAction(act)
        file_menu.addSeparator()
        file_menu.addAction(self.act_export)
        file_menu.addAction(self.act_preview)
        file_menu.addAction(self.act_print)
        file_menu.addSeparator()
        self.recent_menu = file_menu.addMenu("Recent Documents")
        self.recent_menu.aboutToShow.connect(self._fill_recent)
        file_menu.addSeparator()
        file_menu.addAction(self.act_close)
        file_menu.addAction(self.act_exit)
        edit = bar.addMenu("&Edit")
        for act in (self.act_undo, self.act_redo, None, self.act_cut, self.act_copy, self.act_paste,
                    self.act_select_all, None, self.act_find, self.act_find_next, self.act_find_prev,
                    self.act_replace):
            edit.addSeparator() if act is None else edit.addAction(act)
        bar.addMenu("&Help").addAction(self.act_about)

    def _fill_recent(self) -> None:
        self.recent_menu.clear()
        paths = self._recent.existing()
        for path in paths:
            act = self.recent_menu.addAction(path.name)
            act.setToolTip(str(path))
            act.triggered.connect(lambda _=False, p=path: self.controller.open_path(p))
        if not paths:
            self.recent_menu.addAction("(none)").setEnabled(False)

    # ------------------------------------------------------------------- ribbon
    def _build_central(self) -> None:
        ribbon = QTabWidget()
        ribbon.setObjectName("ribbon")
        ribbon.setFixedHeight(112)
        ribbon.addTab(self._file_page(), "File")
        ribbon.addTab(self._home_page(), "Home")
        ribbon.addTab(self._insert_page(), "Insert")
        ribbon.addTab(self._layout_page(), "Layout")
        ribbon.addTab(self._view_page(), "View")
        ribbon.setCurrentIndex(1)
        central = QWidget()
        column = QVBoxLayout(central)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        column.addWidget(ribbon)
        column.addWidget(self.editor, 1)
        column.addWidget(self.find_bar)
        self.setCentralWidget(central)
        self.editor.setFocus()

    def _file_page(self) -> QWidget:
        file_group, output = RibbonGroup("Document"), RibbonGroup("Output")
        for act in (self.act_new, self.act_open, self.act_save):
            file_group.add_big(tool_button(act, big=True))
        file_group.add_rows([tool_button(self.act_save_as)], [tool_button(self.act_close)])
        for act in (self.act_export, self.act_preview, self.act_print):
            output.add_big(tool_button(act, big=True))
        return make_page(file_group, output)

    def _home_page(self) -> QWidget:
        clipboard = RibbonGroup("Clipboard")
        clipboard.add_big(tool_button(self.act_paste, big=True))
        clipboard.add_rows([tool_button(self.act_cut)], [tool_button(self.act_copy)])

        self.font_box = QFontComboBox()
        self.font_box.setAccessibleName("Font family")
        self.font_box.setToolTip("Font")
        self.font_box.currentFontChanged.connect(self._on_font_family)
        self.size_box = QComboBox()
        self.size_box.setEditable(True)
        self.size_box.addItems([str(s) for s in FONT_SIZES])
        self.size_box.setMaximumWidth(64)
        self.size_box.setToolTip("Font size")
        self.size_box.setAccessibleName("Font size")
        self.size_box.textActivated.connect(self._on_font_size)
        self.highlight_button = self._highlight_button()
        font = RibbonGroup("Font")
        font.add_rows(
            [self.font_box, self.size_box],
            [tool_button(self.act_bold, bold=True), tool_button(self.act_italic, italic=True),
             tool_button(self.act_underline, underline=True), tool_button(self.act_strike),
             tool_button(self.act_text_color), self.highlight_button])

        self.spacing_box = QComboBox()
        self.spacing_box.addItems(["1.0", "1.15", "1.5", "2.0"])
        self.spacing_box.setToolTip("Line spacing")
        self.spacing_box.setAccessibleName("Line spacing")
        self.spacing_box.textActivated.connect(
            lambda t: (commands.set_line_spacing(self.editor, int(float(t) * 100)), self.editor.setFocus()))
        paragraph = RibbonGroup("Paragraph")
        paragraph.add_rows(
            [tool_button(self.act_bullets), tool_button(self.act_numbers),
             tool_button(self.act_outdent), tool_button(self.act_indent)],
            [tool_button(self.act_align[k]) for k in ("left", "center", "right", "justify")] + [self.spacing_box])

        self.style_box = QComboBox()
        self.style_box.addItems(STYLE_NAMES)
        self.style_box.setToolTip("Paragraph style")
        self.style_box.setAccessibleName("Paragraph style")
        self.style_box.textActivated.connect(self._apply_style)
        styles = RibbonGroup("Styles")
        styles.add_rows([self.style_box])

        editing = RibbonGroup("Editing")
        editing.add_rows([tool_button(self.act_find)], [tool_button(self.act_replace)])
        return make_page(clipboard, font, paragraph, styles, editing)

    def _highlight_button(self) -> QToolButton:
        button = QToolButton()
        button.setText("Highlight ▾")
        button.setToolTip("Highlight colour")
        button.setFocusPolicy(Qt.TabFocus)
        button.setPopupMode(QToolButton.InstantPopup)
        menu = QMenu(button)
        for name, value in HIGHLIGHTS.items():
            menu.addAction(name, lambda v=value: self._set_highlight(QColor(v)))
        menu.addAction("No highlight", lambda: self._set_highlight(None))
        button.setMenu(menu)
        return button

    def _insert_page(self) -> QWidget:
        group = RibbonGroup("Insert (PLANNED)")
        for label in ("Image", "Table", "Header && Footer", "Page Number", "Equation"):
            button = QToolButton()
            button.setText(label.replace("&&", "&"))
            button.setEnabled(False)
            button.setToolTip(PLANNED_TIP)
            group.add_big(button)
        return make_page(group)

    def _layout_page(self) -> QWidget:
        self.size_box = QComboBox()
        self.size_box.addItems(list(PAGE_SIZES_MM))
        self.size_box.setAccessibleName("Paper size")
        self.size_box.textActivated.connect(self._quick_page_size)
        self.orientation_box = QComboBox()
        self.orientation_box.addItems(["Portrait", "Landscape"])
        self.orientation_box.setAccessibleName("Orientation")
        self.orientation_box.textActivated.connect(self._quick_orientation)
        group = RibbonGroup("Page Setup")
        group.add_rows([self.size_box, self.orientation_box], [tool_button(self.act_page_setup)])
        return make_page(group)

    def _view_page(self) -> QWidget:
        zoom = RibbonGroup("Zoom")
        zoom.add_rows([tool_button(self.act_zoom_out), tool_button(self.act_zoom_reset),
                       tool_button(self.act_zoom_in)])
        self.theme_box = QComboBox()
        self.theme_box.addItems(["Light", "Dark", "System"])
        self.theme_box.setCurrentText(str(self._settings.get("appearance/theme")).capitalize())
        self.theme_box.setAccessibleName("Theme")
        self.theme_box.textActivated.connect(self._on_theme)
        appearance = RibbonGroup("Appearance")
        appearance.add_rows([self.theme_box])
        return make_page(zoom, appearance)

    # --------------------------------------------------------------- status bar
    def _build_status_bar(self) -> None:
        from PySide6.QtWidgets import QLabel
        bar = self.statusBar()
        self.page_label, self.words_label, self.chars_label = QLabel(), QLabel(), QLabel()
        self.zoom_box = QComboBox()
        self.zoom_box.addItems([f"{z}%" for z in ZOOM_STEPS])
        self.zoom_box.setCurrentText("100%")
        self.zoom_box.setAccessibleName("Zoom")
        self.zoom_box.textActivated.connect(lambda t: self.editor.set_zoom(int(t.rstrip("%"))))
        for widget in (self.page_label, self.words_label, self.chars_label):
            widget.setContentsMargins(10, 0, 10, 0)
            bar.addWidget(widget)
        bar.addPermanentWidget(self.zoom_box)
        self._stats_timer = QTimer(self, singleShot=True, interval=200)
        self._stats_timer.timeout.connect(self._update_stats)

    def _update_stats(self) -> None:
        text = self.editor.toPlainText()
        words = len(re.findall(r"\S+", text))
        self.page_label.setText(f"Page {self.editor.current_page()} of {self.editor.page_count()}")
        self.words_label.setText(f"{words:,} word{'s' if words != 1 else ''}")
        self.chars_label.setText(f"{len(text.replace(chr(10), '')):,} characters")

    # ------------------------------------------------------------------ signals
    def _connect_signals(self) -> None:
        e = self.editor
        e.textChanged.connect(self._stats_timer.start)
        e.cursorPositionChanged.connect(self._sync_controls)
        e.cursorPositionChanged.connect(self._update_stats)
        e.currentCharFormatChanged.connect(lambda *_: self._sync_controls())
        e.document().modificationChanged.connect(self._update_title)
        e.undoAvailable.connect(self.act_undo.setEnabled)
        e.redoAvailable.connect(self.act_redo.setEnabled)
        e.copyAvailable.connect(self.act_cut.setEnabled)
        e.copyAvailable.connect(self.act_copy.setEnabled)
        e.zoomChanged.connect(self._on_zoom_changed)
        e.pageLayoutChanged.connect(self._sync_page_boxes)
        self.controller.nameChanged.connect(self._update_title)
        self.controller.nameChanged.connect(self._sync_page_boxes)
        self.controller.nameChanged.connect(self._update_stats)
        for act in (self.act_undo, self.act_redo, self.act_cut, self.act_copy):
            act.setEnabled(False)

    def _update_title(self, *_) -> None:
        self.setWindowTitle(f"{self.controller.display_name}[*] — {APP_NAME}")
        self.setWindowModified(self.controller.modified)

    def _sync_controls(self) -> None:
        """Reflect the formatting at the cursor in the ribbon controls."""
        fmt, cursor = self.editor.currentCharFormat(), self.editor.textCursor()
        blockers = [QSignalBlocker(w) for w in (self.font_box, self.size_box, self.style_box)]
        self.act_bold.setChecked(fmt.fontWeight() > QFont.Normal)
        self.act_italic.setChecked(fmt.fontItalic())
        self.act_underline.setChecked(fmt.fontUnderline())
        self.act_strike.setChecked(fmt.fontStrikeOut())
        families = fmt.fontFamilies()
        self.font_box.setCurrentFont(QFont(families[0] if families else self.editor.font().family()))
        size = fmt.fontPointSize() or self.editor.document().defaultFont().pointSizeF()
        self.size_box.setEditText(f"{size:g}")
        self.style_box.setCurrentText(style_name_of(cursor.block()))
        alignment = self.editor.alignment()
        key = ("center" if alignment & Qt.AlignHCenter else "right" if alignment & Qt.AlignRight
               else "justify" if alignment & Qt.AlignJustify else "left")
        self.act_align[key].setChecked(True)
        current_list = cursor.currentList()
        numbered = current_list is not None and current_list.format().style() in (
            current_list.format().ListDecimal, current_list.format().ListLowerAlpha,
            current_list.format().ListLowerRoman)
        self.act_bullets.setChecked(current_list is not None and not numbered)
        self.act_numbers.setChecked(numbered)
        del blockers

    def _sync_page_boxes(self) -> None:
        layout = self.editor.page_layout
        with_blockers = [QSignalBlocker(self.size_box), QSignalBlocker(self.orientation_box)]
        if layout.size_name in PAGE_SIZES_MM:
            self.size_box.setCurrentText(layout.size_name)
        self.orientation_box.setCurrentText(layout.orientation.capitalize())
        del with_blockers
        self._update_stats()

    def _on_zoom_changed(self, percent: int) -> None:
        blocker = QSignalBlocker(self.zoom_box)
        self.zoom_box.setCurrentText(f"{percent}%")
        del blocker
        self._update_stats()

    # ----------------------------------------------------------------- handlers
    def _on_font_family(self, font: QFont) -> None:
        commands.set_font_family(self.editor, font.family())
        self.editor.setFocus()

    def _on_font_size(self, text: str) -> None:
        try:
            commands.set_font_size(self.editor, float(text))
        except ValueError:
            return
        self.editor.setFocus()

    def _apply_style(self, name: str) -> None:
        apply_style(self.editor.textCursor(), name)
        self._sync_controls()
        self.editor.setFocus()

    def _pick_text_color(self) -> None:
        color = QColorDialog.getColor(self.editor.textColor(), self, "Text Colour")
        if color.isValid():
            commands.set_text_color(self.editor, color)
        self.editor.setFocus()

    def _set_highlight(self, color: QColor | None) -> None:
        commands.set_highlight(self.editor, color)
        self.editor.setFocus()

    def _quick_page_size(self, name: str) -> None:
        layout = self.editor.page_layout
        layout.size_name = name
        layout.width_mm, layout.height_mm = PAGE_SIZES_MM[name]
        self.editor.set_page_layout(layout)

    def _quick_orientation(self, text: str) -> None:
        layout = self.editor.page_layout
        layout.orientation = LANDSCAPE if text == "Landscape" else PORTRAIT
        self.editor.set_page_layout(layout)

    def _page_setup(self) -> None:
        dialog = PageSetupDialog(self.editor.page_layout, self)
        if dialog.exec():
            self.editor.set_page_layout(dialog.result_layout())

    def _on_theme(self, text: str) -> None:
        mode = text.lower()
        self._settings.set("appearance/theme", mode)
        self.apply_theme(mode)

    def apply_theme(self, mode: str) -> None:
        dark = themes.apply_theme(QApplication.instance(), mode)
        self.editor.apply_colors(dark)

    def _about(self) -> None:
        QMessageBox.about(
            self, f"About {APP_NAME}",
            f"<b>{APP_NAME}</b> {__version__}<br>Part of {SUITE_NAME}.<br><br>"
            "A lightweight, open-source word processor for Linux.<br>Licensed under Apache-2.0.")

    def closeEvent(self, event) -> None:
        if self.controller.maybe_save():
            self.controller.shutdown()
            event.accept()
        else:
            event.ignore()


def _shortcut_text(shortcut) -> str:
    first = shortcut[0] if isinstance(shortcut, list) else shortcut
    return QKeySequence(first).toString(QKeySequence.NativeText)
