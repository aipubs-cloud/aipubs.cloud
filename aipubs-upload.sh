#!/usr/bin/env bash

set -euo pipefail

VERSION="1.0"

usage() {
    cat <<'EOF'
Usage:
  ./aipubs-upload.sh path/to/publication

Environment:
  AIPUBS_REPO   Optional path to the aipubs.cloud repository root.
EOF
}

die() {
    echo "❌ $*" >&2
    exit 1
}

info() {
    echo "• $*"
}

ROOT_DIR="${AIPUBS_REPO:-}"
PUBLICATION_DIR="${1:-}"

echo "====================================="
echo " AIPubs Cloud Publisher v${VERSION}"
echo "====================================="

if [[ -z "${PUBLICATION_DIR}" ]]; then
    usage
    exit 1
fi

if [[ ! -d "${PUBLICATION_DIR}" ]]; then
    die "Publication folder not found: ${PUBLICATION_DIR}"
fi

if [[ -z "${ROOT_DIR}" ]]; then
    ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || true)"
fi

if [[ -z "${ROOT_DIR}" || ! -d "${ROOT_DIR}" ]]; then
    die "aipubs.cloud repository not found"
fi

PUBLICATION_DIR="$(cd "${PUBLICATION_DIR}" && pwd)"
ROOT_DIR="$(cd "${ROOT_DIR}" && pwd)"
PUB_SLUG="$(basename "${PUBLICATION_DIR}")"
TARGET_DIR="${ROOT_DIR}/research/papers/${PUB_SLUG}"
STAGING_ROOT="${ROOT_DIR}/research/.staging"
STAGING_DIR="${STAGING_ROOT}/${PUB_SLUG}"

info "[1/6] Checking repository..."
cd "${ROOT_DIR}"

info "[2/6] Validating publication structure..."
REQUIRED_FILES=("README.md" "publication.json")
for file in "${REQUIRED_FILES[@]}"; do
    [[ -f "${PUBLICATION_DIR}/${file}" ]] || die "Missing required file: ${file}"
done

if ! find "${PUBLICATION_DIR}" -maxdepth 1 -type f -name '*.md' | grep -q .; then
    die "Missing manuscript Markdown file"
fi

info "✓ Publication structure valid"
info "Title: $(python3 - <<'PY' "${PUBLICATION_DIR}"
import json
import sys
from pathlib import Path

manifest = json.loads((Path(sys.argv[1]).resolve() / "publication.json").read_text(encoding="utf-8"))
print(manifest.get("title", ""))
PY
)"
info "Version: $(python3 - <<'PY' "${PUBLICATION_DIR}"
import json
import sys
from pathlib import Path

manifest = json.loads((Path(sys.argv[1]).resolve() / "publication.json").read_text(encoding="utf-8"))
print(manifest.get("version", ""))
PY
)"

info "[3/6] Generating RAIP fingerprint..."
readarray -t PY_OUT < <(python3 - <<'PY' "${PUBLICATION_DIR}" "${ROOT_DIR}"
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import jsonschema

publication_dir = Path(sys.argv[1]).resolve()
root_dir = Path(sys.argv[2]).resolve()
manifest_path = publication_dir / "publication.json"
schema_path = root_dir / "schemas" / "publication.schema.json"

if not schema_path.exists():
    raise SystemExit(f"Missing RAIP publication schema: {schema_path}")

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
schema = json.loads(schema_path.read_text(encoding="utf-8"))
jsonschema.validate(manifest, schema)

manifest_bytes = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
manifest_hash = f"sha256:{hashlib.sha256(manifest_bytes).hexdigest()}"

parts = []
for path in sorted(publication_dir.rglob("*")):
    if not path.is_file():
        continue
    rel = path.relative_to(publication_dir)
    if rel.parts and rel.parts[0] == ".raip":
        continue
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    parts.append(f"{rel.as_posix()}::{digest}")

fingerprint = f"sha256:{hashlib.sha256('\n'.join(parts).encode('utf-8')).hexdigest()}"
created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
created_event = {
    "event": "created",
    "timestamp": created_at,
    "previous": None,
}
created_event_bytes = json.dumps(created_event, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
created_event_hash = f"sha256:{hashlib.sha256(created_event_bytes).hexdigest()}"
envelope = {
    "protocol": "RAIP-1.0",
    "canonicalization": "RAIP-C14N-1",
    "identity_scope": {
        "included": "publication-content",
        "excluded_paths": [".raip/*"],
    },
    "artifact": {
        "type": "publication",
        "slug": publication_dir.name,
        "title": manifest.get("title", ""),
        "version": manifest.get("version", ""),
        "manifest_hash": {
            "algorithm": "SHA-256",
            "value": manifest_hash,
        },
        "fingerprint": {
            "algorithm": "SHA-256",
            "scope": "publication-content",
            "value": fingerprint,
        },
    },
    "lifecycle": [
        {
            **created_event,
            "hash": created_event_hash,
        }
    ],
}

raip_dir = publication_dir / ".raip"
raip_dir.mkdir(parents=True, exist_ok=True)
(raip_dir / "envelope.json").write_text(json.dumps(envelope, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print(fingerprint)
print(manifest.get("title", ""))
print(manifest.get("version", ""))
PY
)

HASH="${PY_OUT[0]:-}"
MANIFEST_TITLE="${PY_OUT[1]:-}"
MANIFEST_VERSION="${PY_OUT[2]:-}"

[[ -n "${HASH}" ]] || die "Failed to compute fingerprint"
info "Artifact Content Fingerprint:"
echo "${HASH}"

info "[4/6] Creating RAIP metadata..."
info "✓ RAIP envelope created"

info "[5/6] Copying into research/papers registry..."
if [[ "${TARGET_DIR}" == "${ROOT_DIR}" ]]; then
    die "Refusing to overwrite repository root"
fi
if [[ "${TARGET_DIR}" == "${PUBLICATION_DIR}" ]]; then
    die "Source and destination cannot be identical"
fi
if [[ -e "${TARGET_DIR}" ]]; then
    die "Target publication already exists: ${TARGET_DIR}"
fi
mkdir -p "${STAGING_ROOT}" "${ROOT_DIR}/research/papers"
rm -rf "${STAGING_DIR}"
cp -R "${PUBLICATION_DIR}" "${STAGING_DIR}"
mv "${STAGING_DIR}" "${TARGET_DIR}"
info "✓ Added: research/papers/${PUB_SLUG}"

info "[6/6] Committing publication..."
git add "research/papers/${PUB_SLUG}"
if git diff --cached --quiet; then
    die "No changes detected. Publication already exists or no files were staged."
fi
git commit -m "RAIP publish: ${PUB_SLUG}"

echo
read -r -p "Push to origin/main? (y/n): " PUSH
if [[ "${PUSH}" == "y" ]]; then
    CURRENT_BRANCH="$(git branch --show-current)"
    [[ -n "${CURRENT_BRANCH}" ]] || CURRENT_BRANCH="main"
    git push origin "${CURRENT_BRANCH}"
    echo "🚀 Publication uploaded successfully"
else
    echo "Commit created locally."
    echo "Run: git push origin $(git branch --show-current 2>/dev/null || echo main)"
fi