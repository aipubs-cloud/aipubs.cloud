"""
P2CS Validation interfaces.

Defines contracts for artifact validators and schema checkers.
risk: low
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class ValidationReport:
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class IValidator(ABC):
    """Validates a P2CS artifact holistically."""

    @abstractmethod
    def validate(self, artifact: Any) -> ValidationReport:
        ...


class ISchemaValidator(ABC):
    """Validates a dict/object against a JSON Schema."""

    @abstractmethod
    def validate_against_schema(self, data: Any, schema_id: str) -> ValidationReport:
        ...


class IValidationPlugin(ABC):
    """Plugin hook called after validation completes."""

    @abstractmethod
    def on_validation_completed(self, report: ValidationReport, artifact: Any) -> ValidationReport:
        ...
