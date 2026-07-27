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
import json
import math
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("error: PyYAML is required.  pip install PyYAML", file=sys.stderr)
    sys.exit(1)


_PAPERS_DIR = Path(__file__).parent.parent / "research" / "papers"
_DEFAULT_OUT = _PAPERS_DIR / "index.json"
_WORDS_PER_MINUTE = 200


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return ``(frontmatter_dict, body_text)`` from a Markdown file."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if match:
        fm = yaml.safe_load(match.group(1)) or {}
        body = text[match.end():]
        return fm, body
    return {}, text


def reading_time(body: str) -> int:
    """Estimate reading time in minutes."""
    words = len(body.split())
    return max(1, math.ceil(words / _WORDS_PER_MINUTE))


def slug_from_path(path: Path) -> str:
    """Return a URL slug from the paper file path."""
    return path.stem.lower().replace("_", "-").replace(" ", "-")


def extract_abstract(body: str) -> str:
    """Pull the first paragraph after an ## Abstract heading."""
    match = re.search(r"##\s+Abstract\s*\n+(.*?)(\n\n|\Z)", body, re.DOTALL)
    if match:
        text = match.group(1).strip()
        text = re.sub(r"\s+", " ", text)
        return text[:500]
    # Fallback: first non-empty paragraph
    for para in body.split("\n\n"):
        stripped = para.strip()
        if stripped and not stripped.startswith("#"):
            return re.sub(r"\s+", " ", stripped)[:300]
    return ""


def build_paper_entry(path: Path, papers_dir: Path) -> dict | None:
    """Return a search-index entry for the Markdown paper at *path*."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None

    fm, body = parse_frontmatter(text)
    if not fm.get("title"):
        return None

    title = str(fm.get("title", ""))
    authors = fm.get("authors", [])
    if isinstance(authors, list):
        author_names = [
            (a.get("name") if isinstance(a, dict) else str(a)) for a in authors
        ]
    else:
        author_names = []

    date = str(fm.get("date", ""))
    year = int(date[:4]) if date and date[:4].isdigit() else None

    keywords = fm.get("keywords", fm.get("tags", []))
    if not isinstance(keywords, list):
        keywords = []

    abstract = fm.get("abstract", "") or extract_abstract(body)

    rel = path.relative_to(papers_dir)
    url = "/papers/" + slug_from_path(rel)

    return {
        "title": title,
        "authors": author_names,
        "category": fm.get("category", ""),
        "year": year,
        "date": date,
        "version": str(fm.get("version", "1.0")),
        "abstract": str(abstract)[:500],
        "url": url,
        "keywords": [str(k) for k in keywords],
        "license": str(fm.get("license", "")),
        "doi": str(fm.get("doi", "")) if fm.get("doi") else None,
        "raip": str(fm.get("raip", "")) if fm.get("raip") else None,
        "hasDataset": bool(fm.get("hasDataset", False)),
        "hasCode": bool(fm.get("hasCode", False)),
        "readingTimeMinutes": reading_time(body),
    }


def generate_index(papers_dir: Path, out_path: Path) -> list[dict]:
    papers = []
    md_files = sorted(papers_dir.rglob("*.md"))

    for path in md_files:
        entry = build_paper_entry(path, papers_dir)
        if entry:
            papers.append(entry)

    papers.sort(key=lambda p: (p.get("date") or ""), reverse=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(papers, indent=2, ensure_ascii=False), encoding="utf-8"
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
    args = parser.parse_args()

    papers_dir = Path(args.papers_dir)
    out_path = Path(args.out)

    if not papers_dir.is_dir():
        print(f"warning: papers directory not found: {papers_dir}", file=sys.stderr)
        papers_dir.mkdir(parents=True, exist_ok=True)

    papers = generate_index(papers_dir, out_path)
    print(f"Generated {len(papers)} paper(s) → {out_path}")


if __name__ == "__main__":
    main()
