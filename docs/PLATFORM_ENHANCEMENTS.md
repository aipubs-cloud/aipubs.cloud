# AIPubs.cloud enhancement backlog

This backlog converts the RAIP platform analysis into product-oriented upgrades for the current static research portal and the future verified publishing platform.

## Immediate interface upgrades

1. **RAIP trust section on the homepage.** Explain artifact identity, lifecycle history, attestation, and verifier reports in language that researchers can understand.
2. **Publication provenance panels.** Show verification status, ACF, ALC, signer, and downloadable evidence on each paper page.
3. **Trust center route.** Add an educational view for RAIP, conformance vectors, release gates, and the implementation roadmap.
4. **Verified badges in listings.** Surface provenance status in search results so readers can prioritize evidence-backed publications.
5. **Submission guidance.** Extend publishing instructions to mention RAIP envelope generation, datasets, code, and verifier reports.

## Near-term engineering upgrades

1. **RAIP full-envelope generator.** Generate RAIP-TV-008 through RAIP-TV-011 from a single valid baseline envelope and downstream mutations.
2. **Diagnostic verifier.** Return structured layer results for ACF, ALC, and SIGN failures.
3. **Artifact registration service.** Add endpoints for registering, verifying, and retrieving envelopes and verifier reports.
4. **Evidence storage model.** Store artifact bytes or encrypted references separately from public envelopes and verification reports.
5. **CI publication gate.** Block releases when conformance vectors, schema validation, or publication evidence checks fail.

## Strategic research upgrades

1. **Semantic ACF profile.** Add optional semantic similarity fingerprints as supplementary evidence for revisions and duplicate detection.
2. **DAG lifecycle profile.** Support branching and merging research lineage for datasets, experiments, and model training runs.
3. **Zero-knowledge proof profile.** Allow private claims about embargoed or sensitive artifacts.
4. **Continuous model provenance.** Track model checkpoints, training events, evaluation results, and release attestations.
5. **Verifiable research graph.** Connect papers, code, datasets, prompts, models, reviewers, and citations through RAIP evidence.
