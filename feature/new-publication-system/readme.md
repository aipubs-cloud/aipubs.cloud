# New Publication System

This feature branch tracks work on the next-generation publication pipeline for AIPubs.cloud.

## Overview

The new publication system replaces the current static mock data with a Git-backed, RAIP-verified publishing workflow where every paper, dataset, and code artifact carries a cryptographic evidence envelope.

## Goals

- **Git-native submissions** — authors fork the repo, write in Markdown, and open a PR
- **RAIP envelope generation** — ACF + ALC + SIGN produced automatically on merge
- **Structured metadata** — YAML frontmatter drives search indexing, DOI assignment, and citation export
- **Peer review via GitHub** — open review comments in pull requests with timestamped history
- **Dataset linking** — datasets in `research/datasets/` are versioned and fingerprinted alongside papers

## Components

| Component | Status |
|---|---|
| Submission template (`research/templates/paper-template.md`) | ✅ Done |
| RAIP v1.0 core library (`raip/core/`) | ✅ Done |
| RAIP CLI (`raip publish/verify/inspect/sign/revoke/export/history`) | ✅ Done |
| RAIP schemas (`raip/schemas/raip.schema.json`) | ✅ Done |
| RAIP conformance vectors TV-008..011 | ✅ Done |
| Paper metadata schema (`schemas/paper.schema.json`) | ✅ Done |
| Metadata extractor → search index (`scripts/generate_papers_index.py`) | ✅ Done |
| CI publication gate (`validate-publication.yml`) | ✅ Done |
| CI search index generator (`generate-index.yml`) | ✅ Done |
| RAIP Media Intelligence Suite MVP (`raip-media/`) | ✅ Done |
| Console TUI dashboard (`raip-media dashboard`) | ✅ Done |
| DOI assignment service | 🔲 Planned |
| Author profiles (`authors/`) | 🔲 Planned |
| Peer review platform | 🔲 Planned |

## Quick Start

### Publish a paper with RAIP

```bash
# Install the RAIP CLI
pip install -e .

# Initialise RAIP keypair in your working directory
raip init

# Publish a paper (generates paper.raip.json)
raip publish research/papers/my-paper.md

# Verify integrity
raip verify research/papers/my-paper.md

# Inspect the envelope
raip inspect research/papers/my-paper.md

# Export citation
raip export research/papers/my-paper.md --format bibtex
```

### Process media with RAIP Media Suite

```bash
# Install raip-media
pip install -e ./raip-media

# Transcribe and generate provenance
raip-media transcribe lecture.mp4

# Show live dashboard
raip-media dashboard lecture/

# Verify provenance
raip-media verify lecture/manifest.json

# Export formats
raip-media export lecture/ --all
```

## Contributing

See the root [CONTRIBUTING.md](../../CONTRIBUTING.md) for general guidelines, and [docs/PLATFORM_ENHANCEMENTS.md](../../docs/PLATFORM_ENHANCEMENTS.md) for the full engineering backlog.
