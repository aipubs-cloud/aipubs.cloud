# Copilot Instructions — AIOL Engineering Mode

You are operating in **AIOL Engineering Mode** for this repository.

## Primary Directive

Generate code that is:
1. Modular and component-based
2. Strictly typed and contract-aware
3. Interface-driven for Kernel integration
4. Ethically guarded and auditable
5. Kairos-ready (context/time aware) when relevant

## Required Output Pattern for Feature Requests

When implementing a feature, provide:
1. Module breakdown
2. Data contracts/types
3. Interface definitions
4. Implementation
5. Validation/parsing logic
6. Tests (unit + contract/integration)
7. Risk and governance notes

## Architecture Rules

- Enforce single responsibility per module.
- Prefer composition over inheritance.
- Avoid hidden coupling; call out dependency risks.
- Keep adapters separate from core logic.

## Type & Contract Rules

- Use explicit types on exported functions/classes/interfaces.
- Use strict null-safe patterns.
- Prefer discriminated unions for state variants.
- Validate external inputs at boundaries.

## Kernel Interface Rules

When Kernel interaction exists:
- Define explicit interfaces.
- Declare capabilities required by each operation.
- Provide deterministic and idempotent command behavior where applicable.
- Include graceful fallback/error strategy.

## Ethical/Governance Rules

For AI-impacting or user-impacting logic:
- Add a risk annotation comment (`risk: low|medium|high`).
- Add misuse boundary checks.
- Avoid exposing secrets/PII in logs.
- Include audit-friendly event/log notes.
- Flag high-risk flows for human review.

## Kairos Integration Guidance

If feature context implies Kairos:
- Add context snapshot inputs.
- Add temporal/deferred execution considerations.
- Preserve decision trace metadata.
- Keep Kairos interactions behind adapter interfaces.

## Definition of Done (AIOL)

A task is complete when:
- Types compile cleanly
- Boundary validation exists
- Interfaces are explicit
- Tests cover happy-path and failure-path
- Risk/governance notes exist where relevant
