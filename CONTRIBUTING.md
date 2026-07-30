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
