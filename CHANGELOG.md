# Changelog

All notable changes to AIpubs.cloud are documented here.

---

# Version 1.2.0

## RAIP v1.0 Publication Engine

Added:

- `raip/` — Research Artifact Integrity Protocol v1.0 Python package
  - `raip/core/canonicalize.py` — RAIP-C14N deterministic JSON canonicalization
  - `raip/core/hashing.py` — SHA-256 Artifact Content Fingerprint (ACF)
  - `raip/core/lifecycle.py` — Artifact Lifecycle Chain (ALC) with chained event hashing
  - `raip/core/signatures.py` — Ed25519 RAIP-SIGN attestation (sign + verify)
  - `raip/core/verifier.py` — Diagnostic RAIP-VERIFY-REPORT with per-layer results
  - `raip/cli/main.py` — CLI entry point (`raip` command)
  - `raip/cli/publish.py` — Generate RAIP envelope for a paper
  - `raip/cli/verify.py` — Verify paper integrity (ACF + ALC + SIGN)
  - `raip/cli/inspect.py` — Display envelope contents
  - `raip/cli/sign.py` — Re-sign envelope with local key
  - `raip/cli/revoke.py` — Append REVOKED lifecycle event
  - `raip/schemas/raip.schema.json` — JSON Schema for RAIP envelopes
  - `raip/examples/example-paper.md` — Example paper with complete frontmatter
  - CLI commands: `raip init/publish/verify/inspect/sign/revoke/export/history`
- `raip/tests/` — 37 tests including conformance vectors TV-008..011
  - TV-008: valid baseline → PASS
  - TV-009: artifact bytes mutated → ACF failure
  - TV-010: lifecycle event mutated → ALC failure
  - TV-011: signature tampered → SIGN failure

## RAIP Media Intelligence Suite MVP

Added:

- `raip-media/` — Standalone media processing tool with RAIP provenance
  - `raip_media/raip_core.py` — Self-contained RAIP primitives (no external RAIP package required)
  - `raip_media/extractor.py` — Audio extraction via ffmpeg (graceful fallback)
  - `raip_media/transcriber.py` — Whisper transcription with deterministic stub backend
  - `raip_media/provenance.py` — Maps pipeline outputs to RAIP artifacts (manifest + envelope)
  - `raip_media/dashboard.py` — `rich` console TUI dashboard (live pipeline + bundle view)
  - `raip_media/cli.py` — CLI: `raip-media transcribe/verify/dashboard/export/batch`
  - `raip_media/exporters/` — TXT, Markdown, and SRT subtitle exporters
  - 12 tests covering primitives, provenance, and determinism

## Publication Metadata Engine (Phase 2)

Added:

- `schemas/paper.schema.json` — JSON Schema for paper YAML frontmatter with required/optional fields
- `.github/workflows/validate-publication.yml` — CI gate: schema + RAIP validation on PR

## Search Index Generator (Phase 3)

Added:

- `scripts/generate_papers_index.py` — Scans `research/papers/` and generates `index.json`
- `.github/workflows/generate-index.yml` — Auto-regenerates index on push to main

## Citation Export (Phase 5, partial)

Added:

- `raip export <paper.md> --format bibtex|ris|csl` — One-command citation export

## Infrastructure

Added:

- `pyproject.toml` — RAIP package configuration (setuptools, console_scripts entry point)
- `.github/workflows/raip-ci.yml` — RAIP test matrix (Python 3.10–3.12)

---

# Version 1.1.0

## Site & Infrastructure Improvements

Added:

- Open Graph and Twitter Card meta tags for social sharing
- Canonical URL tag
- Favicon link in `<head>`
- Mobile navigation menu (hamburger) for small screens
- Hash-based URL routing with History API — pages are now bookmarkable and browser back/forward works
- `public/robots.txt` — SEO crawl instructions and sitemap reference
- `public/sitemap.xml` — all primary routes listed for search indexers
- `404.html` — custom not-found page for Cloudflare Pages
- `research/templates/paper-template.md` — structured Markdown template for new paper submissions
- Dynamic copyright year in footer (no longer hardcoded to 2024)
- Clipboard API BibTeX copy button with visual feedback on paper view
- Real GitHub and documentation links in footer (replacing `href="#"` placeholders)

Fixed:

- Removed duplicate Tailwind CSS typography CDN script (was loaded twice)
- Replaced deprecated `marked.setOptions({ highlight })` with `marked.use({ renderer })` API
- `feature/new-publication-system/readme.md` placeholder replaced with real feature overview

Updated:

- `README.md` — expanded from a single-line title to a full project README with setup instructions, structure overview, deployment guide, and citation
- `CITATION.cff` — fixed `YOUR_USERNAME` placeholder to the real repository URL
- `CONTRIBUTING.md` — no changes; confirmed complete

---

# Version 1.0.0

## Initial Release

Added:

- Initial repository structure
- Open source licensing
- Community guidelines
- Security policy
- Citation metadata
- Research organization framework

---

Future releases will document:

- Website improvements
- Publication features
- Research tools
- Infrastructure updates