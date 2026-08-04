"""
P2CS Registry interfaces.

Defines the canonical index of all P2CS-generated artifacts.
risk: low
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator, List, Optional

from p2cs.contracts import RegistryEntry, RegistryEntryStatus, RegistryEntryType


class IRegistry(ABC):
    """High-level API for the P2CS component registry."""

    @abstractmethod
    def register(self, entry: RegistryEntry) -> RegistryEntry:
        """Add or update an entry; returns the persisted entry."""
        ...

    @abstractmethod
    def get(self, entry_id: str) -> Optional[RegistryEntry]:
        ...

    @abstractmethod
    def list_by_type(self, entry_type: RegistryEntryType) -> List[RegistryEntry]:
        ...

    @abstractmethod
    def list_by_status(self, status: RegistryEntryStatus) -> List[RegistryEntry]:
        ...

    @abstractmethod
    def all_entries(self) -> Iterator[RegistryEntry]:
        ...


class IRegistryStore(ABC):
    """Low-level persistence backend for registry entries."""

    @abstractmethod
    def save(self, entry: RegistryEntry) -> None:
        ...

    @abstractmethod
    def load(self, entry_id: str) -> Optional[RegistryEntry]:
        ...

    @abstractmethod
    def load_all(self) -> Iterator[RegistryEntry]:
        ...
