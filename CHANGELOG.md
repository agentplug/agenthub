# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.5] - 2026-07-30

Consolidation release: the full engineering-hardening arc.

### Added
- llama.cpp local provider; provider-generalized LLM layer (LiteLLM for cloud)
- Install provenance (.agenthub-install.json) and ref-pinned installs (user/agent@sha)
- Atomic agent installation (stage-then-swap; failed installs preserve the previous agent)
- Versioned pydantic manifest schema with field-precise errors
- SECURITY.md trust model + resolution hardening (symlink containment, post-clone validation)
- Typed AgentSolveError (opt-in raise_errors=True; dict shim for one release)
- AgentNotFoundError; error-handling policy (CONTRIBUTING.md)
- PEP 561 py.typed marker - shipped types now reach downstream checkers

### Changed
- aisuite replaced by LiteLLM; generation failures raise instead of returning fabricated strings
- Subprocess timeouts kill whole process groups; WebSocket server lifecycle managed
- mypy exemptions 20 -> 5 patterns; coverage gated in CI; honest CLAUDE.md/README claims
- mcp pinned <2.0.0; black pinned <26

### Removed
- Never-functional custom-solve path; DI container; import-broken subpackages
- Ten unused direct dependencies; legacy packaging files


### Changed
- `__version__` is now derived from package metadata (`pyproject.toml` is the
  single source of truth); the duplicate versions in `setup.py` and
  `agenthub/__init__.py` are gone.
- Development dependencies are declared once in
  `[project.optional-dependencies].dev`; the diverging `[dependency-groups]`
  section was removed.
- Project URLs corrected to point at `github.com/agentplug/agenthub`.

### Removed
- Legacy packaging files: `setup.py`, `setup.sh`, `setup.bat`, `setup.ps1`,
  `requirements.txt`, `MANIFEST.in` (the project builds with hatchling from
  `pyproject.toml`; install with `pip install agenthub-sdk` or
  `pip install -e ".[dev]"` for development).
- Dead code: `agenthub/core/agents/wrapper_old.py`,
  `agenthub/runtime/_deprecated/`,
  `agenthub/runtime/process_manager/_deprecated/`.

## [0.1.4] - 2026-03-06

Latest published release. See git history for details.
