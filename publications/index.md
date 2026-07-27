# Publications

This directory indexes all research publications hosted on AIPubs.cloud.

Each publication lives in its own folder under `research/papers/` and follows the [paper template](../research/templates/paper-template.md). A `publication.json` manifest in each paper's folder provides machine-readable provenance metadata conforming to [`schemas/publication.schema.json`](../schemas/publication.schema.json).

## Structure

```
publications/
├── index.md            ← this file
└── examples/
    └── example-publication.json   ← reference publication manifest
```

## Adding a Publication

1. Copy `research/templates/paper-template.md` to a new folder inside `research/papers/<your-paper-id>/`.
2. Fill in the YAML frontmatter and write your paper in Markdown.
3. Create a `publication.json` manifest (see `publications/examples/example-publication.json`) and place it alongside your paper.
4. Open a pull request. The RAIP pipeline will generate ACF/ALC hashes and sign the envelope after review.

## Publication Manifest

Every published paper should include a `publication.json` that declares:

| Field | Required | Description |
|---|---|---|
| `id` | ✅ | Stable slug (e.g. `paper-001`) |
| `title` | ✅ | Full title |
| `authors` | ✅ | Ordered author list |
| `version` | ✅ | Semantic version (`1.0`, `1.1`, …) |
| `license` | ✅ | SPDX identifier (e.g. `CC-BY-4.0`) |
| `date` | ✅ | ISO 8601 publication date |
| `doi` | — | Assigned after acceptance |
| `hash` | — | SHA-256 ACF fingerprint |
| `datasets` | — | Associated dataset paths or URLs |
| `version_history` | — | Past versions with dates and hashes |

See the full schema at [`schemas/publication.schema.json`](../schemas/publication.schema.json).
