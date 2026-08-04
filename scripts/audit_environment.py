#!/usr/bin/env python3
"""
AIPubs.cloud Development Environment Audit

Verifies:
- Python environment
- virtual environment
- dependencies
- RAIP package imports
- project structure
- compilation
- pytest availability
- publication index generator
- audit reports

Outputs:
    test-reports/environment-audit/
        audit-report.json
        audit-report.txt
"""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

REPORT_DIR = ROOT / "test-reports" / "environment-audit"

REQUIRED_PACKAGES = {
    "cryptography": "cryptography",
    "yaml": "PyYAML",
    "jsonschema": "jsonschema",
    "pytest": "pytest",
}

REQUIRED_PATHS = [
    "raip",
    "raip/core",
    "scripts",
    "research",
]


results = {
    "timestamp": datetime.now(timezone.utc)
    .isoformat()
    .replace("+00:00", "Z"),
    "project": "aipubs.cloud",
    "checks": [],
}


def record(name, passed, details):
    results["checks"].append(
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

        return (
            result.returncode == 0,
            result.stdout + result.stderr,
        )

    except Exception as exc:
        return False, str(exc)


def check_python():

    record(
        "python-version",
        True,
        sys.version,
    )


def check_venv():

    prefix = Path(sys.prefix)

    active = (
        ".venv" in str(prefix)
        or "venv" in str(prefix)
    )

    record(
        "virtual-environment",
        active,
        str(prefix),
    )


def check_packages():

    for module, label in REQUIRED_PACKAGES.items():

        try:
            imported = importlib.import_module(module)

            version = getattr(
                imported,
                "__version__",
                "installed",
            )

            record(
                f"package-{label}",
                True,
                version,
            )

        except Exception as exc:

            record(
                f"package-{label}",
                False,
                str(exc),
            )


def check_structure():

    for item in REQUIRED_PATHS:

        path = ROOT / item

        record(
            f"path-{item}",
            path.exists(),
            str(path),
        )


def check_raip():

    modules = [
        "raip",
        "raip.core.hashing",
        "raip.core.canonicalize",
        "raip.core.signatures",
    ]

    for module in modules:

        try:
            importlib.import_module(module)

            record(
                f"import-{module}",
                True,
                "loaded",
            )

        except Exception as exc:

            record(
                f"import-{module}",
                False,
                str(exc),
            )


def check_compile():

    passed, output = run_command(
        [
            sys.executable,
            "-m",
            "compileall",
            "raip",
            "scripts",
        ]
    )

    record(
        "python-compile",
        passed,
        output[-500:],
    )


def check_pytest():

    passed, output = run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "--version",
        ]
    )

    record(
        "pytest",
        passed,
        output.strip(),
    )


def check_registry_generator():

    generator = ROOT / "scripts" / "generate_papers_index.py"

    if not generator.exists():

        record(
            "registry-generator",
            False,
            "missing",
        )
        return

    passed, output = run_command(
        [
            sys.executable,
            str(generator),
            "--help",
        ]
    )

    record(
        "registry-generator",
        passed,
        output[-500:],
    )


def write_report():

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_file = REPORT_DIR / "audit-report.json"

    json_file.write_text(
        json.dumps(
            results,
            indent=2,
        ),
        encoding="utf-8",
    )

    lines = [
        "AIPubs.cloud Environment Audit",
        "=" * 40,
        "",
    ]

    for check in results["checks"]:

        status = (
            "PASS"
            if check["passed"]
            else "FAIL"
        )

        lines.append(
            f"{status}: {check['check']}"
        )

        lines.append(
            f"  {check['details']}"
        )

    (REPORT_DIR / "audit-report.txt").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main():

    print(
        f"Auditing {ROOT}"
    )

    check_python()
    check_venv()
    check_packages()
    check_structure()
    check_raip()
    check_compile()
    check_pytest()
    check_registry_generator()

    write_report()

    failed = [
        x
        for x in results["checks"]
        if not x["passed"]
    ]

    print()

    print(
        f"Checks: {len(results['checks'])}"
    )

    print(
        f"Failed: {len(failed)}"
    )

    print()

    print(
        "Report:"
    )

    print(
        REPORT_DIR
    )

    sys.exit(
        1 if failed else 0
    )


if __name__ == "__main__":
    main()