"""
P2CS Parsing interfaces.

Defines contracts for format-specific parsers and enrichment plugins.
risk: low
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from p2cs.contracts import PublicationManifest


class IPublicationParser(ABC):
    """Parses a raw publication file into a structured PublicationManifest."""

    @abstractmethod
    def parse(self, manifest: PublicationManifest) -> PublicationManifest:
        """Read source_path, populate all structured fields, return enriched manifest."""
        ...

    @property
    @abstractmethod
    def supported_format(self) -> str:
        """Return the format this parser handles (e.g. 'markdown')."""
        ...


class IEquationExtractor(ABC):
    """Extracts equations from raw publication text."""

    @abstractmethod
    def extract(self, content: str) -> list:
        """Return a list of equation dicts with id, content, and label."""
        ...


class IAlgorithmExtractor(ABC):
    """Extracts algorithm descriptions from raw publication text."""

    @abstractmethod
    def extract(self, content: str) -> list:
        """Return a list of algorithm dicts with id, name, and pseudocode."""
        ...


class IParserPlugin(ABC):
    """Plugin hook called after each publication is parsed."""

    @abstractmethod
    def on_publication_parsed(self, manifest: PublicationManifest) -> PublicationManifest:
        """Receive the parsed manifest, optionally enrich it, and return it."""
        ...
