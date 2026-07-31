# ADR 0003: Typed error taxonomy with actionable suggestions

- Status: Accepted (recorded retroactively; decision and implementation
  from the 0.1.5 hardening arc, July 2026)
- Deciders: William Nguyen
- Related: `CONTRIBUTING.md` error-handling policy,
  `agenthub/core/tools/exceptions.py`, `agenthub/core/llm/errors.py`

## Context

Failures originally traveled as `{"error": str(e)}` dicts fabricated at
multiple layers, and callers detected conditions by matching message
text (`"not found" in str(e)`). Three parallel representations coexisted:
error dicts, a never-adopted `Result[T]` monad, and ad-hoc exceptions.

## Decision

- One taxonomy rooted at `AgentHubError`, which carries
  `suggestions` (user-actionable, rendered in `str()`) and `context`
  (machine-readable details like `execution_time`, `raw_response`).
  Subtrees: `AgentError` (solve/load/execution), `ToolError`,
  `ValidationError`, `InstallationError`, `KnowledgeError`,
  `ConfigurationError`, and the LLM tree (`LLMError` →
  `NoModelAvailableError` with per-provider probe results).
- Five binding rules (full text in CONTRIBUTING): interior catches only
  expected types; boundaries chain with `raise ... from e` and never
  fabricate success; no bare/silent excepts; control flow on types, not
  message text; degradation belongs to the consumer.
- Public-API behavior changes ship with a one-release deprecation shim
  (precedent: `CoreLLMService`, then `solve(raise_errors=...)`), and the
  shim reproduces the legacy shape byte-for-byte so existing callers are
  unaffected during the window.

## Consequences

- `solve()` is the reference implementation: handler raises
  `AgentSolveError`, engine passes it through, wrapper shim converts to
  the legacy dict until the next minor release, when raising becomes the
  only behavior.
- Errors teach: `NoModelAvailableError` tells the user exactly what was
  probed and three ways to fix it.
- Remaining debt is measured and registered (broad excepts in legacy
  paths, rag mypy exemption) rather than invisible.
