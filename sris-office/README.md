# Sri's Office

A lightweight, open-source Linux office suite beginning with **Sri's Writer**.

> Make writing a document on Linux feel simple again.

## What it is and why

Sri's Writer aims for the familiarity of a classic ribbon word processor without the
complexity of a full office suite. It is a native Qt desktop application (Python +
PySide6), not Electron and not a web page. Long-term it is meant to be especially
useful for theses, reports and scientific writing.

## Status: version 0.1.0 (early)

Feature status is labelled honestly. **Working** means implemented; **PLANNED** means
designed for but not built.

| Area | Status |
|---|---|
| Main window, ribbon-style tabs, status bar | Working |
| Rich text: font, size, bold/italic/underline/strike, colour, highlight | Working |
| Alignment, indent, line spacing, bullet/numbered/nested lists | Working |
| Styles: Normal, Title, Subtitle, Heading 1-4, Quote, Caption (stored semantically) | Working |
| New / Open / Save / Save As / Close / Recent documents | Working |
| Native `.sri` format (versioned ZIP, rejects newer versions) | Working |
| Unsaved-change protection | Working |
| Find, Find next/previous, Replace, Replace all | Working |
| Word / character / approximate page count | Working |
| Zoom 50-200 % (Ctrl+wheel, Ctrl +/-/0) | Working (see limits) |
| PDF export, HTML export, Print, Print preview | Working |
| Light / Dark / System theme | Working |
| Autosave and crash recovery (never overwrites the original) | Working, basic |
| Page size / orientation / margins | Working |
| DOCX and ODT import/export | PLANNED (adapter stubs only) |
| Images, tables, headers/footers, page numbers | PLANNED |
| TOC, captions, footnotes, bibliography, equations | PLANNED |
| Spell checking (provider architecture exists) | PLANNED |
| Thesis template, `.deb` / AppImage / Flatpak | PLANNED |

### Known limits of 0.1.0

* **Not yet tested on a real desktop by the author.** The Qt-free core (format,
  settings, recovery, errors) has automated tests that pass. The GUI and the Qt tests
  in `tests/test_formatting.py` were written but could not be executed in the
  environment where the code was generated, so expect some first-run bugs. Please
  report them.
* Page numbers (`Page 1 of N`) are **estimated** from document height; real
  pagination arrives with headers/footers. PDF/print output is paginated correctly by Qt.
* Zoom scales text by changing the layout DPI; images/indent pixel sizes are not scaled.
* Applying a paragraph style resets direct character formatting in that paragraph.

## Installation and running (Linux)

```bash
git clone <repository-url> sris-office
cd sris-office
chmod +x run.sh
./run.sh            # creates .venv, installs PySide6, starts the app
./run.sh file.sri   # open a document
./run.sh --test     # run the tests
```

Requirements: Python 3.10+ and `python3-venv`. On Debian/Ubuntu/Linux Mint:

```bash
sudo apt install python3 python3-venv libxcb-cursor0
```

(`libxcb-cursor0` is needed by Qt 6.5+ on X11.)

## Development

```
sris_writer/
  document.py      Qt-free document model (single source of truth)
  formats/         File <-> Document adapters (.sri, HTML; DOCX/ODT planned)
  editor.py        Page-style editor widget
  commands.py      Formatting commands     styles.py   Built-in styles
  controller.py    New/open/save/export/recovery flow
  main_window.py   Ribbon, menus, status bar
```

Layering: `UI -> Editor/Commands -> Document model -> Format adapter -> File`.
See `ARCHITECTURE.md` and `docs/file-format.md`. Without Qt you can still run
`python -m unittest discover -s tests -t .`.

## Roadmap

See `ROADMAP.md`. Contributions welcome: see `CONTRIBUTING.md`.

## License

Apache License 2.0, see `LICENSE`.
