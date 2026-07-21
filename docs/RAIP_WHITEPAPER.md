# RAIP: Research Artifact Integrity Protocol

## A cryptographic provenance framework for AI-native publishing

**Version:** 1.0 draft  
**Platform target:** AIPubs.cloud  
**Primary objective:** turn research uploads into independently verifiable evidence objects.

## Abstract

Modern research publishing is shifting from static manuscripts toward AI-assisted papers, datasets, code repositories, model checkpoints, simulations, prompts, generated outputs, and continuously revised computational workflows. Conventional publishing platforms can host those materials, but they rarely prove exactly what was submitted, how it changed, which evidence was reviewed, and who attested to the final state.

The Research Artifact Integrity Protocol (RAIP) is proposed as the provenance layer for AIPubs.cloud. RAIP combines deterministic artifact identity, lifecycle history, and cryptographic attestation so that every accepted research object can carry a machine-verifiable evidence envelope.

The core chain is:

```text
Artifact bytes
  -> Artifact Content Fingerprint (ACF)
  -> Artifact Lifecycle Chain (ALC)
  -> RAIP-SIGN attestation
  -> verifier report
  -> published evidence record
```

RAIP does not attempt to decide whether a scientific claim is true. Instead, it establishes whether the artifact, history, signatures, and verification transcript match the evidence presented by the author or platform.

## 1. Problem statement

AI-native research platforms need to answer questions that traditional publishing workflows leave ambiguous:

- Is this PDF, dataset, model, or code archive exactly the artifact that was reviewed?
- Which lifecycle events led from draft to published release?
- Did a human researcher, reviewer, lab, or automated platform signer attest to this exact artifact state?
- Can a reader independently reproduce the platform's verification decision?
- Can private or embargoed research establish existence and authorship without disclosing the content?

AIPubs.cloud can address these problems by treating provenance as a first-class publication artifact rather than as incidental metadata.

## 2. Design principles

1. **Evidence over assertion.** A RAIP envelope should demonstrate identity, history, and attestation instead of merely claiming authenticity.
2. **Determinism first.** Every verifier should compute the same ACF, ALC, and signed state for the same inputs.
3. **Layered diagnosis.** Verification results should identify whether identity, lifecycle, or signature failed.
4. **Privacy-aware publication.** Public proofs should be possible even when artifacts are private, embargoed, or encrypted.
5. **Extensible research graph.** RAIP v1 should support simple linear publication lifecycles while leaving room for DAG lineage, semantic fingerprints, zero-knowledge attestations, and continuous model provenance.

## 3. Core protocol layers

### 3.1 Canonicalization (RAIP-C14N)

Cryptographic verification requires stable inputs. RAIP-C14N defines deterministic serialization for lifecycle events, signed states, verifier reports, and future schema-controlled objects. Canonicalization eliminates differences caused by formatting, key ordering, whitespace, or platform-specific JSON output.

### 3.2 Artifact Content Fingerprint (ACF)

The ACF answers: **what exact artifact is this?**

For RAIP v1, the baseline ACF should be a SHA-256 digest over artifact bytes with an explicit algorithm label. This gives AIPubs exact identity for papers, datasets, source archives, model checkpoints, and generated AI outputs.

### 3.3 Artifact Lifecycle Chain (ALC)

The ALC answers: **what happened to this artifact?**

Each lifecycle event is canonicalized and chained from the artifact identity. A simple v1 lifecycle can be linear:

```text
ACF -> CREATED -> SUBMITTED -> REVIEWED -> PUBLISHED
```

Any change to event order, event body, timestamps, reviewer attestations, or publication metadata changes the final ALC value.

### 3.4 RAIP-SIGN attestation

RAIP-SIGN answers: **who or what attested to this exact state?**

The signed state binds the ACF and ALC together. AIPubs can use separate signing keys for authors, reviewers, platform release automation, and institutional partners.

### 3.5 RAIP envelope

A RAIP envelope contains the evidence required by a verifier:

```json
{
  "artifact": { "acf": "sha256:..." },
  "lifecycle": { "alc": "sha256:...", "events": [] },
  "attestation": { "algorithm": "Ed25519", "signature": "..." }
}
```

## 4. Full-envelope conformance vectors

The next implementation milestone should freeze full-envelope vectors derived from one valid baseline state:

| Vector | Mutation | Expected result |
| --- | --- | --- |
| RAIP-TV-008 | None | PASS |
| RAIP-TV-009 | Artifact bytes changed | ACF failure |
| RAIP-TV-010 | Lifecycle event changed | ALC failure |
| RAIP-TV-011 | Signature bytes changed | SIGN failure |

The generator should create the baseline envelope through RAIP primitives, then mutate downstream copies. It should not hard-code expected hashes or signatures. This keeps the test fixture aligned with the protocol's own provenance discipline.

A useful verifier response should be diagnostic, not merely boolean:

```json
{
  "overall": false,
  "artifact": { "valid": false, "reason": "acf_mismatch" },
  "lifecycle": { "valid": false, "reason": "not_evaluated" },
  "signature": { "valid": false, "reason": "not_trusted" }
}
```

## 5. AIPubs.cloud integration model

AIPubs should expose RAIP as a trust substrate underneath the publication experience:

```text
Researcher upload
  -> artifact processing service
  -> RAIP envelope generator
  -> verification report
  -> storage and public evidence endpoint
  -> publication page trust badge
```

Near-term platform features enabled by RAIP include:

- verified publication badges;
- public ACF values for citation and independent validation;
- downloadable RAIP envelopes;
- verifier reports attached to each paper;
- lifecycle timelines for draft, review, revision, publication, and archival events;
- private timestamp proofs for embargoed or encrypted artifacts;
- API endpoints for artifact registration and verification.

## 6. Recommended platform enhancements

### 6.1 Trust center and verifier UI

Add a public trust center explaining RAIP, conformance vectors, release gates, and platform signing keys. Each publication should include a compact provenance panel with ACF, ALC, signer, verification status, and download links.

### 6.2 Artifact registration API

Introduce a future API contract:

```http
POST /api/artifacts/register
POST /api/artifacts/{id}/verify
GET  /api/artifacts/{id}/raip-envelope
GET  /api/artifacts/{id}/verification-report
```

This allows external labs, journals, and CI systems to register artifacts and retrieve verification evidence.

### 6.3 Evidence-aware submission workflow

The publishing workflow should validate required metadata, produce ACF values, attach datasets and code, collect author attestations, run conformance checks, and block publication when verification fails.

### 6.4 Open peer review events

Peer review actions can become lifecycle events. Examples include `REVIEW_REQUESTED`, `REVIEW_SIGNED`, `REVISION_SUBMITTED`, `REVIEW_APPROVED`, and `PUBLISHED`.

### 6.5 Research graph and reproducibility bundles

AIPubs should model papers, datasets, code, prompts, model checkpoints, and results as linked artifacts. RAIP envelopes can then form the foundation for reproducibility bundles and verifiable citations.

## 7. Advanced roadmap

### 7.1 Semantic or topological fingerprints

Semantic fingerprints can supplement cryptographic ACF values by detecting meaning-level similarity across revisions. They must never replace byte-level identity; they should be labeled as probabilistic or model-dependent evidence.

### 7.2 DAG lifecycle lineage

Complex research often forks and merges. A future RAIP-DAG profile can model datasets feeding multiple experiments, separate model training branches, and final publication merges.

### 7.3 Zero-knowledge attestations

AIPubs can eventually support private proofs for claims such as possession, policy compliance, or dataset constraints without revealing protected data.

### 7.4 Continuous AI model provenance

For models that change over time, RAIP can record training checkpoints, dataset versions, evaluation events, hyperparameter changes, and release attestations as evolutionary provenance.

## 8. Implementation roadmap

1. **RAIP core.** Implement canonicalization, ACF, ALC, signing, verifier, and diagnostic results.
2. **Conformance vectors.** Freeze primitive vectors and full-envelope vectors RAIP-TV-008 through RAIP-TV-011.
3. **Release gate.** Add CLI verification, release manifests, and CI enforcement.
4. **AIPubs integration.** Add artifact registration, envelope storage, publication trust panels, and public verifier endpoints.
5. **Advanced evidence.** Research semantic fingerprints, DAG lineage, zero-knowledge proofs, and continuous model provenance.

## 9. Conclusion

AIPubs.cloud can become more than a repository of AI papers. With RAIP, it can become a verified knowledge network where research artifacts carry their own identity, lifecycle, attestation, and verification evidence.

AIPubs distributes knowledge. RAIP proves where that knowledge came from.
