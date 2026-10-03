# The `.sri` file format (version 1)

A `.sri` file is a ZIP archive:

```
document.sri
├── manifest.json    {"application": "Sri's Office", "format": "sri", "version": 1}
├── document.html    rich text body (UTF-8)
├── metadata.json    title, author, language, created, modified, extra{}
├── styles.json      {"version": 1, "paragraph_styles": [...], "page": {...}}
└── media/           embedded resources (reserved for images)
```

Rules
* Readers must reject `version` greater than the one they understand
  (`UnsupportedVersionError`), and reject missing/invalid members (`CorruptDocumentError`).
* Unknown keys in JSON files are ignored, so minor additions do not need a version bump.
* Writers save to `name.sri.tmp` and rename, so a failed save never destroys the original.
* Future directories: `fonts/`, `bibliography/`, `settings/`.
* `paragraph_styles` lists the style name of each paragraph in order; if the paragraph count
  after parsing the HTML differs, the list is ignored and headings are inferred from `<h1>-<h4>`.
