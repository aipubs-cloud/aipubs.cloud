#!/usr/bin/env python3
"""Generate papers.json search index from Markdown frontmatter.

Scans research/papers/ for Markdown files containing YAML frontmatter,
extracts metadata, computes artifact hashes, and writes a consolidated JSON
registry index.

Usage:
    python scripts/generate_papers_index.py
    python scripts/generate_papers_index.py --out public/papers.json
    python scripts/generate_papers_index.py --strict --verbose
"""

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


try:
    import yaml
except ImportError:
    print(
        "error: PyYAML is required. Install with: pip install PyYAML",
        file=sys.stderr,
    )
    sys.exit(1)


_PAPERS_DIR = Path(__file__).parent.parent / "research" / "papers"
_DEFAULT_OUT = _PAPERS_DIR / "index.json"
_WORDS_PER_MINUTE = 200
_SCHEMA_VERSION = "1.0"


def log(message: str, verbose: bool) -> None:
    """Write verbose messages to stderr."""
    if verbose:
        print(message, file=sys.stderr)


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Extract YAML frontmatter and Markdown body."""

    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff")

    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)

    if len(parts) < 3:
        return {}, text

    yaml_text = parts[1]
    body = parts[2].lstrip("\n")

    try:
        metadata = yaml.safe_load(yaml_text) or {}
    except yaml.YAMLError:
        return {}, text

    if not isinstance(metadata, dict):
        metadata = {}

    return metadata, body


def reading_time(body: str) -> int:
    """Estimate reading time in minutes."""

    words = len(body.split())
    return max(1, math.ceil(words / _WORDS_PER_MINUTE))


def slug_from_path(path: Path, papers_dir: Path) -> str:
    """Create stable URL slug from paper path."""

    relative = path.relative_to(papers_dir).with_suffix("")

    slug = "-".join(relative.parts).lower()

    slug = slug.replace("_", "-")
    slug = slug.replace(" ", "-")

    slug = re.sub(
        r"[^a-z0-9-]+",
        "-",
        slug,
    )

    return slug.strip("-")


def extract_abstract(body: str) -> str:
    """Extract abstract section or fallback paragraph."""

    match = re.search(
        r"^##\s+Abstract\s*$\n+(.*?)(\n\n|\Z)",
        body,
        re.MULTILINE | re.DOTALL,
    )

    if match:
        text = match.group(1).strip()
        text = re.sub(r"\s+", " ", text)
        return text[:500]

    for paragraph in body.split("\n\n"):
        paragraph = paragraph.strip()

        if paragraph and not paragraph.startswith("#"):
            return re.sub(r"\s+", " ", paragraph)[:500]

    return ""


def compute_sha256(path: Path) -> str:
    """Compute SHA-256 artifact fingerprint."""

    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            digest.update(chunk)

    return digest.hexdigest()


def normalize_authors(value: Any) -> List[str]:
    """Normalize author metadata."""

    if isinstance(value, list):
        return [
            str(author["name"])
            if isinstance(author, dict) and author.get("name") is not None
            else str(author)
            for author in value
            if not isinstance(author, dict) or author.get("name") is not None
        ]

    if isinstance(value, str):
        return [value]

    return []


def normalize_keywords(value: Any) -> List[str]:
    """Normalize keyword metadata."""

    if isinstance(value, list):
        return [str(item) for item in value]

    if isinstance(value, str):
        return [value]

    return []


def build_paper_entry(
    path: Path,
    papers_dir: Path,
    strict: bool = False,
    verbose: bool = False,
) -> Dict[str, Any] | None:
    """Build registry entry from Markdown paper."""

    try:
        text = path.read_text(
            encoding="utf-8"
        )

    except OSError as error:

        message = f"Cannot read {path}: {error}"

        if strict:
            raise RuntimeError(message)

        log(message, verbose)
        return None


    metadata, body = parse_frontmatter(text)


    title = str(
        metadata.get("title", "")
    ).strip()


    if not title:

        message = f"Missing title: {path}"

        if strict:
            raise ValueError(message)

        log(message, verbose)

        return None


    date = str(
        metadata.get("date", "")
    ).strip()


    year = (
        int(date[:4])
        if date[:4].isdigit()
        else None
    )


    keywords = normalize_keywords(
        metadata.get(
            "keywords",
            metadata.get("tags", []),
        )
    )


    abstract = (
        metadata.get("abstract")
        or extract_abstract(body)
    )


    abstract = str(
        abstract
    ).strip()[:500]


    abstract_html = (
        metadata.get("abstractHtml")
        or metadata.get("abstract_html")
    )


    artifact_hash = compute_sha256(path)


    return {
        "title": title,
        "authors": normalize_authors(
            metadata.get("authors", [])
        ),
        "category": metadata.get(
            "category",
            "",
        ),
        "year": year,
        "date": date,
        "version": str(
            metadata.get(
                "version",
                "1.0",
            )
        ),
        "abstract": abstract,
        "abstractHtml": (
            str(abstract_html)
            if abstract_html
            else None
        ),
        "url": (
            "/papers/"
            + slug_from_path(
                path,
                papers_dir,
            )
        ),
        "keywords": keywords,
        "license": str(
            metadata.get(
                "license",
                "",
            )
        ),
        "doi": (
            str(metadata["doi"])
            if metadata.get("doi")
            else None
        ),
        "raip": (
            str(metadata["raip"])
            if metadata.get("raip")
            else None
        ),
        "hasDataset": bool(
            metadata.get(
                "hasDataset",
                False,
            )
        ),
        "hasCode": bool(
            metadata.get(
                "hasCode",
                False,
            )
        ),
        "readingTimeMinutes": reading_time(body),
        "artifactHash": artifact_hash,
        "hashAlgorithm": "sha256",
    }


def generate_index(
    papers_dir: Path,
    output_path: Path,
    strict: bool = False,
    verbose: bool = False,
) -> List[Dict[str, Any]]:
    """Generate complete publication registry."""

    papers: List[Dict[str, Any]] = []

    markdown_files = sorted(
        papers_dir.rglob("*.md")
    )


    for paper in markdown_files:

        entry = build_paper_entry(
            paper,
            papers_dir,
            strict=strict,
            verbose=verbose,
        )

        if entry:
            papers.append(entry)


    papers.sort(
        key=lambda item: (
            item.get("date") or "",
            item.get("title", "").lower(),
        ),
        reverse=True,
    )


    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    generated_at = (
        datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


    payload = {
        "schemaVersion": _SCHEMA_VERSION,
        "generatedAt": generated_at,
        "generator": "aipubs-indexer",
        "count": len(papers),
        "papers": papers,
    }


    output_path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


    return papers


def main() -> None:

    parser = argparse.ArgumentParser(
        description=__doc__
    )


    parser.add_argument(
        "--papers-dir",
        default=str(_PAPERS_DIR),
        help=f"Papers directory (default: {_PAPERS_DIR})",
    )


    parser.add_argument(
        "--out",
        default=str(_DEFAULT_OUT),
        help=f"Output path (default: {_DEFAULT_OUT})",
    )


    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on invalid papers.",
    )


    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )


    args = parser.parse_args()


    papers_dir = Path(
        args.papers_dir
    )

    output_path = Path(
        args.out
    )


    if not papers_dir.exists():

        print(
            f"warning: papers directory missing: {papers_dir}",
            file=sys.stderr,
        )

        papers_dir.mkdir(
            parents=True,
            exist_ok=True,
        )


    papers = generate_index(
        papers_dir,
        output_path,
        strict=args.strict,
        verbose=args.verbose,
    )


    print(
        f"Generated {len(papers)} paper(s) → {output_path}"
    )


if __name__ == "__main__":
    main()