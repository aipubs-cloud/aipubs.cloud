# GitHub Actions

AIPubs.cloud workflows are intentionally path-scoped so unrelated changes do not consume CI resources or create noisy checks.

## Trigger matrix

| Workflow | Pull requests / pushes | Scheduled | Manual | Primary scope |
|---|---|---|---|---|
| `raip-ci.yml` | Yes, path-filtered | No | No | `raip/**`, `pyproject.toml` |
| `raip-media-ci.yml` | Yes, path-filtered | No | No | `raip-media/**` |
| `validate-publication.yml` | PR only, path-filtered | No | No | `research/papers/**`, `research/datasets/**` |
| `generate-index.yml` | Main push, path-filtered | No | No | `research/papers/**`, index generator |
| `site-audit.yml` | PR, site-path-filtered | Daily | Yes | Site, blog, and audit code |

## Principles

1. **Run only when inputs can affect the result.** Use `paths`/`paths-ignore` before adding runtime conditionals.
2. **Separate unrelated test suites.** RAIP core and RAIP Media have independent workflows so a change to one does not execute the other's tests.
3. **Keep production monitoring periodic.** The site audit retains a daily production smoke test because production can drift independently of source changes.
4. **Keep manual recovery available where useful.** `workflow_dispatch` is appropriate for operational verification without creating an always-on trigger.
5. **Use least-privilege permissions.** Workflows should default to read-only repository access and request write access only when an automated artifact/PR genuinely requires it.
6. **Avoid automation loops.** Generated changes should not retrigger the workflow that generated them unless that validation is intentional.

## Current follow-up

- #45 tracks making the site audit run against the PR/local preview instead of production for code-change validation.
- #47 tracks the broader workflow trigger, job-scope, permission, and duplicate-work audit.
