"""Turns exceptions into the 'Reason / Suggested action' text users see."""
from __future__ import annotations

import errno

from .formats.errors import FormatError


def describe_error(exc: BaseException) -> tuple[str, str]:
    """Return ``(reason, suggestion)`` for an exception. Never exposes tracebacks."""
    if isinstance(exc, FormatError):
        return str(exc) or "The file format is not supported.", exc.suggestion
    if isinstance(exc, PermissionError):
        return ("Permission denied.",
                "Choose another folder or check file permissions.")
    if isinstance(exc, FileNotFoundError):
        return ("The file or folder does not exist.",
                "Check that the location still exists, or choose another one.")
    if isinstance(exc, OSError):
        if exc.errno == errno.ENOSPC:
            return "There is no space left on the device.", "Free some disk space or choose another drive."
        if exc.errno == errno.EROFS:
            return "The location is read-only.", "Choose a writable folder."
        return (exc.strerror or "A file system error occurred.",
                "Choose another location and try again.")
    return ("An unexpected error occurred. Details were written to the log file.",
            "Try again. If the problem continues, please report it.")


def format_error_message(action: str, exc: BaseException) -> str:
    reason, suggestion = describe_error(exc)
    return (f"Sri's Writer could not {action}.\n\n"
            f"Reason:\n{reason}\n\nSuggested action:\n{suggestion}")
