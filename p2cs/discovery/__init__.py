"""
P2CS Discovery interfaces.

Defines the contracts that all discovery plugins must implement.
risk: low
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator, List, Optional

from p2cs.contracts import PublicationManifest, SupportedFormat


class IPublicationScanner(ABC):
    """Scans repository paths and yields publication manifests."""

    @abstractmethod
    def scan(
        self,
        paths: List[str],
        formats: Optional[List[SupportedFormat]] = None,
        since_commit: Optional[str] = None,
    ) -> Iterator[PublicationManifest]:
        """Yield one PublicationManifest per discovered publication."""
        ...


class IFormatDetector(ABC):
    """Detects the format of a file at a given path."""

    @abstractmethod
    def detect(self, path: str) -> Optional[SupportedFormat]:
        """Return the detected format or None if unrecognised."""
        ...


class IDiscoveryPlugin(ABC):
    """Plugin hook called after each publication is discovered."""

    @abstractmethod
    def on_publication_discovered(self, manifest: PublicationManifest) -> PublicationManifest:
        """Receive and optionally enrich the manifest; must return a manifest."""
        ...
