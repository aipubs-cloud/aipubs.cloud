# AIPubs.cloud Development Setup Guide

## Overview

This document defines the development environment setup, dependency installation, package validation, and testing workflow for the AIPubs.cloud publication infrastructure.

The project contains:

* RAIP artifact provenance framework
* Publication registry generator
* Markdown research paper indexing pipeline
* CI validation tooling

---

# 1. Open the Codespace

Clone or open the repository:

```bash
cd /workspaces/aipubs.cloud
```

Confirm repository root:

```bash
pwd
```

Expected:

```text
/workspaces/aipubs.cloud
```

---

# 2. Initialize Python Environment

Confirm Python version:

```bash
python --version
```

Supported:

```text
Python 3.12+
```

Upgrade packaging tools:

```bash
python -m pip install --upgrade pip setuptools wheel
```

---

# 3. Install Development Dependencies

Install required packages:

```bash
python -m pip install \
    cryptography \
    PyYAML \
    jsonschema \
    pytest
```

Verify:

```bash
python -m pip freeze | grep -E "cryptography|PyYAML|jsonschema|pytest"
```

Expected packages:

```text
cryptography
PyYAML
jsonschema
pytest
```

---

# 4. Validate RAIP Package Loading

Do not execute package files directly.

Incorrect:

```bash
python raip/core/verifier.py
```

Correct:

```bash
python -m raip.core.verifier
```

Python package imports require the repository root to be the execution context.

---

# 5. Verify RAIP Core Imports

Run:

```bash
python - <<'PY'
import raip
import raip.core.hashing
import raip.core.canonicalize
import raip.core.signatures

print("RAIP core import successful")
PY
```

Expected:

```text
RAIP core import successful
```

---

# 6. Verify Available Signing API

Before importing RAIP signing functions, inspect the module:

```bash
python - <<'PY'
import raip.core.signatures as signatures

print(dir(signatures))
PY
```

Use only functions exported by the current implementation.

Example:

```python
from raip.core.signatures import verify_signature
```

Do not assume function names from previous versions.

---

# 7. Compile Check

Validate Python syntax:

```bash
python -m compileall raip scripts
```

Expected:

```text
Compilation successful
```

---

# 8. Run Test Suite

Install pytest if missing:

```bash
python -m pip install pytest
```

Run:

```bash
pytest -v
```

Do not execute pytest files directly:

Incorrect:

```bash
python tests/test_file.py
```

Correct:

```bash
pytest tests/test_file.py -v
```

---

# 9. Publication Registry Generator

Generate the publication index:

```bash
python scripts/generate_papers_index.py \
    --strict \
    --verbose
```

Expected output:

```text
Generated N paper(s) → research/papers/index.json
```

---

# 10. Registry Output Validation

Generated registry:

```text
research/papers/index.json
```

Expected structure:

```json
{
  "schemaVersion": "1.0",
  "generatedAt": "UTC timestamp",
  "generator": "aipubs-indexer",
  "count": 0,
  "papers": []
}
```

Each paper should contain:

```json
{
  "title": "",
  "authors": [],
  "artifactHash": "",
  "hashAlgorithm": "sha256",
  "url": ""
}
```

---

# 11. Registry Test Reports

Tests generate audit artifacts:

```text
test-reports/
└── latest/
    ├── generated-index.json
    ├── validation-report.json
    ├── sha-report.json
    ├── test-summary.json
    └── execution.log
```

These reports provide:

* registry validation evidence
* artifact hash verification
* execution logs
* CI debugging information

---

# 12. Common Errors

## Error

```text
ModuleNotFoundError: No module named 'raip'
```

Fix:

```bash
cd /workspaces/aipubs.cloud
python -m raip.core.verifier
```

---

## Error

```text
ModuleNotFoundError: No module named 'cryptography'
```

Fix:

```bash
python -m pip install cryptography
```

---

## Error

```text
ModuleNotFoundError: No module named 'pytest'
```

Fix:

```bash
python -m pip install pytest
```

---

## Error

```text
ImportError: cannot import name 'sign_state'
```

Cause:

The RAIP signing API changed.

Inspect:

```bash
python - <<'PY'
import raip.core.signatures as s
print(dir(s))
PY
```

Use the exported function names.

---

# 13. Recommended CI Pipeline

Every pull request should execute:

```text
Checkout
   |
Install dependencies
   |
Compile Python modules
   |
Run pytest
   |
Generate publication index
   |
Validate registry schema
   |
Upload reports
```

---

# 14. Development Completion Checklist

Before committing:

* [ ] `python -m compileall raip scripts`
* [ ] `pytest -v`
* [ ] `python scripts/generate_papers_index.py --strict`
* [ ] `research/papers/index.json` generated
* [ ] RAIP imports validated
* [ ] test reports reviewed

---

AIPubs.cloud development is considered healthy when the publication registry, RAIP provenance layer, and CI validation pipeline execute successfully from a clean environment.
