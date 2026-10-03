"""Standard message boxes with the wording required by the spec."""
from __future__ import annotations

from PySide6.QtWidgets import QMessageBox

from ..errors import format_error_message

SAVE, DISCARD, CANCEL = "save", "discard", "cancel"


def confirm_unsaved(parent) -> str:
    box = QMessageBox(QMessageBox.Warning, "Unsaved changes",
                      "This document has unsaved changes.", parent=parent)
    box.setInformativeText("Save changes before closing?")
    save = box.addButton("Save", QMessageBox.AcceptRole)
    discard = box.addButton("Discard", QMessageBox.DestructiveRole)
    box.addButton("Cancel", QMessageBox.RejectRole)
    box.setDefaultButton(save)
    box.exec()
    clicked = box.clickedButton()
    if clicked is save:
        return SAVE
    if clicked is discard:
        return DISCARD
    return CANCEL


def show_error(parent, action: str, exc: BaseException) -> None:
    QMessageBox.critical(parent, "Sri's Writer", format_error_message(action, exc))


def confirm_restore(parent) -> bool:
    box = QMessageBox(QMessageBox.Question, "Recovered document",
                      "Sri's Writer found a recovered document.", parent=parent)
    box.setInformativeText("Restore it?")
    restore = box.addButton("Restore", QMessageBox.AcceptRole)
    box.addButton("Discard", QMessageBox.DestructiveRole)
    box.setDefaultButton(restore)
    box.exec()
    return box.clickedButton() is restore
