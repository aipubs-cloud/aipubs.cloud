#!/usr/bin/env python3
"""
AIPubs.cloud Repository Inventory Auditor

Creates a complete repository map:
- folders
- files
- Python packages
- workflows
- schemas
- tests
- dependencies
- git state
- reports

Output:
    test-reports/repo-inventory/
"""

from pathlib import Path
import json
import subprocess
import hashlib
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parent.parent

REPORT_DIR = ROOT / "test-reports" / "repo-inventory"


IGNORE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".cache",
}


def ensure_reports():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def sha256(path):
    h = hashlib.sha256()

    try:
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)

        return h.hexdigest()

    except Exception:
        return None


def git_command(args):
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        return result.stdout.strip()

    except Exception:
        return None


def scan_files():

    files = []

    for path in ROOT.rglob("*"):

        if any(part in IGNORE_DIRS for part in path.parts):
            continue

        if path.is_file():

            try:
                stat = path.stat()

                files.append(
                    {
                        "path": str(path.relative_to(ROOT)),
                        "size_bytes": stat.st_size,
                        "extension": path.suffix,
                        "sha256": sha256(path),
                    }
                )

            except Exception:
                pass

    return files


def build_tree():

    lines = []

    for path in sorted(ROOT.rglob("*")):

        if any(part in IGNORE_DIRS for part in path.parts):
            continue

        depth = len(path.relative_to(ROOT).parts)

        prefix = "    " * depth

        if path.is_dir():
            lines.append(
                f"{prefix}{path.name}/"
            )

        else:
            lines.append(
                f"{prefix}{path.name}"
            )

    return "\n".join(lines)


def classify(files):

    categories = {
        "python": [],
        "tests": [],
        "workflows": [],
        "schemas": [],
        "docs": [],
        "dependencies": [],
        "config": [],
    }


    for f in files:

        p = f["path"].lower()


        if p.endswith(".py"):
            categories["python"].append(f["path"])


        if "test" in p:
            categories["tests"].append(f["path"])


        if ".github/workflows" in p:
            categories["workflows"].append(f["path"])


        if "schema" in p:
            categories["schemas"].append(f["path"])


        if p.endswith(
            (
                ".md",
                ".rst",
                ".txt"
            )
        ):
            categories["docs"].append(f["path"])


        if Path(p).name in {
            "requirements.txt",
            "requirements-dev.txt",
            "pyproject.toml",
            "package.json",
            "package-lock.json",
        }:
            categories["dependencies"].append(f["path"])


        if p.endswith(
            (
                ".yaml",
                ".yml",
                ".json",
                ".toml",
                ".env.example",
            )
        ):
            categories["config"].append(f["path"])


    return categories


def write_reports(files, categories):

    inventory = {

        "generatedAt":
            datetime.now(timezone.utc).isoformat(),

        "repository":
            ROOT.name,

        "root":
            str(ROOT),

        "statistics":
            {
                "files":
                    len(files),

                "total_bytes":
                    sum(
                        x["size_bytes"]
                        for x in files
                    ),

                "python_files":
                    len(categories["python"]),

                "tests":
                    len(categories["tests"]),

                "workflows":
                    len(categories["workflows"]),
            },

        "categories":
            categories,

        "git":
            {
                "branch":
                    git_command(
                        [
                            "branch",
                            "--show-current"
                        ]
                    ),

                "status":
                    git_command(
                        [
                            "status",
                            "--short"
                        ]
                    ),

                "commit":
                    git_command(
                        [
                            "rev-parse",
                            "HEAD"
                        ]
                    ),
            },

        "files":
            files,
    }


    (REPORT_DIR / "repo_inventory.json").write_text(
        json.dumps(
            inventory,
            indent=2
        ),
        encoding="utf-8",
    )


    (REPORT_DIR / "tree.txt").write_text(
        build_tree(),
        encoding="utf-8",
    )


    (REPORT_DIR / "python_files.json").write_text(
        json.dumps(
            categories["python"],
            indent=2
        ),
        encoding="utf-8",
    )


    (REPORT_DIR / "dependency_files.json").write_text(
        json.dumps(
            categories["dependencies"],
            indent=2
        ),
        encoding="utf-8",
    )


    md = f"""
# AIPubs.cloud Repository Inventory Report

Generated:

{inventory['generatedAt']}


Repository:

{ROOT}


## Statistics

Files:
{len(files)}

Python Files:
{len(categories['python'])}

Tests:
{len(categories['tests'])}

Workflows:
{len(categories['workflows'])}


## Top-Level Structure

See:

tree.txt


## Dependency Files

{chr(10).join(categories['dependencies'])}


## Python Modules

{chr(10).join(categories['python'][:100])}


## Tests

{chr(10).join(categories['tests'][:100])}


## Schemas

{chr(10).join(categories['schemas'])}


## Git

Branch:

{inventory['git']['branch']}


Commit:

{inventory['git']['commit']}


Status:


{inventory['git']['status']}


"""


    (REPORT_DIR / "repo_report.md").write_text(
        md,
        encoding="utf-8",
    )


def main():

    print(
        f"Scanning {ROOT}"
    )

    ensure_reports()

    files = scan_files()

    categories = classify(files)

    write_reports(
        files,
        categories
    )


    print()

    print(
        "Repository inventory complete"
    )

    print(
        f"Reports: {REPORT_DIR}"
    )


if __name__ == "__main__":
    main()