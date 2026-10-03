"""Spell-checking provider architecture. PLANNED: no checker is implemented.

Real providers (Hunspell, enchant, a Tamil dictionary...) will implement
``SpellCheckProvider`` and register themselves, so the editor never depends
on one engine or one language.
"""
from __future__ import annotations

from typing import Protocol


class SpellCheckProvider(Protocol):
    language: str

    def is_correct(self, word: str) -> bool: ...
    def suggestions(self, word: str, limit: int = 5) -> list[str]: ...


class SpellCheckRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, SpellCheckProvider] = {}

    def register(self, provider: SpellCheckProvider) -> None:
        self._providers[provider.language] = provider

    def languages(self) -> list[str]:
        return sorted(self._providers)

    def get(self, language: str) -> SpellCheckProvider | None:
        return self._providers.get(language)
