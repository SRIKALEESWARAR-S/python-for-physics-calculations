"""Application bootstrap: logging, QApplication, main window."""
from __future__ import annotations

import logging
import logging.handlers
import os
import sys
from pathlib import Path

from . import APP_NAME, __version__

log = logging.getLogger("sris_writer")


def log_directory() -> Path:
    base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return base / "sris-office"


def setup_logging() -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    try:
        directory = log_directory()
        directory.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.handlers.RotatingFileHandler(
            directory / "sris-writer.log", maxBytes=500_000, backupCount=2, encoding="utf-8"))
    except OSError:
        pass   # logging to a file is optional
    logging.basicConfig(level=logging.INFO, handlers=handlers,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def _install_excepthook() -> None:
    def hook(exc_type, exc, tb):
        log.critical("Unhandled exception", exc_info=(exc_type, exc, tb))
        try:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                None, APP_NAME,
                f"{APP_NAME} ran into an unexpected problem.\n\n"
                "Your work is autosaved and can be restored the next time you start the program.\n"
                f"Details were written to {log_directory() / 'sris-writer.log'}.")
        except Exception:
            pass
    sys.excepthook = hook


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv if argv is None else argv)
    setup_logging()
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print("PySide6 is not installed. Run ./run.sh to set up the environment.", file=sys.stderr)
        return 1
    from .main_window import MainWindow
    from .settings import qt_settings_store

    app = QApplication(argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(__version__)
    app.setOrganizationName("Sri's Office")
    app.setDesktopFileName("sris-writer")
    _install_excepthook()

    settings = qt_settings_store()
    window = MainWindow(settings)
    window.apply_theme(str(settings.get("appearance/theme")))
    window.show()
    if len(argv) > 1:
        window.controller.open_path(Path(argv[1]))
    return app.exec()
