"""
P2CS Synthesis interfaces.

Defines contracts for synthesis engine plugins.
risk: high  — synthesized code must be human-reviewed before merge.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from p2cs.contracts import ComponentManifest, SemanticGraph, SupportedLanguage


class ISynthesisEngine(ABC):
    """Core interface for a code synthesis engine."""

    @property
    @abstractmethod
    def engine_id(self) -> str:
        """Unique identifier for this engine (e.g. 'openai-codex-v1')."""
        ...

    @property
    @abstractmethod
    def supported_languages(self) -> List[SupportedLanguage]:
        ...

    @abstractmethod
    def synthesize(
        self,
        graph: SemanticGraph,
        language: SupportedLanguage,
        confidence_threshold: float = 0.7,
    ) -> List[ComponentManifest]:
        """Generate components; return empty list if confidence_threshold not met."""
        ...


class ILanguageAdapter(ABC):
    """Translates a generic component spec into language-specific artifacts."""

    @property
    @abstractmethod
    def language(self) -> SupportedLanguage:
        ...

    @abstractmethod
    def render(self, manifest: ComponentManifest) -> str:
        """Return the generated source code as a string."""
        ...


class ISynthesisPlugin(ABC):
    """Plugin hook called when synthesis is requested."""

    @abstractmethod
    def on_synthesis_requested(
        self,
        graph: SemanticGraph,
        language: Optional[SupportedLanguage],
    ) -> List[ComponentManifest]:
        """Plugins may supplement or override the built-in synthesis engine."""
        ...
