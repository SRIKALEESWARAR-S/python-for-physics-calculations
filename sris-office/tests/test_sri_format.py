"""Native .sri format: save, load, corruption and version handling (no Qt needed)."""
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from sris_writer.document import Document, Metadata, PageLayout
from sris_writer.formats import CorruptDocumentError, UnsupportedVersionError, read_document, write_document
from sris_writer.formats.sri import FORMAT_VERSION, load_sri, save_sri


class SriFormatTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _sample(self) -> Document:
        return Document(html="<p>Hello ħ ψ(x,t)</p>", metadata=Metadata(title="T", author="Sri"),
                        page=PageLayout.named("A5", "landscape"),
                        paragraph_styles=["Title"], media={"fig.png": b"\x89PNG"})

    def test_round_trip(self):
        path = self.dir / "a.sri"
        save_sri(self._sample(), path)
        doc = load_sri(path)
        self.assertEqual(doc.html, "<p>Hello ħ ψ(x,t)</p>")
        self.assertEqual(doc.metadata.title, "T")
        self.assertEqual(doc.metadata.author, "Sri")
        self.assertEqual(doc.page.size_name, "A5")
        self.assertEqual(doc.page.orientation, "landscape")
        self.assertEqual(doc.paragraph_styles, ["Title"])
        self.assertEqual(doc.media, {"fig.png": b"\x89PNG"})
        self.assertEqual(doc.path, path)

    def test_manifest_and_layout(self):
        path = self.dir / "a.sri"
        save_sri(self._sample(), path)
        with zipfile.ZipFile(path) as z:
            names = set(z.namelist())
            manifest = json.loads(z.read("manifest.json"))
        self.assertTrue({"manifest.json", "document.html", "metadata.json", "styles.json",
                         "media/fig.png"} <= names)
        self.assertEqual(manifest, {"application": "Sri's Office", "format": "sri",
                                    "version": FORMAT_VERSION})

    def test_no_temp_file_left_behind(self):
        save_sri(self._sample(), self.dir / "a.sri")
        self.assertEqual([p.name for p in self.dir.iterdir()], ["a.sri"])

    def test_failed_save_keeps_original(self):
        path = self.dir / "a.sri"
        save_sri(self._sample(), path)
        bad = self._sample()
        bad.media["x"] = 12345   # writestr will fail mid-write
        with self.assertRaises(Exception):
            save_sri(bad, path)
        self.assertEqual(load_sri(path).metadata.title, "T")
        self.assertEqual(len(list(self.dir.iterdir())), 1)

    def test_not_a_zip(self):
        path = self.dir / "bad.sri"
        path.write_text("hello")
        with self.assertRaises(CorruptDocumentError):
            load_sri(path)

    def test_truncated_file(self):
        path = self.dir / "a.sri"
        save_sri(self._sample(), path)
        path.write_bytes(path.read_bytes()[:40])
        with self.assertRaises(CorruptDocumentError):
            load_sri(path)

    def test_missing_member(self):
        path = self.dir / "m.sri"
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("manifest.json", json.dumps({"format": "sri", "version": 1}))
        with self.assertRaises(CorruptDocumentError):
            load_sri(path)

    def test_wrong_format_name(self):
        path = self.dir / "w.sri"
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("manifest.json", json.dumps({"format": "other", "version": 1}))
        with self.assertRaises(CorruptDocumentError):
            load_sri(path)

    def test_future_version_rejected(self):
        path = self.dir / "f.sri"
        save_sri(self._sample(), path)
        with zipfile.ZipFile(path) as z:
            members = {n: z.read(n) for n in z.namelist()}
        members["manifest.json"] = json.dumps(
            {"application": "Sri's Office", "format": "sri", "version": FORMAT_VERSION + 1}).encode()
        with zipfile.ZipFile(path, "w") as z:
            for name, blob in members.items():
                z.writestr(name, blob)
        with self.assertRaises(UnsupportedVersionError):
            load_sri(path)

    def test_bad_json_is_corrupt(self):
        path = self.dir / "j.sri"
        save_sri(self._sample(), path)
        with zipfile.ZipFile(path) as z:
            members = {n: z.read(n) for n in z.namelist()}
        members["metadata.json"] = b"{not json"
        with zipfile.ZipFile(path, "w") as z:
            for name, blob in members.items():
                z.writestr(name, blob)
        with self.assertRaises(CorruptDocumentError):
            load_sri(path)

    def test_registry_dispatch_and_html_export(self):
        save_sri(self._sample(), self.dir / "a.sri")
        self.assertEqual(read_document(self.dir / "a.sri").metadata.author, "Sri")
        write_document(self._sample(), self.dir / "a.html")
        text = (self.dir / "a.html").read_text(encoding="utf-8")
        self.assertIn("ψ(x,t)", text)
        self.assertIn("charset", text.lower())

    def test_planned_formats_raise_clearly(self):
        from sris_writer.formats import FeatureNotAvailableError
        with self.assertRaises(FeatureNotAvailableError):
            read_document(self.dir / "x.docx")


if __name__ == "__main__":
    unittest.main()
