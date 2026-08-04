"""
P2CS Semantic interfaces.

Defines contracts for knowledge graph construction and enrichment plugins.
risk: medium
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from p2cs.contracts import (
    GraphEdge,
    GraphNode,
    PublicationManifest,
    SemanticGraph,
)


class ISemanticGraphBuilder(ABC):
    """Constructs a SemanticGraph from an enriched PublicationManifest."""

    @abstractmethod
    def build(self, manifest: PublicationManifest) -> SemanticGraph:
        """Return a fully-populated SemanticGraph with provenance."""
        ...


class INodeExtractor(ABC):
    """Extracts typed nodes from publication content."""

    @abstractmethod
    def extract_nodes(self, manifest: PublicationManifest) -> List[GraphNode]:
        ...


class IRelationExtractor(ABC):
    """Infers edges between nodes in the semantic graph."""

    @abstractmethod
    def extract_edges(self, nodes: List[GraphNode], manifest: PublicationManifest) -> List[GraphEdge]:
        ...


class ISemanticPlugin(ABC):
    """Plugin hook called after the semantic graph is created."""

    @abstractmethod
    def on_semantic_graph_created(self, graph: SemanticGraph) -> SemanticGraph:
        """Augment or validate the graph; must return a graph."""
        ...
