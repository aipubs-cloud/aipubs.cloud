# Changelog

All notable changes to AIpubs.cloud are documented here.

---

# Version 1.3.1

## Site Audit, Publication, and Automation Maintenance

Added:

- Automated website accessibility and interaction audit infrastructure (#41 / #44)
  - Playwright browser checks
  - axe accessibility analysis
  - Main-site and blog availability checks
  - Mobile navigation verification
  - Keyboard-focus verification
  - Audit reports and GitHub Actions artifacts
  - Scheduled production smoke testing
- Deterministic local/preview audit documentation (#45 / #46)
  - `MAIN_URL`, `BLOG_URL`, `BLOG_ARTICLE_URL`, and `AUDIT_ENV` environment contract
  - Local static-server audit examples
  - Separate production smoke-test guidance
- Follow-up CI workflow optimization audit (#47)
  - Tracking workflow trigger scope, job-level work selection, permission minimization, and duplicate-work prevention

Updated:

- Continued semantic-version changelog tracking for all newly merged website audit and automation artifacts.
- Site quality process now treats the accessibility audit as a repeatable regression system rather than a one-time manual review.

Maintenance:

- Identified the remaining gap between production smoke testing and PR/preview validation for the site audit; deterministic local/preview execution remains tracked in #45.
- Identified GitHub Actions scope optimization opportunities, including RAIP Media trigger coverage and separation of unrelated RAIP core/media test execution.

---

# Version 1.3.0

## Recent Merge Consolidation and Version Tracking

Added:

- AIPubs blog publication pipeline foundation
  - Lifecycle stages for incoming, reviewed, approved, and published content
  - Foundation for controlled publication workflows and future blog deployment

- P2CS (Publication-to-Code Synthesis) foundation
  - AIOL-aligned subsystem architecture
  - Versioned contracts and JSON schemas
  - Pipeline stages for discovery, parsing, semantic analysis, synthesis, validation, provenance, registry, and publishing
  - Plugin-driven synthesis design

- RAIP ecosystem hardening
  - Publication validation pipeline
  - Machine-readable validation reports
  - Provenance receipts
  - Explicit lifecycle failure codes
  - Infoweave architecture manifests

Updated:

- SECURITY.md with expanded supported versions, reporting process, coordinated disclosure guidance, and security practices.
- Project documentation references and agent naming consistency.

Infrastructure:

- Improved CI publication workflows.
- Continued migration toward semantic version tracking for changed artifacts.

Version tracking policy:

Beginning with Version 1.3.0, changed project files should include explicit version identifiers where applicable. Version changes should be recorded using semantic versioning:

- MAJOR: breaking architecture or contract changes
- MINOR: new features, systems, or capabilities
- PATCH: fixes, documentation updates, and maintenance changes

---

# Version 1.2.0

## RAIP v1.0 Publication Engine

Added:

- RAIP v1.0 Python package with canonicalization, ACF hashing, ALC lifecycle chains, signatures, verification, and CLI tooling.
- RAIP Media Intelligence Suite MVP.
- Publication metadata schemas.
- Search index generation workflows.
- Citation export foundations.
- RAIP CI and validation workflows.

---

# Version 1.1.0

## Site & Infrastructure Improvements

Added:

- SEO metadata improvements.
- Mobile navigation.
- Hash-based routing.
- Robots and sitemap support.
- Cloudflare Pages error handling.
- Publication templates.

Fixed:

- Frontend metadata issues.
- Deprecated markdown rendering usage.
- Documentation placeholders.

---

# Version 1.0.0

## Initial Release

Added:

- Initial repository structure.
- Open source licensing.
- Community guidelines.
- Security policy.
- Citation metadata.
- Research organization framework.

---

Future releases will document:

- Website improvements
- Publication features
- Research tools
- Infrastructure updates
