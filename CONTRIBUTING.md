# Contributing to AgentHub

## Development setup

```bash
git clone https://github.com/agentplug/agenthub.git
cd agenthub
uv sync --extra dev --extra rag
pre-commit install
```

## Workflow

- Branch from `develop`; open PRs against `develop` (`main` tracks releases).
- One concern per PR. Conventional-commit messages (`fix(runtime): ...`).
- CI gates every PR: `ruff`, `black`, `mypy agenthub/` (must stay green —
  see the exemption note in `pyproject.toml`), and `pytest` with a coverage
  floor that only ratchets upward.

## Error-handling policy

The historical pattern of `except Exception: log-and-continue` made
failures silent and debugging archaeology. New and touched code follows
these rules:

1. **Interior code catches only what it expects.** Filesystem work catches
   `OSError`; YAML parsing catches `yaml.YAMLError`; subprocess calls catch
   `subprocess.SubprocessError`; AgentHub logic catches the typed
   `AgentHubError` subclasses. Everything else propagates — an unexpected
   exception is a bug report, not noise to suppress.

2. **Boundary handlers may catch `Exception` — with obligations.** A
   boundary is a place where an exception must become a value: the top of
   a public API call (`load_agent`, `install_agent`), the edge of a
   subprocess/CLI/tool execution, or an availability probe for an optional
   feature. Boundary handlers must (a) log with `exc_info=True` or convert
   to a typed error/result carrying the cause (`raise X(...) from e`),
   (b) re-raise domain exceptions unchanged rather than re-wrapping them,
   and (c) never fabricate a success value. Good examples:
   `AutoInstaller.install_agent`, `RepositoryCloner.clone_agent`.

3. **Never bare `except:`; never silent `pass`.** Where ignoring an error
   is genuinely correct, use `contextlib.suppress(SpecificError)` with a
   comment saying why.

4. **Control flow runs on types, not message text.** Matching on
   `str(e)` contents is forbidden — define an exception subclass instead
   (see `AgentNotFoundError`, which replaced a `"not found" in str(e)`
   check).

5. **Fallback behavior belongs to the consumer.** Library code raises;
   the caller decides whether to degrade, retry, or surface. Returning a
   fake value in place of an error (the old `"AISuite not available"`
   string) is the pattern this policy exists to prevent.

The ~190 remaining blanket handlers predate this policy and are being
narrowed subsystem by subsystem; do not add new ones.

## Debt burn-down schedule

Debt is registered with dates and paid on a schedule, not swept when
someone feels energetic. The register lives in three places: blanket
handlers (below), mypy exemptions (`pyproject.toml`), and the coverage
ratchet (`.github/workflows/test.yml`). All three are ratchets: the
numbers may only shrink.

| Item | Measured | Target | Release |
|---|---|---|---|
| `core.mcp.*` mypy exemption (15 errors) | 2026-07-31 | removed | 0.1.6 (done) |
| `communication.*` mypy exemptions (24 errors) | 2026-07-31 | removed | 0.1.6 (done) |
| Coverage floor 35% | 2026-07-30 | 45% | 0.1.6 (done) |
| `rag.*` mypy exemption (27 errors, untyped `llama_index`) | 2026-07-31 | register empty: typed facade or per-line ignores | 0.1.7 |
| Silent SDK auto-install (progress logs at INFO; invisible to SDK users who never call `setup_logging()`) | 2026-07-31 | document, or emit a default handler for install progress | 0.1.7 |
| String-typed path params bypass the deprecation shim (heuristic resolution dropped with no warning when a param declares `type: string`) | 2026-07-31 | audit first-party manifests; warn on the declared-string case | 0.1.7 |
| Blanket `except Exception` handlers | ~190 (2026-07-30) | ≤120, sweeping `github/` + `environment/` first | 0.1.8 |
| Legacy-dict `solve()` shim, file-path heuristic, raw positional-args pass-through | — | flipped/removed as promised | 0.2.0 |
| Blanket handlers | ~190 | ≤60 | 0.2.0 |
| phase2.5 mock-wiring tests | 277 tests | converted to behavioral or retired on touch | continuous |

Rules: never add new exemptions, never lower the coverage floor, never
add new blanket handlers. A missed target moves the date, never the goal.

## Tests

- Unit tests must be hermetic: no network, no live LLMs, no wall-clock
  dependence. Gate anything that needs a real server behind
  `@pytest.mark.integration` and an explicit env var.
- New tests mirror the package layout under `tests/<package-path>/`
  (the phase-named directories are frozen history).
- Temporary debug files use the semantic prefixes from `CLAUDE.md`
  (`verify_*`, `debug_*`) and are deleted before commit.

## Security

Agent execution is trusted-code-by-design; read `SECURITY.md` before
touching the installer, cloner, storage, or executor paths — resolution
integrity (symlink containment, post-clone validation) is enforced and
tested in `tests/security/`.
