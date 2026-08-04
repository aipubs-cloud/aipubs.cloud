# P2CS Architecture

**Publication-to-Code Synthesis (P2CS)** is a core platform subsystem of AIPubs.cloud.  
It transforms scholarly publications into executable, reproducible, provenance-preserving software artifacts.

## Overview

P2CS is organised as a staged pipeline of independent AIOL modules. Each stage:

- validates its incoming artifacts against versioned JSON schemas
- produces signed, provenance-annotated outputs
- publishes artifacts to the next stage via GitHub Actions
- fails independently without corrupting downstream stages

```
publications/
    ↓
[Discovery]  →  PublicationManifest
    ↓
[Parser]     →  enriched PublicationManifest
    ↓
[Semantic]   →  SemanticGraph
    ↓
[Synthesis]  →  ComponentManifest[]
    ↓
[Experiments]→  ExperimentManifest[]
    ↓
[Validation] →  ValidationReport
    ↓
[Benchmark]  →  BenchmarkReport
    ↓
[Provenance] →  ProvenanceManifest
    ↓
[Registry]   →  RegistryEntry[]
    ↓
[Publish]    →  PR for human review
```

## Design Principles

| Principle | Implication |
|-----------|-------------|
| Modular | One AIOL module per stage; single responsibility |
| Event-driven | Stages communicate via typed events and artifact uploads |
| Plugin-first | No extraction model is hardcoded; all synthesis is injected via plugins |
| Language-agnostic | Synthesis targets Python, Rust, TypeScript, Go, C++ via adapter plugins |
| Deterministic | Provenance hashes enable bit-for-bit reproducibility checks |
| Provenance-preserving | Every artifact carries a full RAIP-compatible provenance chain |
| Reproducible | Experiments include seed, Docker image, and Nix flake metadata |
| Versioned | All contracts are semantically versioned at `schema_version: 1.0.0` |
| Extensible | New synthesis engines integrate via `ISynthesisEngine` without touching core |
| Independently testable | Each module exposes stable interfaces testable in isolation |

## Directory Structure

```
.aiol/
    modules/         # AIOL module specifications (YAML)
    registry/        # Module index
    schemas/         # JSON schemas for all P2CS artifacts
    plugins/         # Plugin registry and descriptors
    contracts/       # Cross-stage contract index

p2cs/
    contracts.py     # Shared Python dataclasses (stable API)
    discovery/       # IPublicationScanner, IFormatDetector
    parsing/         # IPublicationParser, IEquationExtractor
    semantic/        # ISemanticGraphBuilder, INodeExtractor
    synthesis/       # ISynthesisEngine, ILanguageAdapter
    experiments/     # IExperimentBuilder
    validation/      # IValidator, ISchemaValidator
    provenance/      # IProvenanceEngine, DefaultProvenanceEngine
    registry/        # IRegistry, IRegistryStore
    orchestration/   # IPipelineStage, IPipelineOrchestrator
    tests/           # Unit + contract tests

generated/
    manifests/       # PublicationManifest outputs + registry index
    semantic/        # SemanticGraph outputs
    components/      # Component scaffolds
    experiments/     # Experiment scaffolds
    benchmarks/      # BenchmarkReport outputs
    provenance/      # ProvenanceManifest outputs

.github/workflows/
    p2cs-discovery.yml
    p2cs-parse.yml
    p2cs-analysis.yml
    p2cs-synthesis.yml
    p2cs-validation.yml
    p2cs-publish.yml
```

## AIOL Integration

Every P2CS stage is specified as an AIOL module in `.aiol/modules/`. The module spec defines:

- **lifecycle** — state machine for the stage
- **inputs / outputs** — typed contracts consumed and produced
- **events** — emitted events and their payload types
- **interfaces** — Python ABCs the stage implements
- **capabilities** — declared required capabilities
- **plugin_interfaces** — extension points for synthesis engines

## Provenance Model

P2CS extends RAIP. Every artifact receives a `ProvenanceRecord` containing:

- `publication_id` / `publication_version` — originating publication
- `originating_section` — section that sourced the extraction
- `source_hash` — SHA-256 of the publication content
- `workflow_id` / `workflow_version` — producing GitHub Actions workflow
- `engine_id` / `aiol_module_version` — synthesis engine that generated the artifact
- `generated_at` — UTC ISO-8601 timestamp
- `repository_commit` — git SHA of the repository at generation time
- `integrity_hash` — SHA-256 of the artifact content (tamper-evident)

## Plugin Lifecycle

Plugins are discovered from `.aiol/plugins/registry.yml`. Each plugin declares which lifecycle events it handles via a `PluginDescriptor`. No imports are hardcoded.

Lifecycle events:
1. `publication.discovered`
2. `publication.parsed`
3. `semantic_graph.created`
4. `synthesis.requested`
5. `experiment.generated`
6. `validation.completed`
7. `benchmark.completed`
8. `artifact.published`

## Workflow Orchestration

Each GitHub Actions workflow stage:

1. Downloads the previous stage's artifact by run ID
2. Validates incoming artifacts against JSON schemas
3. Executes its stage logic
4. Attaches provenance to all outputs
5. Uploads outputs as a named artifact
6. Fails independently (no cascading failures)

The Publish workflow opens a **draft PR** for human review before any generated code is merged.

## Extension Guide

To add a new synthesis engine:

1. Implement `ISynthesisEngine` from `p2cs.synthesis`
2. Create a `PluginDescriptor` JSON file in `.aiol/plugins/`
3. Register it in `.aiol/plugins/registry.yml`
4. The engine will be discovered automatically at runtime

To add a new language target:

1. Implement `ILanguageAdapter` from `p2cs.synthesis`
2. Register the adapter via a plugin descriptor

See [contributor-guide.md](contributor-guide.md) for full details.
