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

## Planned Components

| Component | Status |
|---|---|
| Submission template (`research/templates/paper-template.md`) | ✅ Done |
| RAIP envelope generator (CLI) | 🔲 Planned |
| Metadata extractor (frontmatter → search index) | 🔲 Planned |
| DOI assignment service | 🔲 Planned |
| CI publication gate (conformance + schema checks) | 🔲 Planned |

## Contributing

See the root [CONTRIBUTING.md](../../CONTRIBUTING.md) for general guidelines, and [docs/PLATFORM_ENHANCEMENTS.md](../../docs/PLATFORM_ENHANCEMENTS.md) for the full engineering backlog.