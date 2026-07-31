# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Breaking (behavior):** when no LLM is reachable, `solve()` now raises
  `AgentSolveError` ("No LLM available to select a method", carrying the
  LLM layer's probe diagnostics) instead of silently running the first
  declared method with empty parameters and reporting it as success. The
  fabricated selection was the exact anti-pattern the error policy forbids.
  Under the default `raise_errors=False` shim this surfaces as the legacy
  `{"error": ...}` dict; opt back into the old behavior per call with
  `solve(..., fallback_first_method=True)`.

## [0.1.6] - 2026-07-31

Hardening arc: typed errors completed, composition converged, A2A
ambition amputated, architecture documented. Suite fully green at ~49%
coverage (enforced floor 45%); mypy exemptions down to one.

Note: typed `AgentSolveError` was documented in 0.1.5's changelog but
the code landed after the tag — it ships in this release, reconciling
the notes with reality.

### Added
- `ARCHITECTURE.md`: the pipeline, the four product contracts, the LLM
  layer, and the error model on one page, with file:line anchors
- Decision records in `docs/adr/` (0001 composition execution model,
  0002 communication transport, 0003 typed error taxonomy, 0004 LLM
  provider layer, 0005 manifest schema v1) and a dated debt burn-down
  schedule in CONTRIBUTING.md
- Characterization test suite pinning the solve/executor/wrapper/AgentInfo
  contracts (including subprocess-isolated pins that `import agenthub`
  leaves global logging state untouched), an end-to-end solve-contract
  suite, and a real MCP composition round trip (in-memory client↔server,
  zero network, zero mocks)
- Schema-aware file-path resolution: parameters declared `type: file`
  (or `path`/`file_path`/`filepath`) in agent.yaml are resolved against
  the agent directory then cwd

### Changed
- FrameworkSolveHandler raises typed `AgentSolveError` (with suggestions
  and `execution_time` context) instead of fabricating `{"error": ...}`
  dicts; the default `raise_errors=False` shim reproduces the legacy dicts
  (same keys and message) for one release
- LLM selection responses are parsed with the shared structured extractor
  (`core.llm.structured`) — prose/fence-wrapped JSON now parses instead of
  failing as "no selection"
- External tool execution converged on one in-process path and one
  assignment store (ADR 0001); `AgentToolManager.execute_tool` keeps its
  access check and now works
- Library code no longer prints auto-install progress; it logs at INFO and
  the CLI configures logging. SDK users opt in via `agenthub.setup_logging()`
- `import agenthub` no longer disables third-party loggers; the MCP/HTTP
  suppression moved into `setup_logging()`, which the CLI always calls
- `list_python_versions` returns `[]` when discovery fails instead of a
  fabricated `["3.12", "3.11", ...]` list (the CLI already renders the
  empty case honestly)
- Coverage ratchet raised 35% → 45% (measured actual: 49%)
- mypy exemption register: 5 entries → 1 (`rag.*` remains; `core.mcp.*`
  and all three `communication.*` removed and their errors fixed)
- pre-commit mypy environment declares `websockets>=12`, matching
  pyproject (it previously resolved an older layout and disagreed with dev)

### Deprecated
- The legacy string file-path heuristic for parameters with no declared
  type (fires with a DeprecationWarning; declare `type: file` to keep
  resolution) — **flips in 0.2.0**
- Positional arguments to methods with no declared interface (raw `args`
  tuple pass-through warns; becomes an AgentExecutionError) — **flips in 0.2.0**
- `solve()` error dicts under `raise_errors=False` (DeprecationWarning;
  catching `AgentSolveError` becomes the only behavior) — **flips in 0.2.0**

### Removed
- **Breaking:** the phase-3.4 A2A protocol is gone —
  `core/communication/protocol.py` (agent cards, task/status/result
  messages), the router's `agent_message`/`agent_request`/
  `agent_response` wire types, and the capability registry. Agent-to-
  agent messaging had no consumers; composition is MCP tools (ADR 0002);
  the monitoring WebSocket path is unchanged
- **Breaking:** `MCPClient`, `MCPConnectionPool`, `AsyncToolExecutor`,
  and `ToolInjector` — along with the `get_mcp_client` and
  `get_tool_injector` helpers exported from `agenthub.core` — are gone
  from `agenthub.core` / `agenthub.core.mcp`. They served a
  never-functional execution path (per-call stdio subprocess with a fresh
  empty registry that could not see `@tool` registrations) and had no
  production callers (ADR 0001)
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
- `add_external_tools` replaced the assignment store while extending the
  local list, so the two disagreed; now union semantics in both
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
