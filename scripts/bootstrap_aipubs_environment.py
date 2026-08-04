#!/usr/bin/env python3
"""
AIPubs.cloud Environment Bootstrap + Verification

Performs:
- repository root detection
- virtual environment verification
- requirements verification
- RAIP package structure checks
- package install (editable)
- Python compile checks
- import validation
- papers index script validation
- audit report generation

Reports:
    test-reports/bootstrap-audit/
        bootstrap-report.json
        bootstrap-report.txt
"""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

REPORT_DIR = ROOT / "test-reports" / "bootstrap-audit"

REQUIRED_FILES = [
    "requirements-dev.txt",
    "raip/__init__.py",
    "raip/core/__init__.py",
    "scripts/generate_papers_index.py",
]

REQUIRED_PACKAGES = [
    "cryptography",
    "yaml",
    "jsonschema",
    "pytest",
]

RAIP_IMPORTS = [
    "raip",
    "raip.core.hashing",
    "raip.core.canonicalize",
    "raip.core.signatures",
]


report = {
    "timestamp": datetime.now(timezone.utc)
    .isoformat()
    .replace("+00:00", "Z"),
    "root": str(ROOT),
    "checks": [],
}


def add(name, passed, details):
    report["checks"].append(
        {
            "check": name,
            "passed": passed,
            "details": details,
        }
    )


def run(cmd):
    try:
        result = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

        return (
            result.returncode == 0,
            result.stdout + result.stderr,
        )

    except Exception as exc:
        return False, str(exc)


def check_python():

    add(
        "python-version",
        True,
        sys.version,
    )


def check_venv():

    active = (
        ROOT / ".venv"
    ) in Path(sys.executable).parents

    add(
        "virtual-environment",
        active,
        sys.executable,
    )


def check_files():

    for item in REQUIRED_FILES:

        path = ROOT / item

        add(
            f"file-{item}",
            path.exists(),
            str(path),
        )


def check_dependencies():

    for package in REQUIRED_PACKAGES:

        try:
            module = importlib.import_module(package)

            add(
                f"dependency-{package}",
                True,
                getattr(
                    module,
                    "__version__",
                    "installed",
                ),
            )

        except Exception as exc:

            add(
                f"dependency-{package}",
                False,
                str(exc),
            )


def check_raip_imports():

    for module_name in RAIP_IMPORTS:

        try:

            importlib.import_module(module_name)

            add(
                f"import-{module_name}",
                True,
                "loaded",
            )

        except Exception as exc:

            add(
                f"import-{module_name}",
                False,
                str(exc),
            )


def check_compile():

    passed, output = run(
        [
            sys.executable,
            "-m",
            "compileall",
            "raip",
            "scripts",
        ]
    )

    add(
        "compile-python",
        passed,
        output[-1000:],
    )


def check_registry():

    script = ROOT / "scripts" / "generate_papers_index.py"

    passed, output = run(
        [
            sys.executable,
            str(script),
            "--help",
        ]
    )

    add(
        "papers-index-generator",
        passed,
        output[-500:],
    )


def check_pytest():

    passed, output = run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--version",
        ]
    )

    add(
        "pytest",
        passed,
        output.strip(),
    )


def install_editable():

    pyproject = ROOT / "pyproject.toml"

    if not pyproject.exists():

        pyproject.write_text(
            """
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "aipubs-raip"
version = "1.0.0"

[tool.setuptools.packages.find]
where = ["."]
""".strip()
        )

        add(
            "created-pyproject",
            True,
            str(pyproject),
        )

    passed, output = run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-e",
            ".",
        ]
    )

    add(
        "editable-install",
        passed,
        output[-1000:],
    )


def write_report():

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    (REPORT_DIR / "bootstrap-report.json").write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    lines = [
        "AIPubs.cloud Bootstrap Audit",
        "=" * 40,
        "",
    ]

    for item in report["checks"]:

        status = (
            "PASS"
            if item["passed"]
            else "FAIL"
        )

        lines.append(
            f"{status}: {item['check']}"
        )

        lines.append(
            f"  {item['details']}"
        )

    (REPORT_DIR / "bootstrap-report.txt").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main():

    print(
        "AIPubs.cloud bootstrap verification"
    )

    check_python()
    check_venv()
    check_files()

    install_editable()

    check_dependencies()
    check_raip_imports()
    check_compile()
    check_registry()
    check_pytest()

    write_report()

    failures = [
        x
        for x in report["checks"]
        if not x["passed"]
    ]

    print()
    print(
        f"Checks: {len(report['checks'])}"
    )
    print(
        f"Failures: {len(failures)}"
    )
    print()
    print(
        "Report:"
    )
    print(
        REPORT_DIR
    )

    sys.exit(
        1 if failures else 0
    )


if __name__ == "__main__":
    main()