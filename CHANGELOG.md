# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Characterization test suite pinning the solve/executor/wrapper/AgentInfo
  contracts (including subprocess-isolated pins that `import agenthub`
  leaves global logging state untouched)
- Schema-aware file-path resolution: parameters declared `type: file`
  (or `path`/`file_path`/`filepath`) in agent.yaml are resolved against
  the agent directory then cwd

### Changed
- FrameworkSolveHandler raises typed `AgentSolveError` (with suggestions
  and `execution_time` context) instead of fabricating `{"error": ...}`
  dicts; the default `raise_errors=False` shim reproduces the legacy dicts
  byte-for-byte for one release
- LLM selection responses are parsed with the shared structured extractor
  (`core.llm.structured`) — prose/fence-wrapped JSON now parses instead of
  failing as "no selection"
- Library code no longer prints auto-install progress; it logs at INFO and
  the CLI configures logging. SDK users opt in via `agenthub.setup_logging()`
- `import agenthub` no longer disables third-party loggers; the MCP/HTTP
  suppression moved into `setup_logging()`, which the CLI always calls
- `list_python_versions` returns `[]` when discovery fails instead of a
  fabricated `["3.12", "3.11", ...]` list (the CLI already renders the
  empty case honestly)
- Coverage ratchet raised 35% → 45% (measured actual: 47%)

### Deprecated
- The legacy string file-path heuristic for parameters with no declared
  type (fires with a DeprecationWarning for one release; declare
  `type: file` to keep resolution)
- Positional arguments to methods with no declared interface (raw `args`
  tuple pass-through warns; becomes an AgentExecutionError next release)

### Removed
- **Breaking:** the phase-3.4 A2A protocol is gone —
  `core/communication/protocol.py` (agent cards, task/status/result
  messages), the router's `agent_message`/`agent_request`/
  `agent_response` wire types, and the capability registry. Agent-to-
  agent messaging had no consumers; composition is MCP tools. Decision
  recorded in `docs/adr/0002-communication-transport.md`; the monitoring
  WebSocket path (logs, progress, user input) is unchanged and no longer
  mypy-exempt
- **Breaking:** `MCPClient`, `MCPConnectionPool`, `AsyncToolExecutor`,
  and `ToolInjector` are gone from `agenthub.core` / `agenthub.core.mcp`.
  They served a never-functional execution path (per-call stdio
  subprocess with a fresh empty registry that could not see `@tool`
  registrations) and had no production callers — removed per the
  never-functional precedent, recorded in
  `docs/adr/0001-composition-execution-model.md`
- External tool assignment now has a single store (the registry's access
  manager); `AgentToolManager.agent_tools` no longer exists
- Unused `Result[T]` monad (`core/common/`), never-instantiated
  `SolveResult`, unreachable `{"query": args[0]}` parameter-guess
  fallbacks, and the dead `solve` branch in `AgentWrapper.__getattr__`
- Contract-less legacy tests (`test_project_structure.py` file-existence
  asserts); empty `tests/integration/` directory

### Fixed
- `AgentWrapper` facade: eleven copied AgentInfo fields became read-only
  property delegations (no drift), and the wrapper→executor tool-context
  JSON serialize→deserialize round-trip is gone
- The autouse WebSocket cleanup fixture nulled the singleton before trying
  to stop it, so no server was ever stopped; order fixed, cleanup errors
  logged instead of swallowed
- `test_enterprise_cleanup_workflow` no longer depends on the host
  machine's environment (installed-package probe stubbed)

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
