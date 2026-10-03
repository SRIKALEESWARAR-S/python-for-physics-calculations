"""Qt-dependent tests: formatting, styles, round-trip, HTML and PDF export.

Skipped automatically when PySide6 is not installed. Run headless with
QT_QPA_PLATFORM=offscreen (run.sh --test does this).
"""
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    from PySide6.QtGui import QFont, QTextCursor
    from PySide6.QtWidgets import QApplication
    HAVE_QT = True
except ImportError:      # pragma: no cover
    HAVE_QT = False


@unittest.skipUnless(HAVE_QT, "PySide6 not installed")
class FormattingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def make_editor(self, text="Hello world"):
        from sris_writer.editor import PageEditor
        editor = PageEditor()
        editor.setPlainText(text)
        return editor

    def test_bold_on_selection(self):
        from sris_writer import commands
        editor = self.make_editor()
        editor.selectAll()
        commands.toggle_bold(editor)
        self.assertGreater(editor.textCursor().charFormat().fontWeight(), QFont.Normal)
        commands.toggle_bold(editor)
        self.assertEqual(editor.textCursor().charFormat().fontWeight(), QFont.Normal)

    def test_font_size(self):
        from sris_writer import commands
        editor = self.make_editor()
        editor.selectAll()
        commands.set_font_size(editor, 20)
        self.assertEqual(editor.textCursor().charFormat().fontPointSize(), 20)

    def test_heading_style_is_semantic(self):
        from sris_writer.styles import all_style_names, apply_style
        editor = self.make_editor("Title\nBody")
        cursor = editor.textCursor()
        cursor.setPosition(0)
        apply_style(cursor, "Heading 1")
        self.assertEqual(all_style_names(editor.document()), ["Heading 1", "Normal"])
        self.assertEqual(editor.document().firstBlock().blockFormat().headingLevel(), 1)

    def test_lists_toggle_and_nest(self):
        from sris_writer import commands
        editor = self.make_editor("item")
        commands.toggle_list(editor, numbered=False)
        self.assertIsNotNone(editor.textCursor().currentList())
        commands.change_indent(editor, 1)
        self.assertEqual(editor.textCursor().currentList().format().indent(), 2)
        commands.toggle_list(editor, numbered=False)   # toggling the same type removes the list
        self.assertIsNone(editor.textCursor().currentList())

    def test_undo_redo(self):
        editor = self.make_editor("")
        editor.insertPlainText("abc")
        editor.undo()
        self.assertEqual(editor.toPlainText(), "")
        editor.redo()
        self.assertEqual(editor.toPlainText(), "abc")

    def test_document_round_trip_through_sri(self):
        from sris_writer.document import Document, PageLayout
        from sris_writer.formats.sri import load_sri, save_sri
        from sris_writer.styles import all_style_names, apply_style
        editor = self.make_editor("Heading\nBody text")
        c = editor.textCursor()
        c.setPosition(0)
        apply_style(c, "Title")
        model = editor.to_document(Document(page=PageLayout.named("Letter")))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t.sri"
            save_sri(model, path)
            other = self.make_editor("")
            other.load_document(load_sri(path))
        self.assertEqual(other.toPlainText(), "Heading\nBody text")
        self.assertEqual(all_style_names(other.document())[0], "Title")
        self.assertEqual(other.page_layout.size_name, "Letter")
        self.assertFalse(other.document().isModified())

    def test_pdf_export_multi_page(self):
        from sris_writer.document import PageLayout
        from sris_writer.printing import export_pdf
        editor = self.make_editor("\n".join(f"Line {i}" for i in range(300)))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "out.pdf"
            export_pdf(editor.document(), PageLayout.named("A4"), path, "Test")
            data = path.read_bytes()
        self.assertTrue(data.startswith(b"%PDF"))
        self.assertGreater(data.count(b"/Type /Page\n") + data.count(b"/Type /Page "), 1)

    def test_pdf_export_unwritable_location(self):
        from sris_writer.document import PageLayout
        from sris_writer.printing import export_pdf
        editor = self.make_editor()
        with self.assertRaises(OSError):
            export_pdf(editor.document(), PageLayout(), Path("/nonexistent-dir/x.pdf"))

    def test_zoom_steps(self):
        editor = self.make_editor()
        editor.zoom_step(1)
        self.assertEqual(editor.zoom, 125)
        editor.set_zoom(100)
        editor.zoom_step(-1)
        self.assertEqual(editor.zoom, 75)


if __name__ == "__main__":
    unittest.main()
