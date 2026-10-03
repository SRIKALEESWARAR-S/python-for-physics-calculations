"""Exceptions raised by format adapters. They carry user-presentable text."""
from __future__ import annotations


class FormatError(Exception):
    """Base class for all file-format problems."""

    #: Short, human-friendly suggestion shown in the error dialog.
    suggestion = "Try opening a different file or restoring a backup."


class CorruptDocumentError(FormatError):
    """The file is not a valid document of the expected format."""

    suggestion = "The file may be damaged. Try restoring it from a backup."


class UnsupportedVersionError(FormatError):
    """The file was written by a newer version of Sri's Office."""

    suggestion = "Update Sri's Office to open this file."


class FeatureNotAvailableError(FormatError):
    """The requested format is PLANNED but not implemented yet."""

    suggestion = "Use the native .sri format, or export to PDF or HTML."
