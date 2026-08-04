"""
P2CS Experiment interfaces.

Defines contracts for experiment scaffold generation plugins.
risk: medium
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from p2cs.contracts import ComponentManifest, ExperimentManifest, SemanticGraph


class IExperimentBuilder(ABC):
    """Generates experiment manifests from components and semantic graph."""

    @abstractmethod
    def build(
        self,
        components: List[ComponentManifest],
        graph: SemanticGraph,
    ) -> List[ExperimentManifest]:
        ...


class IExperimentPlugin(ABC):
    """Plugin hook called after each experiment is generated."""

    @abstractmethod
    def on_experiment_generated(self, manifest: ExperimentManifest) -> ExperimentManifest:
        ...
