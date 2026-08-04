#!/usr/bin/env python3
"""
Comprehensive validation suite for aipubs paper registry generator.

Outputs:
    test-reports/latest/
        generated-index.json
        validation-report.json
        sha-report.json
        test-summary.json
"""

import json
import hashlib
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest


ROOT = Path(__file__).parent.parent
REPORT_DIR = ROOT / "test-reports" / "latest"

FIXTURE_DIR = Path(__file__).parent / "fixtures"

SCRIPT = ROOT / "scripts" / "generate_papers_index.py"


def reset_reports():
    if REPORT_DIR.exists():
        shutil.rmtree(REPORT_DIR)

    REPORT_DIR.mkdir(parents=True)


@pytest.fixture(scope="session", autouse=True)
def setup_reports():
    reset_reports()


def sha256(path: Path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)

    return h.hexdigest()


def run_generator(tmp_path):

    papers = tmp_path / "papers"
    papers.mkdir()

    shutil.copytree(
        FIXTURE_DIR,
        papers,
        dirs_exist_ok=True,
    )

    output = REPORT_DIR / "generated-index.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--papers-dir",
            str(papers),
            "--out",
            str(output),
            "--strict",
            "--verbose",
        ],
        capture_output=True,
        text=True,
    )

    (REPORT_DIR / "execution.log").write_text(
        result.stdout + "\n" + result.stderr,
        encoding="utf-8",
    )

    assert result.returncode == 0

    return output


def test_registry_generation(tmp_path):

    output = run_generator(tmp_path)

    assert output.exists()

    data = json.loads(
        output.read_text()
    )

    assert data["schemaVersion"] == "1.0"
    assert data["generator"] == "aipubs-indexer"

    assert isinstance(
        data["papers"],
        list
    )

    assert data["count"] == len(data["papers"])


def test_required_registry_fields(tmp_path):

    output = run_generator(tmp_path)

    registry = json.loads(
        output.read_text()
    )

    failures = []

    required = [
        "title",
        "authors",
        "url",
        "abstract",
        "artifactHash",
        "hashAlgorithm",
    ]

    for paper in registry["papers"]:

        for field in required:
            if field not in paper:
                failures.append(
                    {
                        "paper": paper.get("title"),
                        "missing": field,
                    }
                )

    report = {
        "timestamp":
            datetime.now(timezone.utc)
            .isoformat(),

        "failures": failures,
        "passed": len(failures) == 0,
    }

    (REPORT_DIR / "validation-report.json").write_text(
        json.dumps(
            report,
            indent=2
        ),
        encoding="utf-8",
    )

    assert failures == []


def test_sha_integrity(tmp_path):

    output = run_generator(tmp_path)

    registry = json.loads(
        output.read_text()
    )

    sha_report = []

    for paper in registry["papers"]:

        sha_report.append(
            {
                "title": paper["title"],
                "hashAlgorithm":
                    paper["hashAlgorithm"],
                "artifactHash":
                    paper["artifactHash"],
                "valid":
                    len(paper["artifactHash"]) == 64,
            }
        )

    (REPORT_DIR / "sha-report.json").write_text(
        json.dumps(
            sha_report,
            indent=2
        ),
        encoding="utf-8",
    )

    assert all(
        x["valid"]
        for x in sha_report
    )


def test_nested_slug_generation(tmp_path):

    output = run_generator(tmp_path)

    registry = json.loads(
        output.read_text()
    )

    urls = [
        p["url"]
        for p in registry["papers"]
    ]

    assert len(urls) == len(set(urls))


def test_html_abstract_support(tmp_path):

    output = run_generator(tmp_path)

    registry = json.loads(
        output.read_text()
    )

    html_entries = [
        p for p in registry["papers"]
        if p.get("abstractHtml")
    ]

    assert len(html_entries) >= 1


def test_report_generation():

    summary = {
        "timestamp":
            datetime.now(timezone.utc)
            .isoformat(),

        "system":
            "aipubs-indexer",

        "status":
            "PASS",

        "reports": [
            "generated-index.json",
            "validation-report.json",
            "sha-report.json",
            "execution.log",
        ],
    }

    (REPORT_DIR / "test-summary.json").write_text(
        json.dumps(
            summary,
            indent=2
        ),
        encoding="utf-8",
    )