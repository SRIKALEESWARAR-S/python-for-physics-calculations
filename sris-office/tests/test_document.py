"""Model, metadata, settings, recent documents, recovery and error text (no Qt needed)."""
import os
import tempfile
import unittest
from pathlib import Path

from sris_writer.document import Document, Metadata, PageLayout
from sris_writer.errors import describe_error, format_error_message
from sris_writer.formats.errors import CorruptDocumentError
from sris_writer.recovery import RecoveryManager
from sris_writer.settings import MemoryBackend, RecentDocuments, SettingsStore


class ModelTests(unittest.TestCase):
    def test_page_orientation(self):
        layout = PageLayout.named("A4", "landscape")
        self.assertEqual(layout.effective_size_mm, (297.0, 210.0))
        self.assertAlmostEqual(layout.text_width_mm, 297 - 50.8)

    def test_from_dict_tolerates_garbage(self):
        layout = PageLayout.from_dict({"width_mm": "oops", "orientation": "sideways", "bogus": 1})
        self.assertEqual(layout.width_mm, 210.0)
        self.assertEqual(layout.orientation, "portrait")

    def test_metadata_touch_and_defaults(self):
        meta = Metadata(title="x")
        before = meta.modified
        meta.touch()
        self.assertGreaterEqual(meta.modified, before)
        self.assertEqual(Metadata.from_dict({"title": 5}).title, "")

    def test_display_name(self):
        self.assertEqual(Document().display_name, "Untitled")
        self.assertEqual(Document(path=Path("/a/Thesis.sri")).display_name, "Thesis.sri")


class SettingsTests(unittest.TestCase):
    def test_defaults_and_roundtrip(self):
        store = SettingsStore(MemoryBackend())
        self.assertEqual(store.get("appearance/theme"), "light")
        store.set("appearance/theme", "dark")
        self.assertEqual(store.get("appearance/theme"), "dark")

    def test_corrupt_value_falls_back(self):
        backend = MemoryBackend()
        backend.setValue("view/zoom", "{broken")
        self.assertEqual(SettingsStore(backend).get("view/zoom"), 100)

    def test_recent_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = []
            for name in ("a.sri", "b.sri", "c.sri"):
                f = Path(tmp) / name
                f.write_text("x")
                files.append(f)
            recent = RecentDocuments(SettingsStore(MemoryBackend()), limit=2)
            for f in files:
                recent.add(f)
            self.assertEqual([p.name for p in recent.existing()], ["c.sri", "b.sri"])
            recent.add(files[1])
            self.assertEqual([p.name for p in recent.existing()], ["b.sri", "c.sri"])
            files[1].unlink()    # missing files vanish gracefully
            self.assertEqual([p.name for p in recent.existing()], ["c.sri"])


class RecoveryTests(unittest.TestCase):
    def test_crash_recovery_cycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            dead = RecoveryManager(Path(tmp), pid=2 ** 22 + 12345)   # a pid that is not running
            doc = Document(html="<p>draft</p>", path=Path("/home/x/Thesis.sri"))
            doc.metadata.title = "Draft"
            dead.write(doc)
            self.assertIsNone(doc.metadata.extra.get("recovery_original_path"))  # caller's doc untouched
            live = RecoveryManager(Path(tmp))
            entries = live.pending()
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].original_path, "/home/x/Thesis.sri")
            restored = live.load(entries[0])
            self.assertIsNone(restored.path)           # never silently overwrite the original
            self.assertEqual(restored.html, "<p>draft</p>")
            live.discard(entries[0])
            self.assertEqual(live.pending(), [])

    def test_running_session_not_offered(self):
        with tempfile.TemporaryDirectory() as tmp:
            other = RecoveryManager(Path(tmp), pid=os.getpid())
            other.write(Document(html="x"))
            self.assertEqual(RecoveryManager(Path(tmp)).pending(), [])

    def test_unreadable_recovery_file_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            junk = Path(tmp) / f"recovery-{2 ** 22 + 99}-abcd.sri"
            junk.write_text("junk")
            self.assertEqual(RecoveryManager(Path(tmp)).pending(), [])
            self.assertFalse(junk.exists())


class ErrorTextTests(unittest.TestCase):
    def test_permission_denied(self):
        reason, suggestion = describe_error(PermissionError())
        self.assertEqual(reason, "Permission denied.")
        self.assertIn("another folder", suggestion)

    def test_message_shape_and_no_traceback(self):
        text = format_error_message("save this document", PermissionError())
        self.assertTrue(text.startswith("Sri's Writer could not save this document."))
        self.assertIn("Reason:", text)
        self.assertIn("Suggested action:", text)
        self.assertNotIn("Traceback", text)

    def test_format_error_and_unexpected(self):
        self.assertIn("damaged", describe_error(CorruptDocumentError("bad"))[1])
        self.assertIn("unexpected", describe_error(RuntimeError("boom"))[0])
        self.assertNotIn("boom", describe_error(RuntimeError("boom"))[0])


if __name__ == "__main__":
    unittest.main()
