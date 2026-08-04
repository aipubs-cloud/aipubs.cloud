"""
P2CS Orchestration interfaces.

Defines contracts for pipeline stage coordination.
risk: low
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StageResult:
    stage_id: str
    success: bool
    outputs: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    artifact_paths: List[str] = field(default_factory=list)


class IPipelineStage(ABC):
    """A single orchestrated stage in the P2CS pipeline."""

    @property
    @abstractmethod
    def stage_id(self) -> str:
        ...

    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> StageResult:
        """Execute the stage and return a result. Must not raise on failure."""
        ...

    @abstractmethod
    def validate_inputs(self, inputs: Dict[str, Any]) -> List[str]:
        """Return a list of validation error messages (empty = valid)."""
        ...


class IPipelineOrchestrator(ABC):
    """Coordinates sequential or parallel execution of pipeline stages."""

    @abstractmethod
    def register_stage(self, stage: IPipelineStage) -> None:
        ...

    @abstractmethod
    def run(self, initial_inputs: Dict[str, Any]) -> List[StageResult]:
        """Execute all registered stages and return ordered results."""
        ...
