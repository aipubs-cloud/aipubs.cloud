# P2CS Roadmap

**Milestone: P2CS Foundation (v0.1.0-alpha)**

This roadmap establishes a stable, incrementally deliverable path from infrastructure contracts through fully autonomous research compilation.

---

## Phase 1 — Infrastructure and Contracts *(current)*

**Goal:** Stable data contracts, directory structure, AIOL specs, and CI pipeline before any extraction model is written.

- [x] P2CS directory structure (`p2cs/`, `.aiol/`, `generated/`)
- [x] Typed data contracts (`p2cs/contracts.py`)
- [x] JSON Schemas for all artifact types (9 schemas)
- [x] AIOL module specifications for all subsystems (9 modules)
- [x] Plugin registry and descriptor schema
- [x] Cross-stage contracts index
- [x] GitHub Actions pipeline (discovery → parse → analysis → synthesis → validation → publish)
- [x] DefaultProvenanceEngine (stdlib only, RAIP-compatible)
- [x] DefaultIntegrityHasher
- [x] Registry interfaces (`IRegistry`, `IRegistryStore`)
- [x] Orchestration interfaces (`IPipelineStage`, `IPipelineOrchestrator`)
- [x] Unit + contract tests (31 tests, all passing)
- [x] Architecture documentation
- [x] Contributor guide

---

## Phase 2 — Publication Parsing

**Goal:** Real parsers for each supported format, replacing the skeleton scanner.

- [ ] Markdown parser (`IPublicationParser` for markdown)
- [ ] Equation extractor (LaTeX math blocks)
- [ ] Algorithm extractor (pseudocode blocks)
- [ ] Figure and table extractor
- [ ] Reference extractor (BibTeX, inline citations)
- [ ] PDF text extraction adapter
- [ ] HTML parser adapter
- [ ] DOCX adapter
- [ ] Integration tests against real publications in `research/papers/`

---

## Phase 3 — Semantic Graph Generation

**Goal:** Build knowledge graphs from parsed publications using plugin-driven extraction.

- [ ] First `INodeExtractor` plugin (keyword/concept extraction)
- [ ] First `IRelationExtractor` plugin (co-occurrence relations)
- [ ] Graph serialisation to `generated/semantic/`
- [ ] Graph visualisation artifact (DOT or JSON-LD)
- [ ] Cross-publication deduplication (shared concept nodes)
- [ ] Integration tests against sample publications

---

## Phase 4 — Code Synthesis

**Goal:** Generate real, runnable code components from the semantic graph.

- [ ] First `ISynthesisEngine` plugin (Python code generation)
- [ ] Python `ILanguageAdapter`
- [ ] TypeScript `ILanguageAdapter`
- [ ] Component scaffold includes working tests (pytest / jest)
- [ ] Confidence threshold gating (no output below threshold)
- [ ] Human-review PR gate enforced in CI
- [ ] Rust `ILanguageAdapter`
- [ ] Go `ILanguageAdapter`

---

## Phase 5 — Experiment Generation

**Goal:** Generate reproducible experiments from synthesised components.

- [ ] First `IExperimentBuilder` plugin
- [ ] Jupyter notebook scaffold generation
- [ ] `config.yaml` + `benchmark.py` + `README.md` template
- [ ] Docker image metadata in `ExperimentManifest`
- [ ] Random seed enforcement
- [ ] Integration with `research/experiments/`

---

## Phase 6 — Validation and Benchmarking

**Goal:** Automated correctness and performance validation of generated artifacts.

- [ ] `IValidator` implementation using jsonschema + pytest runner
- [ ] `IBenchmarkEngine` implementation (Python timeit / Rust criterion)
- [ ] `BenchmarkReport` persistence to `generated/benchmarks/`
- [ ] CI gate: block publish if validation fails
- [ ] Accuracy metric hooks for ML components
- [ ] Convergence metric hooks for optimisation algorithms

---

## Phase 7 — Autonomous Refinement

**Goal:** Feedback loop from benchmark results back to synthesis.

- [ ] Benchmark delta comparison (regression detection)
- [ ] Re-synthesis trigger when benchmark delta exceeds threshold
- [ ] Cross-publication improvement suggestions (newer method supersedes older)
- [ ] Duplicate component detection and merge proposal
- [ ] Semantic versioning automation (`CHANGELOG.md` per component)

---

## Phase 8 — Continuous Research Compilation

**Goal:** Fully autonomous, continuously enriching knowledge base.

- [ ] Nightly rescan of all publications
- [ ] Research graph update (`publications → concepts → components → experiments`)
- [ ] Interactive demos (Streamlit / Gradio) for high-confidence components
- [ ] Educational artifact generation (tutorials, API docs, quizzes)
- [ ] Formal methods integration (theorem verification stubs)
- [ ] Streamlit/Gradio demo hosting via Cloudflare Pages
- [ ] Public registry API endpoint

---

## Long-Term Vision

AIPubs.cloud evolves into an **autonomous research compiler**:

- Publications become executable knowledge
- AIOL modules become reusable, versioned implementations
- Experiments become reproducible benchmark suites
- RAIP provides the trust layer linking every generated artifact to its scholarly source

Every future synthesis engine — code generation, theorem verification, dataset construction, simulation, formal methods, educational content — integrates through the same stable P2CS architecture.
