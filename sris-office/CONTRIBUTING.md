# Contributing

1. Keep layers separate: UI -> editor/commands -> document model -> format adapter -> file.
2. No Qt imports in `document.py`, `formats/`, `settings.py`, `recovery.py`, `errors.py`.
3. Add tests for behaviour you change (`./run.sh --test`). Don't claim a feature is done untested.
4. Label unfinished features `PLANNED`; never fake them with plain text.
5. Small, meaningful commits; semantic versioning.
