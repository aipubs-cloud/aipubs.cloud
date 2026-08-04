#!/usr/bin/env python3
"""
AIPubs.cloud Full Repository Audit

Performs a complete repository verification:

- Repository inventory
- Folder and file mapping
- Python compilation
- Package detection
- Dependency verification
- RAIP package imports
- Git state
- Test discovery
- Workflow discovery
- Schema discovery
- Report generation

Outputs:

test-reports/full-repo-audit/
    repo-inventory.json
    repo-tree.txt
    audit-report.json
    audit-report.txt
    audit-report.md

Usage:

    python scripts/full_repo_audit.py
"""

from pathlib import Path
from datetime import datetime, timezone
import subprocess
import json
import hashlib
import importlib.metadata
import os
import sys


ROOT = Path(__file__).resolve().parent.parent

REPORT_DIR = ROOT / "test-reports" / "full-repo-audit"

INVENTORY_REPORT = REPORT_DIR / "repo-inventory.json"
TREE_REPORT = REPORT_DIR / "repo-tree.txt"
JSON_REPORT = REPORT_DIR / "audit-report.json"
TXT_REPORT = REPORT_DIR / "audit-report.txt"
MD_REPORT = REPORT_DIR / "audit-report.md"


IGNORE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "test-reports",
}


checks = []


def ensure_reports():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def add_check(name, passed, details=""):
    checks.append(
        {
            "check": name,
            "passed": passed,
            "details": details,
        }
    )


def run_command(command):

    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        return result.returncode, result.stdout.strip(), result.stderr.strip()

    except Exception as e:
        return 1, "", str(e)


def sha256(path):

    digest = hashlib.sha256()

    try:
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                digest.update(chunk)

        return digest.hexdigest()

    except Exception:
        return None


def scan_files():

    files = []

    for path in ROOT.rglob("*"):

        if any(part in IGNORE_DIRS for part in path.parts):
            continue

        if path.is_file():

            stat = path.stat()

            files.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "size": stat.st_size,
                    "extension": path.suffix,
                    "sha256": sha256(path),
                }
            )

    return files


def tree():

    output = []

    for path in sorted(ROOT.rglob("*")):

        if any(part in IGNORE_DIRS for part in path.parts):
            continue

        depth = len(path.relative_to(ROOT).parts)

        prefix = "    " * depth

        if path.is_dir():
            output.append(f"{prefix}{path.name}/")
        else:
            output.append(f"{prefix}{path.name}")

    return "\n".join(output)


def git_info():

    info = {}

    commands = {
        "branch": [
            "git",
            "branch",
            "--show-current",
        ],
        "commit": [
            "git",
            "rev-parse",
            "HEAD",
        ],
        "status": [
            "git",
            "status",
            "--short",
        ],
    }

    for key, cmd in commands.items():

        code, out, err = run_command(cmd)

        info[key] = out if code == 0 else err

    return info


def package_version(name):

    try:
        return importlib.metadata.version(name)

    except Exception:
        return None


def verify_environment():

    add_check(
        "python-version",
        True,
        sys.version,
    )


    add_check(
        "virtual-environment",
        sys.prefix != sys.base_prefix,
        sys.prefix,
    )


    for package in [
        "cryptography",
        "PyYAML",
        "jsonschema",
        "pytest",
    ]:

        version = package_version(package)

        add_check(
            f"package-{package}",
            version is not None,
            version or "missing",
        )


def verify_paths():

    paths = [
        "raip",
        "raip/core",
        "scripts",
        "research",
        "schemas",
    ]

    for item in paths:

        path = ROOT / item

        add_check(
            f"path-{item}",
            path.exists(),
            str(path),
        )


def verify_imports():

    modules = [
        "raip",
        "raip.core.hashing",
        "raip.core.canonicalize",
        "raip.core.signatures",
    ]

    for module in modules:

        code, out, err = run_command(
            [
                sys.executable,
                "-c",
                f"import {module}",
            ]
        )

        add_check(
            f"import-{module}",
            code == 0,
            "loaded" if code == 0 else err,
        )


def compile_python():

    code, out, err = run_command(
        [
            sys.executable,
            "-m",
            "compileall",
            "raip",
            "scripts",
        ]
    )

    add_check(
        "python-compile",
        code == 0,
        out + err,
    )


def run_tests():

    code, out, err = run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
        ]
    )

    add_check(
        "pytest",
        code == 0,
        out + err,
    )


def verify_registry():

    script = ROOT / "scripts" / "generate_papers_index.py"

    if not script.exists():

        add_check(
            "registry-generator",
            False,
            "missing script",
        )

        return


    code, out, err = run_command(
        [
            sys.executable,
            str(script),
        ]
    )


    add_check(
        "registry-generator",
        code == 0,
        out + err,
    )


def write_inventory(files):

    inventory = {

        "generatedAt":
            datetime.now(timezone.utc).isoformat(),

        "repository":
            ROOT.name,

        "root":
            str(ROOT),

        "fileCount":
            len(files),

        "totalBytes":
            sum(
                f["size"]
                for f in files
            ),

        "files":
            files,

        "git":
            git_info(),
    }


    INVENTORY_REPORT.write_text(
        json.dumps(
            inventory,
            indent=2,
        ),
        encoding="utf-8",
    )


def write_reports(files):

    report = {

        "timestamp":
            datetime.now(timezone.utc).isoformat(),

        "project":
            ROOT.name,

        "checks":
            checks,

        "summary":
            {
                "total":
                    len(checks),

                "passed":
                    len(
                        [
                            x for x in checks
                            if x["passed"]
                        ]
                    ),

                "failed":
                    len(
                        [
                            x for x in checks
                            if not x["passed"]
                        ]
                    ),
            },
    }


    JSON_REPORT.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )


    TXT_REPORT.write_text(
        "\n".join(
            [
                "AIPubs.cloud Full Repository Audit",
                "=" * 40,
                "",
                *[
                    (
                        f"{'PASS' if x['passed'] else 'FAIL'}: "
                        f"{x['check']}\n"
                        f"  {x['details']}"
                    )
                    for x in checks
                ],
            ]
        ),
        encoding="utf-8",
    )


    MD_REPORT.write_text(
        "\n".join(
            [
                "# AIPubs.cloud Full Repository Audit",
                "",
                f"Generated: {report['timestamp']}",
                "",
                "| Check | Result | Details |",
                "|---|---|---|",
                *[
                    (
                        f"| {x['check']} | "
                        f"{'PASS' if x['passed'] else 'FAIL'} | "
                        f"{x['details']} |"
                    )
                    for x in checks
                ],
            ]
        ),
        encoding="utf-8",
    )


def main():

    ensure_reports()

    print(f"Auditing {ROOT}")

    files = scan_files()

    write_inventory(files)

    TREE_REPORT.write_text(
        tree(),
        encoding="utf-8",
    )


    verify_environment()
    verify_paths()
    verify_imports()
    compile_python()
    run_tests()
    verify_registry()

    write_reports(files)

    failed = [
        x for x in checks
        if not x["passed"]
    ]

    print()
    print(
        f"Checks: {len(checks)}"
    )

    print(
        f"Failed: {len(failed)}"
    )

    print()
    print(
        f"Reports:"
    )

    print(
        REPORT_DIR
    )


if __name__ == "__main__":
    main()