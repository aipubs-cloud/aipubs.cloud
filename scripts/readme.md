Here’s a tight, high‑value breakdown of what your script does, why it works, and where it can be improved — all directly grounded in the code you shared in your active VS Code tab.

---

## 🧩 Core Functionality (Concise Takeaway)
Your script **scans `research/papers/` for Markdown files**, extracts **YAML frontmatter + abstract + metadata**, computes **reading time**, generates **URL slugs**, and writes a consolidated **`index.json`** sorted by date.

It’s essentially a **static-site search index generator for academic papers**.

---

## 📘 What the Script Actually Does — Step by Step

### 1. **Locate papers**
- Uses `_PAPERS_DIR = research/papers/`
- Recursively finds all `*.md` files via `rglob`.

### 2. **Parse YAML frontmatter**
`parse_frontmatter()`:
- Detects `--- ... ---` at the top.
- Loads YAML via PyYAML.
- Returns `(frontmatter_dict, markdown_body)`.

### 3. **Extract metadata**
`build_paper_entry()` pulls:
- `title`
- `authors` (supports list of dicts or strings)
- `date` → `year`
- `keywords` or `tags`
- `category`
- `version`
- `license`
- `doi`
- `raip`
- `hasDataset`
- `hasCode`

### 4. **Generate abstract**
`extract_abstract()`:
- Prefer `## Abstract` section.
- Fallback: first non‑empty paragraph.
- Normalizes whitespace.
- Truncates to 300–500 chars.

### 5. **Compute reading time**
`reading_time()`:
- Words ÷ 200 WPM → rounded up.
- Minimum 1 minute.

### 6. **Generate URL slug**
`slug_from_path()`:
- Lowercase filename.
- Replace `_` and spaces with `-`.
- Final URL: `/papers/<slug>`.

### 7. **Write JSON index**
`generate_index()`:
- Sorts papers by date (descending).
- Writes pretty‑printed JSON to `index.json`.

---

## 🔍 Strengths of the Script
- **Robust frontmatter parsing** with fallback behavior.
- **Graceful handling** of missing fields.
- **Consistent URL generation** for static sites.
- **Abstract extraction logic** is practical and resilient.
- **Reading time estimation** is simple and effective.
- **Safe YAML parsing** (no `unsafe_load`).

---

## ⚠️ Weak Spots & Opportunities for Improvement

### 1. **Frontmatter regex is brittle**
Current regex requires:

```
---\n ... \n---
```

If a file has:
- extra spaces,
- Windows line endings,
- comments inside YAML,
- or trailing whitespace,

…it may fail.

**Fix:** use a more tolerant parser or a Markdown/YAML library that handles frontmatter natively.

---

### 2. **Slug generation ignores nested directories**
If papers are organized like:

```
papers/2024/my_paper.md
```

Your slug becomes:

```
/papers/my-paper
```

This loses hierarchy.

**Better:**

```python
rel = path.relative_to(papers_dir)
slug = str(rel.with_suffix("")).replace("/", "-")
```

---

### 3. **Date sorting is string‑based**
Sorting by `"2024-10-01"` works, but if formats vary (e.g., `2024/10/01` or missing leading zeros), ordering breaks.

**Better:** parse with `datetime.fromisoformat()`.

---

### 4. **Abstract extraction may grab headings**
If the first paragraph after `## Abstract` contains subheadings or lists, you may get noise.

---

### 5. **No validation for required fields**
If a paper is missing:
- `title`
- `authors`
- `date`

…it silently skips or produces partial entries.

You may want warnings.

---

### 6. **No support for Markdown links or formatting**
Abstract extraction strips whitespace but not Markdown syntax.

---

## 🚀 Suggested Enhancements (High‑Impact)

### ✔ Add logging for skipped papers
```python
if not fm.get("title"):
    print(f"Skipping {path}: missing title")
```

### ✔ Support nested slugs
```python
url = "/papers/" + slug_from_path(rel)
```

could become:

```python
url = "/papers/" + str(rel.with_suffix("")).replace("/", "-")
```

### ✔ Normalize dates
```python
from datetime import datetime

try:
    dt = datetime.fromisoformat(date)
except ValueError:
    dt = None
```

### ✔ More robust frontmatter parsing
Use `python-frontmatter`:

```python
import frontmatter
post = frontmatter.loads(text)
fm = post.metadata
body = post.content
```

---

## 🧪 If You Want, I Can:
- Refactor the script for robustness
- Add unit tests
- Add CLI options (e.g., `--strict`, `--verbose`)
- Add support for HTML abstracts
- Add caching for large paper directories
- Convert this into a reusable library module

Just tell me the direction you want to take next.



---


You’re building a real system here, not a toy—so let’s refactor this like it matters.

---

### Refactored script: more robust, with strict/verbose, HTML abstracts, and caching

```python
#!/usr/bin/env python3
"""Generate papers.json search index from Markdown frontmatter.

Scans a papers directory for Markdown files containing YAML frontmatter,
extracts metadata, and writes a consolidated JSON index to the path
provided (default: research/papers/index.json).

Features:
- Robust frontmatter parsing
- Strict mode (fail on malformed/invalid papers)
- Verbose logging
- Optional HTML abstracts
- Simple caching for large directories
"""

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("error: PyYAML is required.  pip install PyYAML", file=sys.stderr)
    sys.exit(1)


_PAPERS_DIR = Path(__file__).parent.parent / "research" / "papers"
_DEFAULT_OUT = _PAPERS_DIR / "index.json"
_CACHE_DEFAULT = _PAPERS_DIR / ".papers_index.cache.json"
_WORDS_PER_MINUTE = 200


@dataclass
class PaperEntry:
    title: str
    authors: List[str]
    category: str
    year: Optional[int]
    date: str
    version: str
    abstract: str
    abstractHtml: Optional[str]
    url: str
    keywords: List[str]
    license: str
    doi: Optional[str]
    raip: Optional[str]
    hasDataset: bool
    hasCode: bool
    readingTimeMinutes: int


def log(msg: str, verbose: bool) -> None:
    if verbose:
        print(msg, file=sys.stderr)


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Return (frontmatter_dict, body_text) from a Markdown file.

    More tolerant frontmatter parsing:
    - Frontmatter must start at the beginning with '---'
    - Ends at the next line with '---'
    """
    if not text.startswith("---"):
        return {}, text

    lines = text.splitlines()
    fm_lines: List[str] = []
    end_index: Optional[int] = None

    # Skip initial '---'
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = i
            break
        fm_lines.append(line)

    if end_index is None:
        # No closing '---'
        return {}, text

    fm_text = "\n".join(fm_lines)
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        fm = {}

    body = "\n".join(lines[end_index + 1:])
    return fm, body


def reading_time(body: str) -> int:
    """Estimate reading time in minutes."""
    words = len(body.split())
    return max(1, math.ceil(words / _WORDS_PER_MINUTE))


def slug_from_rel_path(rel: Path) -> str:
    """Return a URL slug from the relative paper file path.

    Example:
        2024/my_paper.md -> '2024-my-paper'
    """
    no_suffix = rel.with_suffix("")
    return "-".join(str(no_suffix).split("/")).lower().replace("_", "-")


def extract_abstract_markdown(body: str) -> str:
    """Pull the first paragraph after an ## Abstract heading (Markdown)."""
    match = re.search(r"^##\s+Abstract\s*$\n+(.*?)(\n\n|\Z)", body, re.DOTALL | re.MULTILINE)
    if match:
        text = match.group(1).strip()
        text = re.sub(r"\s+", " ", text)
        return text[:500]
    # Fallback: first non-empty paragraph
    for para in body.split("\n\n"):
        stripped = para.strip()
        if stripped and not stripped.startswith("#"):
            return re.sub(r"\s+", " ", stripped)[:500]
    return ""


def parse_date(date_str: str) -> Tuple[str, Optional[int], Optional[datetime]]:
    """Normalize date string and extract year + datetime object for sorting."""
    if not date_str:
        return "", None, None
    date_str = date_str.strip()
    # Try ISO first
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m", "%Y"):
        try:
            dt = datetime.strptime(date_str, fmt)
            year = dt.year
            # Normalize to ISO date if full date
            if fmt in ("%Y-%m-%d", "%Y/%m/%d"):
                norm = dt.strftime("%Y-%m-%d")
            elif fmt == "%Y-%m":
                norm = dt.strftime("%Y-%m")
            else:
                norm = str(year)
            return norm, year, dt
        except ValueError:
            continue
    # Fallback: year from first 4 digits
    year = int(date_str[:4]) if date_str[:4].isdigit() else None
    return date_str, year, None


def build_paper_entry(
    path: Path,
    papers_dir: Path,
    strict: bool,
    verbose: bool,
) -> Optional[PaperEntry]:
    """Return a search-index entry for the Markdown paper at *path*."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        msg = f"error: cannot read {path}: {e}"
        if strict:
            raise RuntimeError(msg)
        log(msg, verbose)
        return None

    fm, body = parse_frontmatter(text)
    if not isinstance(fm, dict):
        fm = {}

    title = str(fm.get("title", "")).strip()
    if not title:
        msg = f"warning: skipping {path}: missing title"
        if strict:
            raise RuntimeError(msg)
        log(msg, verbose)
        return None

    authors_raw = fm.get("authors", [])
    author_names: List[str] = []
    if isinstance(authors_raw, list):
        for a in authors_raw:
            if isinstance(a, dict):
                name = a.get("name")
                if name:
                    author_names.append(str(name))
            else:
                author_names.append(str(a))
    elif isinstance(authors_raw, str):
        author_names = [authors_raw]
    else:
        author_names = []

    date_raw = str(fm.get("date", "")).strip()
    date_norm, year, _dt = parse_date(date_raw)

    keywords_raw = fm.get("keywords", fm.get("tags", []))
    if isinstance(keywords_raw, list):
        keywords = [str(k) for k in keywords_raw]
    elif isinstance(keywords_raw, str):
        keywords = [keywords_raw]
    else:
        keywords = []

    # Abstract: prefer explicit HTML, then explicit text, then Markdown extraction
    abstract_html = fm.get("abstractHtml") or fm.get("abstract_html")
    abstract_text = fm.get("abstract") or ""
    if not abstract_text:
        abstract_text = extract_abstract_markdown(body)
    abstract_text = str(abstract_text).strip()[:500]

    rel = path.relative_to(papers_dir)
    url = "/papers/" + slug_from_rel_path(rel)

    entry = PaperEntry(
        title=title,
        authors=author_names,
        category=str(fm.get("category", "")).strip(),
        year=year,
        date=date_norm,
        version=str(fm.get("version", "1.0")),
        abstract=abstract_text,
        abstractHtml=str(abstract_html) if abstract_html else None,
        url=url,
        keywords=keywords,
        license=str(fm.get("license", "")),
        doi=str(fm.get("doi", "")) if fm.get("doi") else None,
        raip=str(fm.get("raip", "")) if fm.get("raip") else None,
        hasDataset=bool(fm.get("hasDataset", False)),
        hasCode=bool(fm.get("hasCode", False)),
        readingTimeMinutes=reading_time(body),
    )
    return entry


def load_cache(cache_path: Path, verbose: bool) -> Dict[str, Any]:
    if not cache_path.is_file():
        return {}
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            log(f"cache: loaded from {cache_path}", verbose)
            return data
    except Exception as e:
        log(f"cache: failed to load {cache_path}: {e}", verbose)
    return {}


def save_cache(cache_path: Path, cache: Dict[str, Any], verbose: bool) -> None:
    try:
        cache_path.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
        log(f"cache: saved to {cache_path}", verbose)
    except Exception as e:
        log(f"cache: failed to save {cache_path}: {e}", verbose)


def generate_index(
    papers_dir: Path,
    out_path: Path,
    strict: bool,
    verbose: bool,
    cache_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    cache: Dict[str, Any] = {}
    if cache_path:
        cache = load_cache(cache_path, verbose)

    papers: List[PaperEntry] = []
    md_files = sorted(papers_dir.rglob("*.md"))

    new_cache: Dict[str, Any] = {"files": {}}

    for path in md_files:
        rel_str = str(path.relative_to(papers_dir))
        stat = path.stat()
        key = rel_str
        mtime = stat.st_mtime

        cached_file = cache.get("files", {}).get(key)
        if cached_file and cached_file.get("mtime") == mtime:
            # Reuse cached entry
            entry_data = cached_file.get("entry")
            if entry_data:
                papers.append(PaperEntry(**entry_data))
                new_cache["files"][key] = {"mtime": mtime, "entry": entry_data}
                log(f"cache: reused {rel_str}", verbose)
                continue

        entry = build_paper_entry(path, papers_dir, strict=strict, verbose=verbose)
        if entry:
            papers.append(entry)
            new_cache["files"][key] = {"mtime": mtime, "entry": asdict(entry)}

    # Sort by normalized date (descending), then title
    papers.sort(key=lambda p: (p.date or "", p.title.lower()), reverse=True)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_data = [asdict(p) for p in papers]
    out_path.write_text(
        json.dumps(out_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if cache_path:
        save_cache(cache_path, new_cache, verbose)

    return out_data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--papers-dir",
        default=str(_PAPERS_DIR),
        help=f"Papers directory (default: {_PAPERS_DIR})",
    )
    parser.add_argument(
        "--out",
        default=str(_DEFAULT_OUT),
        help=f"Output JSON path (default: {_DEFAULT_OUT})",
    )
    parser.add_argument(
        "--cache",
        default=str(_CACHE_DEFAULT),
        help=f"Cache file path (default: {_CACHE_DEFAULT}, use '' to disable)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on malformed papers (missing title, unreadable file, etc.)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging to stderr",
    )
    args = parser.parse_args()

    papers_dir = Path(args.papers_dir)
    out_path = Path(args.out)
    cache_path = Path(args.cache) if args.cache.strip() else None

    if not papers_dir.is_dir():
        print(f"warning: papers directory not found: {papers_dir}", file=sys.stderr)
        papers_dir.mkdir(parents=True, exist_ok=True)

    papers = generate_index(
        papers_dir=papers_dir,
        out_path=out_path,
        strict=args.strict,
        verbose=args.verbose,
        cache_path=cache_path,
    )
    print(f"Generated {len(papers)} paper(s) → {out_path}")


if __name__ == "__main__":
    main()
```

---

### Unit tests (pytest-style) for core behavior

You can drop this into `tests/test_generate_papers_index.py`:

```python
import json
from pathlib import Path
import textwrap

import pytest

from scripts.generate_papers_index import (
    parse_frontmatter,
    reading_time,
    slug_from_rel_path,
    extract_abstract_markdown,
    build_paper_entry,
    generate_index,
)


def write_md(tmp_path: Path, rel: str, content: str) -> Path:
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def test_parse_frontmatter_basic():
    text = textwrap.dedent(
        """\
        ---
        title: Test Paper
        authors:
          - name: Alice
        ---
        Body text here.
        """
    )
    fm, body = parse_frontmatter(text)
    assert fm["title"] == "Test Paper"
    assert "Body text here." in body


def test_parse_frontmatter_no_frontmatter():
    text = "No frontmatter here.\nJust text."
    fm, body = parse_frontmatter(text)
    assert fm == {}
    assert body.startswith("No frontmatter")


def test_reading_time_minimum():
    assert reading_time("one two") == 1


def test_slug_from_rel_path_nested():
    rel = Path("2024/my_paper.md")
    assert slug_from_rel_path(rel) == "2024-my-paper"


def test_extract_abstract_markdown_heading():
    body = textwrap.dedent(
        """\
        # Title

        ## Abstract

        This is the abstract paragraph.

        ## Another
        """
    )
    abstract = extract_abstract_markdown(body)
    assert "This is the abstract paragraph." in abstract


def test_build_paper_entry_basic(tmp_path):
    content = textwrap.dedent(
        """\
        ---
        title: Test Paper
        authors:
          - name: Alice
          - Bob
        date: 2024-01-02
        keywords: [ai, ml]
        abstract: Explicit abstract.
        hasDataset: true
        hasCode: false
        ---
        Body text here.
        """
    )
    path = write_md(tmp_path, "test_paper.md", content)
    entry = build_paper_entry(path, tmp_path, strict=True, verbose=False)
    assert entry is not None
    assert entry.title == "Test Paper"
    assert entry.authors == ["Alice", "Bob"]
    assert entry.year == 2024
    assert "Explicit abstract" in entry.abstract
    assert entry.hasDataset is True
    assert entry.hasCode is False
    assert entry.url.endswith("test-paper")


def test_build_paper_entry_html_abstract(tmp_path):
    content = textwrap.dedent(
        """\
        ---
        title: HTML Abstract Paper
        abstractHtml: "<p>This is <em>HTML</em> abstract.</p>"
        ---
        Body text here.
        """
    )
    path = write_md(tmp_path, "html_paper.md", content)
    entry = build_paper_entry(path, tmp_path, strict=True, verbose=False)
    assert entry.abstractHtml is not None
    assert "<em>HTML</em>" in entry.abstractHtml


def test_generate_index_with_cache(tmp_path):
    papers_dir = tmp_path / "papers"
    papers_dir.mkdir()

    content = textwrap.dedent(
        """\
        ---
        title: Cached Paper
        date: 2024-01-01
        ---
        Body text here.
        """
    )
    write_md(papers_dir, "cached.md", content)

    out_path = tmp_path / "index.json"
    cache_path = tmp_path / ".cache.json"

    # First run: builds index and cache
    data1 = generate_index(
        papers_dir=papers_dir,
        out_path=out_path,
        strict=True,
        verbose=False,
        cache_path=cache_path,
    )
    assert len(data1) == 1

    # Second run: should reuse cache
    data2 = generate_index(
        papers_dir=papers_dir,
        out_path=out_path,
        strict=True,
        verbose=False,
        cache_path=cache_path,
    )
    assert len(data2) == 1

    # Ensure JSON is valid
    loaded = json.loads(out_path.read_text(encoding="utf-8"))
    assert loaded[0]["title"] == "Cached Paper"
```

---

If you want, next step we can wire this into your repo’s CI (pytest + `python -m compileall` on `scripts/`) so this index generator never silently rots.


---


This version is a good baseline and is much closer to something that can ship with `aipubs.cloud`, but compared with the hardened refactor above it is still missing a few publication-registry safeguards.

I would not replace it wholesale yet. I would evolve this version because it already matches your repo conventions:

* `research/papers/` as source
* `index.json` as generated registry
* YAML frontmatter as metadata contract
* frontend consuming static JSON

The main weaknesses before CI adoption:

---

## 1. Frontmatter parser is too brittle

Current:

```python
match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
```

This fails if:

* there is no newline after closing `---`
* there are extra spaces
* malformed YAML exists
* a document starts with BOM
* a paper contains a second `---` separator in content

Better:

```python
def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)

    if len(parts) < 3:
        return {}, text

    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}, text

    return fm, parts[2].lstrip("\n")
```

This is much more tolerant for a research repository.

---

## 2. Add strict mode

Right now:

```python
if not fm.get("title"):
    return None
```

A broken paper silently disappears.

For a publication system this is dangerous.

A missing title should fail CI.

Add:

```python
parser.add_argument(
    "--strict",
    action="store_true",
    help="Fail on invalid papers"
)
```

Then:

```python
def build_paper_entry(path, papers_dir, strict=False):
```

and:

```python
if not fm.get("title"):
    message = f"Missing title: {path}"

    if strict:
        raise ValueError(message)

    print(f"warning: {message}", file=sys.stderr)
    return None
```

Now CI catches publication mistakes.

---

## 3. Add RAIP fingerprint support

This is the biggest missed opportunity.

Your registry already has:

```python
"raip": ...
```

but it does not verify the artifact.

Add:

```python
import hashlib
```

then:

```python
def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)

    return digest.hexdigest()
```

Then:

```python
"artifactHash": compute_sha256(path),
"hashAlgorithm": "sha256",
```

Now every paper in the public index has provenance.

Example:

```json
{
  "title": "Synthetic Ontogeny",
  "raip": "RAIP-1.0",
  "artifactHash": "b83c91d...",
  "hashAlgorithm": "sha256"
}
```

That makes the index a registry, not just a search file.

---

## 4. Fix nested paper URL collision

Current:

```python
def slug_from_path(path: Path) -> str:
    return path.stem.lower()
```

Problem:

```
research/papers/
 ├── ai/paper.md
 └── quantum/paper.md
```

Both become:

```
/papers/paper
```

Collision.

Use:

```python
def slug_from_path(path: Path) -> str:
    return "-".join(path.with_suffix("").parts).lower().replace("_", "-")
```

Result:

```
/papers/ai-paper
/papers/quantum-paper
```

---

## 5. Sort stability

Current:

```python
papers.sort(key=lambda p: (p.get("date") or ""), reverse=True)
```

If dates match, ordering can shuffle.

Use:

```python
papers.sort(
    key=lambda p: (
        p.get("date") or "",
        p.get("title", "").lower()
    ),
    reverse=True
)
```

---

## 6. Add generated metadata

The frontend will eventually benefit from knowing when the registry was built.

Add:

```python
out.write_text(
    json.dumps(
        {
            "generatedAt": datetime.utcnow().isoformat() + "Z",
            "count": len(papers),
            "papers": papers
        },
        indent=2,
        ensure_ascii=False,
    )
)
```

Then the frontend can display:

```
Publication Registry
142 artifacts indexed
Last updated: 2026-08-04
```

---

## Suggested final architecture

I would make this the publication pipeline:

```
research/papers/*.md
        |
        |
        v
generate_papers_index.py
        |
        |
        +--> SHA256 artifact fingerprint
        |
        +--> metadata extraction
        |
        +--> reading metrics
        |
        v
research/papers/index.json
        |
        |
        v
aipubs.cloud frontend
```

The current script is about 80% there. The missing 20% is exactly the layer that turns it from a static-site helper into a real artifact registry: strict validation, deterministic URLs, provenance, and CI failure signals. That fits very naturally with your RAIP work.


---

```python
#!/usr/bin/env python3
"""Generate papers.json search index from Markdown frontmatter.

Scans research/papers/ for Markdown files containing YAML frontmatter,
extracts metadata, and writes a consolidated JSON index to the path
provided (default: research/papers/index.json).

Usage:
    python scripts/generate_papers_index.py
    python scripts/generate_papers_index.py --out public/papers.json
"""

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import yaml
except ImportError:
    print("error: PyYAML is required.  pip install PyYAML", file=sys.stderr)
    sys.exit(1)


_PAPERS_DIR = Path(__file__).parent.parent / "research" / "papers"
_DEFAULT_OUT = _PAPERS_DIR / "index.json"
_WORDS_PER_MINUTE = 200


def log(msg: str, verbose: bool) -> None:
    if verbose:
        print(msg, file=sys.stderr)


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Return (frontmatter_dict, body_text) from a Markdown file.

    More tolerant frontmatter parsing:
    - Frontmatter must start at the beginning with '---'
    - Ends at the next '---'
    """
    # Strip BOM if present
    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff")

    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    fm_text = parts[1]
    body = parts[2].lstrip("\n")

    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        return {}, text

    if not isinstance(fm, dict):
        fm = {}

    return fm, body


def reading_time(body: str) -> int:
    """Estimate reading time in minutes."""
    words = len(body.split())
    return max(1, math.ceil(words / _WORDS_PER_MINUTE))


def slug_from_path(path: Path, papers_dir: Path) -> str:
    """Return a URL slug from the paper file path, including nested dirs.

    research/papers/ai/paper.md -> ai-paper
    """
    rel = path.relative_to(papers_dir).with_suffix("")
    parts = rel.parts
    slug = "-".join(parts).lower().replace("_", "-").replace(" ", "-")
    return slug


def extract_abstract(body: str) -> str:
    """Pull the first paragraph after an ## Abstract heading."""
    match = re.search(
        r"^##\s+Abstract\s*$\n+(.*?)(\n\n|\Z)",
        body,
        re.DOTALL | re.MULTILINE,
    )
    if match:
        text = match.group(1).strip()
        text = re.sub(r"\s+", " ", text)
        return text[:500]
    # Fallback: first non-empty paragraph
    for para in body.split("\n\n"):
        stripped = para.strip()
        if stripped and not stripped.startswith("#"):
            return re.sub(r"\s+", " ", stripped)[:500]
    return ""


def compute_sha256(path: Path) -> str:
    """Compute SHA256 fingerprint of the paper file."""
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_paper_entry(
    path: Path,
    papers_dir: Path,
    strict: bool = False,
    verbose: bool = False,
) -> Dict[str, Any] | None:
    """Return a search-index entry for the Markdown paper at *path*."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        msg = f"error: cannot read {path}: {e}"
        if strict:
            raise RuntimeError(msg)
        log(msg, verbose)
        return None

    fm, body = parse_frontmatter(text)

    title = str(fm.get("title", "")).strip()
    if not title:
        msg = f"Missing title: {path}"
        if strict:
            raise ValueError(msg)
        print(f"warning: {msg}", file=sys.stderr)
        return None

    authors = fm.get("authors", [])
    if isinstance(authors, list):
        author_names = [
            (a.get("name") if isinstance(a, dict) else str(a)) for a in authors
        ]
    elif isinstance(authors, str):
        author_names = [authors]
    else:
        author_names = []

    date = str(fm.get("date", "")).strip()
    year = int(date[:4]) if date and date[:4].isdigit() else None

    keywords = fm.get("keywords", fm.get("tags", []))
    if isinstance(keywords, list):
        keywords = [str(k) for k in keywords]
    elif isinstance(keywords, str):
        keywords = [keywords]
    else:
        keywords = []

    # Abstract: prefer explicit HTML, then explicit text, then Markdown extraction
    abstract_html = fm.get("abstractHtml") or fm.get("abstract_html")
    abstract = fm.get("abstract", "") or extract_abstract(body)
    abstract = str(abstract).strip()[:500]

    url = "/papers/" + slug_from_path(path, papers_dir)

    artifact_hash = compute_sha256(path)

    entry = {
        "title": title,
        "authors": author_names,
        "category": fm.get("category", ""),
        "year": year,
        "date": date,
        "version": str(fm.get("version", "1.0")),
        "abstract": abstract,
        "abstractHtml": str(abstract_html) if abstract_html else None,
        "url": url,
        "keywords": keywords,
        "license": str(fm.get("license", "")),
        "doi": str(fm.get("doi", "")) if fm.get("doi") else None,
        "raip": str(fm.get("raip", "")) if fm.get("raip") else None,
        "hasDataset": bool(fm.get("hasDataset", False)),
        "hasCode": bool(fm.get("hasCode", False)),
        "readingTimeMinutes": reading_time(body),
        "artifactHash": artifact_hash,
        "hashAlgorithm": "sha256",
    }
    return entry


def generate_index(
    papers_dir: Path,
    out_path: Path,
    strict: bool = False,
    verbose: bool = False,
) -> List[Dict[str, Any]]:
    papers: List[Dict[str, Any]] = []
    md_files = sorted(papers_dir.rglob("*.md"))

    for path in md_files:
        entry = build_paper_entry(path, papers_dir, strict=strict, verbose=verbose)
        if entry:
            papers.append(entry)

    papers.sort(
        key=lambda p: (
            p.get("date") or "",
            p.get("title", "").lower(),
        ),
        reverse=True,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generatedAt": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "count": len(papers),
        "papers": papers,
    }
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return papers


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--papers-dir",
        default=str(_PAPERS_DIR),
        help=f"Papers directory (default: {_PAPERS_DIR})",
    )
    parser.add_argument(
        "--out",
        default=str(_DEFAULT_OUT),
        help=f"Output JSON path (default: {_DEFAULT_OUT})",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on invalid papers (missing title, unreadable file, etc.)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging to stderr",
    )
    args = parser.parse_args()

    papers_dir = Path(args.papers_dir)
    out_path = Path(args.out)

    if not papers_dir.is_dir():
        print(f"warning: papers directory not found: {papers_dir}", file=sys.stderr)
        papers_dir.mkdir(parents=True, exist_ok=True)

    papers = generate_index(
        papers_dir=papers_dir,
        out_path=out_path,
        strict=args.strict,
        verbose=args.verbose,
    )
    print(f"Generated {len(papers)} paper(s) → {out_path}")


if __name__ == "__main__":
    main()
```

===

The **new version is a meaningful upgrade** over the original. It is no longer just an index generator; it is becoming a publication registry builder. The diff is mostly positive. Below is the engineering review of the migration.

## Summary of changes

| Area                | Original        | New                                                 | Assessment             |
| ------------------- | --------------- | --------------------------------------------------- | ---------------------- |
| Frontmatter parsing | Regex only      | BOM handling + tolerant split parsing + YAML safety | ✅ Improved             |
| Abstract extraction | Basic           | Multiline heading-safe extraction                   | ✅ Improved             |
| Nested paper URLs   | Filename only   | Relative path slug                                  | ✅ Fixed collision risk |
| Authors parsing     | Lists only      | Lists + strings                                     | ✅ Improved             |
| Keywords parsing    | Lists only      | Lists + strings                                     | ✅ Improved             |
| Strict validation   | None            | `--strict`                                          | ✅ Important            |
| Logging             | Silent failures | Verbose mode                                        | ✅ Important            |
| Provenance          | None            | SHA-256 artifact hash                               | ✅ RAIP aligned         |
| HTML abstracts      | None            | `abstractHtml` support                              | ✅ Frontend ready       |
| Output metadata     | Raw array       | Registry envelope                                   | ⚠️ Breaking change     |
| Cache               | None            | None                                                | ⏳ Still missing        |

---

# Major improvement: RAIP compatibility

This is the biggest architectural jump:

```python
artifact_hash = compute_sha256(path)
```

and:

```json
{
  "artifactHash": "abc123...",
  "hashAlgorithm": "sha256"
}
```

Now every indexed paper has an immutable identity.

That aligns directly with RAIP:

```
Markdown Artifact
        |
        |
        v
SHA-256 fingerprint
        |
        |
        v
Publication Index
        |
        |
        v
Public Registry
```

This is the right direction for `aipubs.cloud`.

---

# Important breaking change

The original generated:

```json
[
  {
    "title": "Paper One",
    "url": "/papers/paper-one"
  }
]
```

The new generates:

```json
{
  "generatedAt": "2026-08-04T02:20:00Z",
  "count": 1,
  "papers": [
    {
      "title": "Paper One",
      "url": "/papers/paper-one"
    }
  ]
}
```

This is actually a better schema, but your frontend must change.

Old:

```javascript
papers.forEach(...)
```

New:

```javascript
papersIndex.papers.forEach(...)
```

or:

```javascript
const papers = data.papers ?? data;
```

I would recommend the compatibility approach:

```javascript
async function loadPapers() {
    const data = await fetch("/papers/index.json")
        .then(r => r.json());

    return Array.isArray(data)
        ? data
        : data.papers;
}
```

That prevents older deployments from breaking.

---

# One bug: `datetime.utcnow()` warning

Current:

```python
datetime.utcnow()
```

Python 3.12+ considers naive UTC timestamps discouraged.

Replace:

```python
from datetime import datetime, timezone
```

then:

```python
datetime.now(timezone.utc)
```

Final:

```python
"generatedAt": datetime.now(timezone.utc)
    .isoformat(timespec="seconds")
    .replace("+00:00", "Z")
```

Produces:

```text
2026-08-04T02:20:00Z
```

---

# One subtle bug: slug generation

New:

```python
slug = "-".join(rel.parts).lower()
```

Good.

But:

```
research/papers/
 └── AI Research.md
```

becomes:

```
ai research
```

because:

```python
.replace(" ", "-")
```

only happens after joining.

Current:

```python
slug = "-".join(rel.parts).lower().replace("_", "-").replace(" ", "-")
```

works, but I would add special character normalization:

```python
slug = re.sub(
    r"[^a-z0-9-]+",
    "-",
    slug
).strip("-")
```

So:

```
Quantum Theory: Ω Edition.md
```

becomes:

```
quantum-theory-edition
```

---

# Missing piece: deleted paper detection

Right now:

```
paper.md
   |
   v
index.json
```

If someone deletes:

```
paper.md
```

the next build removes it correctly.

That is good.

But with RAIP lifecycle, you may eventually want:

```json
{
 "status": "removed",
 "removedAt": "...",
 "previousHash": "..."
}
```

rather than disappearance.

That would allow a provenance chain.

---

# Missing piece: cache

The original enhancement proposal had:

```
mtime
 |
 v
reuse existing metadata
```

The new version removed it.

For 10 papers, irrelevant.

For:

```
aipubs.cloud
 ├── 10,000 papers
 ├── datasets
 ├── media artifacts
```

you will want caching.

I would add:

```
research/papers/.index-cache.json
```

with:

```json
{
 "paper.md": {
   "sha256": "...",
   "entry": {}
 }
}
```

Then:

```
SHA unchanged?
       |
       v
reuse entry
```

This actually fits RAIP better than mtime caching.

---

# One thing I would change before merging

The generated object should probably become:

```json
{
  "schemaVersion": "1.0",
  "generatedAt": "...",
  "generator": "aipubs-indexer",
  "count": 42,
  "papers": []
}
```

Why?

Because you now have a registry protocol.

Future frontend versions can branch:

```javascript
if(index.schemaVersion === "1.0")
```

---

# Verdict

I would merge the new version over the original.

The upgrade path is:

```
Original
  |
  |  static search helper
  v
New
  |
  |  provenance-aware publication registry
  v
RAIP Registry Engine
```

Before production, I would make three final changes:

1. ✅ Replace `datetime.utcnow()` with timezone-aware UTC
2. ✅ Add `schemaVersion` to the JSON output
3. ✅ Add SHA-based caching

After that, this is no longer just generating `papers.json`. It is the first layer of an artifact registry.
