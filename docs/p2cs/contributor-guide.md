# P2CS Contributor Guide

This guide explains how to extend P2CS by adding new synthesis engines, parsers, language adapters, or validation plugins.

---

## Adding a Synthesis Engine

A synthesis engine transforms a `SemanticGraph` into one or more `ComponentManifest` objects.

### Step 1 — Implement `ISynthesisEngine`

```python
# my_org/my_engine.py
from p2cs.synthesis import ISynthesisEngine
from p2cs.contracts import ComponentManifest, SemanticGraph, SupportedLanguage
from typing import List

class MyExtractionEngine(ISynthesisEngine):
    @property
    def engine_id(self) -> str:
        return "my-org.my-engine-v1"

    @property
    def supported_languages(self) -> List[SupportedLanguage]:
        return ["python", "typescript"]

    def synthesize(
        self,
        graph: SemanticGraph,
        language: SupportedLanguage,
        confidence_threshold: float = 0.7,
    ) -> List[ComponentManifest]:
        # Your extraction logic here.
        # Return [] if confidence_threshold is not met.
        return []
```

### Step 2 — Create a Plugin Descriptor

```json
{
  "schema_version": "1.0.0",
  "plugin_id": "my-org.my-engine-v1",
  "name": "My Extraction Engine",
  "version": "1.0.0",
  "language": "python",
  "entrypoint": "my_org.my_engine:MyExtractionEngine",
  "hooks": [
    {
      "event": "synthesis.requested",
      "handler": "synthesize",
      "priority": 50
    }
  ],
  "capabilities": ["synthesis.generate"]
}
```

Save it as `.aiol/plugins/my-engine.plugin.json`.

### Step 3 — Register the Plugin

Add an entry to `.aiol/plugins/registry.yml`:

```yaml
plugins:
  - plugin_id: my-org.my-engine-v1
    manifest_path: .aiol/plugins/my-engine.plugin.json
    enabled: true
```

The P2CS pipeline will discover and invoke your engine on the next run.

---

## Adding a Language Adapter

```python
from p2cs.synthesis import ILanguageAdapter
from p2cs.contracts import ComponentManifest, SupportedLanguage

class RustAdapter(ILanguageAdapter):
    @property
    def language(self) -> SupportedLanguage:
        return "rust"

    def render(self, manifest: ComponentManifest) -> str:
        # Return Rust source code as a string
        return f"// {manifest.name}\n"
```

Register via the same plugin descriptor mechanism, using `synthesis.requested` hook with `language: rust`.

---

## Adding a Parser

```python
from p2cs.parsing import IPublicationParser
from p2cs.contracts import PublicationManifest

class LatexParser(IPublicationParser):
    @property
    def supported_format(self) -> str:
        return "latex"

    def parse(self, manifest: PublicationManifest) -> PublicationManifest:
        # Read manifest.source_path, populate sections/equations/algorithms
        return manifest
```

Register on the `publication.parsed` hook.

---

## Adding a Validation Plugin

```python
from p2cs.validation import IValidationPlugin, ValidationReport

class MyComplianceCheck(IValidationPlugin):
    def on_validation_completed(self, report: ValidationReport, artifact) -> ValidationReport:
        # Add custom checks
        return report
```

Register on the `validation.completed` hook.

---

## Provenance Requirements

Every plugin that generates or modifies an artifact **must** call `DefaultProvenanceEngine.attach()` and set `integrity_hash` before emitting the artifact. Artifacts without provenance will be rejected by the Validation stage.

```python
from p2cs.provenance import DefaultProvenanceEngine
from p2cs.contracts import WorkflowContext

engine = DefaultProvenanceEngine()
context = WorkflowContext(
    workflow_id="my-workflow",
    workflow_version="1.0.0",
    repository_commit=os.environ.get("GITHUB_SHA", ""),
)
provenance = engine.attach(artifact, publication_manifest, context, "my-engine-id", "1.0.0")
artifact.provenance = provenance
```

---

## Testing Your Plugin

1. Write unit tests in a `tests/` directory alongside your plugin.
2. Import `p2cs.contracts` types directly — no mocks required for contract types.
3. Run: `pytest` from the repository root.

See `p2cs/tests/` for reference test patterns.

---

## Risk Annotation

Every module that touches synthesis or external data must include a `# risk: low|medium|high` comment at the top. High-risk modules require explicit human review in the PR before merge.

---

## Governance

- All synthesised code must pass through the Publish workflow's draft PR gate.
- No generated code is merged to `main` without human review.
- The RAIP provenance chain must remain intact from publication through to every generated artifact.
