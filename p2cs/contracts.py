"""
P2CS contracts — shared data types and provenance structures.

All P2CS subsystems exchange data through these typed dataclasses.
risk: low
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WorkflowContext:
    """Runtime context injected by a GitHub Actions workflow."""
    workflow_id: str
    workflow_version: str
    repository_commit: str
    run_id: str = ""

    def to_dict(self) -> Dict[str, str]:
        return {
            "workflow_id": self.workflow_id,
            "workflow_version": self.workflow_version,
            "repository_commit": self.repository_commit,
            "run_id": self.run_id,
        }


@dataclass
class ProvenanceRecord:
    """Full provenance chain for a P2CS-generated artifact (extends RAIP)."""
    publication_id: str
    publication_version: str
    originating_section: str
    source_hash: str  # sha256:… of the originating publication content
    workflow_id: str
    workflow_version: str
    engine_id: str
    aiol_module_version: str
    generated_at: datetime
    repository_commit: str
    integrity_hash: str = ""  # sha256:… of the artifact content; set after generation

    def compute_integrity(self, content: bytes) -> "ProvenanceRecord":
        digest = "sha256:" + hashlib.sha256(content).hexdigest()
        return ProvenanceRecord(
            publication_id=self.publication_id,
            publication_version=self.publication_version,
            originating_section=self.originating_section,
            source_hash=self.source_hash,
            workflow_id=self.workflow_id,
            workflow_version=self.workflow_version,
            engine_id=self.engine_id,
            aiol_module_version=self.aiol_module_version,
            generated_at=self.generated_at,
            repository_commit=self.repository_commit,
            integrity_hash=digest,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "publication_id": self.publication_id,
            "publication_version": self.publication_version,
            "originating_section": self.originating_section,
            "source_hash": self.source_hash,
            "workflow_id": self.workflow_id,
            "workflow_version": self.workflow_version,
            "engine_id": self.engine_id,
            "aiol_module_version": self.aiol_module_version,
            "generated_at": self.generated_at.isoformat(),
            "repository_commit": self.repository_commit,
            "integrity_hash": self.integrity_hash,
        }


# ---------------------------------------------------------------------------
# Publication
# ---------------------------------------------------------------------------

SupportedFormat = Literal["markdown", "pdf", "html", "latex", "docx"]
SectionType = Literal[
    "abstract", "introduction", "method", "result",
    "discussion", "conclusion", "reference", "appendix", "other"
]


@dataclass
class PublicationSection:
    id: str
    type: SectionType
    title: str = ""
    content: str = ""
    content_hash: str = ""


@dataclass
class PublicationManifest:
    """Stable artifact exchanged between Discovery and Parser stages."""
    schema_version: str = "1.0.0"
    publication_id: str = ""
    title: str = ""
    authors: List[Dict[str, str]] = field(default_factory=list)
    abstract: str = ""
    keywords: List[str] = field(default_factory=list)
    source_format: SupportedFormat = "markdown"
    source_path: str = ""
    source_hash: str = ""
    ingested_at: Optional[datetime] = None
    raip_envelope: str = ""
    sections: List[PublicationSection] = field(default_factory=list)
    equations: List[Dict[str, str]] = field(default_factory=list)
    algorithms: List[Dict[str, str]] = field(default_factory=list)
    figures: List[Dict[str, str]] = field(default_factory=list)
    references: List[Dict[str, str]] = field(default_factory=list)
    provenance: Optional[ProvenanceRecord] = None

    def set_ingested_now(self) -> None:
        self.ingested_at = datetime.now(tz=timezone.utc)


# ---------------------------------------------------------------------------
# Semantic Graph
# ---------------------------------------------------------------------------

NodeType = Literal[
    "concept", "method", "algorithm", "variable",
    "dataset", "model", "equation", "framework", "protocol", "api"
]
EdgeRelation = Literal[
    "uses", "implements", "extends", "depends_on",
    "produces", "references", "equivalent_to", "derived_from"
]


@dataclass
class GraphNode:
    id: str
    type: NodeType
    label: str
    description: str = ""
    source_section: str = ""
    confidence: float = 1.0
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    id: str
    source: str
    target: str
    relation: EdgeRelation
    weight: float = 1.0


@dataclass
class SemanticGraph:
    schema_version: str = "1.0.0"
    publication_id: str = ""
    generated_at: Optional[datetime] = None
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)
    provenance: Optional[ProvenanceRecord] = None


# ---------------------------------------------------------------------------
# Component
# ---------------------------------------------------------------------------

SupportedLanguage = Literal["python", "rust", "typescript", "go", "cpp", "java", "other"]


@dataclass
class ComponentManifest:
    schema_version: str = "1.0.0"
    component_id: str = ""
    name: str = ""
    version: str = "0.1.0"
    description: str = ""
    language: SupportedLanguage = "python"
    license: str = "Apache-2.0"
    interfaces: List[Dict[str, str]] = field(default_factory=list)
    dependencies: List[Dict[str, str]] = field(default_factory=list)
    artifacts: Dict[str, str] = field(default_factory=dict)
    quality: Dict[str, Any] = field(default_factory=dict)
    provenance: Optional[ProvenanceRecord] = None


# ---------------------------------------------------------------------------
# Experiment
# ---------------------------------------------------------------------------

ExperimentType = Literal[
    "reproduction", "benchmark", "ablation",
    "baseline_comparison", "visualization", "other"
]


@dataclass
class ExperimentManifest:
    schema_version: str = "1.0.0"
    experiment_id: str = ""
    name: str = ""
    version: str = "0.1.0"
    description: str = ""
    type: ExperimentType = "reproduction"
    entrypoint: str = ""
    runtime: str = "python"
    runtime_version: str = ""
    random_seed: Optional[int] = None
    deterministic: bool = False
    related_components: List[str] = field(default_factory=list)
    datasets: List[str] = field(default_factory=list)
    benchmark_hooks: List[Dict[str, str]] = field(default_factory=list)
    provenance: Optional[ProvenanceRecord] = None


# ---------------------------------------------------------------------------
# Benchmark
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkMetric:
    name: str
    value: float
    unit: str
    lower_is_better: bool = True
    baseline: Optional[float] = None
    delta_percent: Optional[float] = None


@dataclass
class BenchmarkReport:
    schema_version: str = "1.0.0"
    benchmark_id: str = ""
    component_or_experiment_id: str = ""
    run_at: Optional[datetime] = None
    metrics: List[BenchmarkMetric] = field(default_factory=list)
    passed: bool = False
    notes: str = ""
    provenance: Optional[ProvenanceRecord] = None


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

RegistryEntryType = Literal[
    "library", "aiol_module", "experiment", "dataset",
    "benchmark", "prompt", "documentation"
]
RegistryEntryStatus = Literal["active", "deprecated", "experimental", "archived"]


@dataclass
class RegistryEntry:
    schema_version: str = "1.0.0"
    entry_id: str = ""
    type: RegistryEntryType = "library"
    name: str = ""
    version: str = ""
    description: str = ""
    language_targets: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    path: str = ""
    manifest_path: str = ""
    dependencies: List[Dict[str, str]] = field(default_factory=list)
    status: RegistryEntryStatus = "experimental"
    provenance: Optional[ProvenanceRecord] = None
