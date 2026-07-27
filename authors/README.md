# Authors

This directory is reserved for author profile files on AIPubs.cloud.

Each author profile is a JSON file conforming to [`schemas/author.schema.json`](../schemas/author.schema.json).

## File Naming

Author profiles should be named using the author's GitHub username or a URL-safe slug derived from their name:

```
authors/
├── README.md
├── jane-researcher.json
└── john-collaborator.json
```

## Author Profile Fields

| Field | Required | Description |
|---|---|---|
| `name` | ✅ | Full display name |
| `given` | — | Given (first) name for citation formatting |
| `family` | — | Family (last) name for citation formatting |
| `orcid` | — | ORCID iD (strongly recommended) |
| `affiliation` | — | Primary institution |
| `email` | — | Contact email |
| `github` | — | GitHub username |
| `website` | — | Personal/institutional website |
| `bio` | — | Short biography (1–3 sentences) |
| `publications` | — | AIPubs.cloud publication IDs |

See the full schema at [`schemas/author.schema.json`](../schemas/author.schema.json).

## Example

```json
{
  "name": "Jane Researcher",
  "given": "Jane",
  "family": "Researcher",
  "orcid": "0000-0002-1825-0097",
  "affiliation": "Institute for Open Science",
  "email": "jane@example.org",
  "github": "jane-researcher",
  "bio": "Jane is a researcher specialising in open AI publishing and reproducibility.",
  "publications": ["paper-example"]
}
```
