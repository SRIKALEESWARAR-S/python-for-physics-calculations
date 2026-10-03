# Architecture

```
UI (main_window, widgets, dialogs)
  -> Controller / Commands (controller.py, commands.py, styles.py)
    -> Editor widget (editor.py)  <->  Document model (document.py, Qt-free)
      -> Format adapters (formats/)
        -> File
```

* **Document model** (`document.py`): HTML body, metadata, page layout, per-paragraph style
  names, media. No Qt imports, so it is fast to test and format-agnostic.
* **Format adapters** (`formats/`): convert `File <-> Document`. `.sri` and HTML work.
  DOCX/ODT adapters are stubs raising `FeatureNotAvailableError` ("PLANNED"). The editor
  never talks to a file format directly.
* **Editor** (`editor.py`): the only place that converts `Document <-> QTextDocument`
  (`load_document`, `to_document`).
* **Semantic styles** (`styles.py`): each paragraph carries a style name in a custom block
  property; headings also use Qt heading levels. Names are saved in `styles.json`, so a future
  table of contents reads real structure, not font sizes.
* **Controller** (`controller.py`): file lifecycle, unsaved-change prompts, error dialogs,
  autosave/recovery. Errors are translated by `errors.py` into "Reason / Suggested action".
* **Output** (`printing.py`): PDF/print use a clone of the document with page margins taken
  from the device, so output is independent of the on-screen page drawing.
* **Spell checking** (`spellcheck.py`): provider protocol and registry only (PLANNED).

## Where future features plug in

| Feature | Plug-in point |
|---|---|
| DOCX / ODT | New adapters in `formats/` mapping to/from `Document` |
| Images | `Document.media` + `media/` in the container (already reserved) |
| Headers/footers, page numbers | New fields on `Document`/`PageLayout`, rendered in `printing.py` |
| TOC, captions, cross refs | Read `paragraph_styles` / heading structure |
| Spell check | Register a `SpellCheckProvider` per language (Tamil included) |
| Other apps (Calc, Impress, Draw) | Sibling packages next to `sris_writer/`; shared code can move to a `sris_core/` package |
