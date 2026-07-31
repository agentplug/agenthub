# Architecture

AgentHub is an SDK for distributing and invoking AI agents. Agents are
GitHub-hosted packages described by an `agent.yaml` manifest, installed
with one line (`ah.load_agent("user/agent")`), and invoked in natural
language (`agent.solve("goal")`). This document maps the internal
pipeline and the contracts that hold it together. It describes structure,
not usage.

See also: [README](README.md) (product tour),
[CREATING_AGENTS](CREATING_AGENTS.md) (the agent-author contract),
[SECURITY](SECURITY.md) (trust model),
[CONTRIBUTING](CONTRIBUTING.md) (error-handling and test policy).

## The pipeline

```
agent.yaml (manifest: interface.methods, typed parameters)
  → AgentLoader.load_agent              agenthub/core/agents/loader.py:96
  → AgentManifest (pydantic schema v1)  agenthub/core/agents/manifest.py:61
  → AgentInfo                           agenthub/core/agents/agent_info.py:6
  → AgentWrapper                        agenthub/core/agents/wrapper.py:21
  → solve(): SolveEngine                agenthub/core/agents/solve/engine.py:14
    → FrameworkSolveHandler             agenthub/core/agents/solve/framework_handler.py:16
      (one LLM call selects the method and extracts its parameters)
  → MethodExecutor                      agenthub/core/agents/method_executor.py:18
    (parameter mapping, schema-aware file-path resolution)
  → AgentRuntime / ProcessManager       agenthub/runtime/agent_runtime.py:37
    → Executor (per-agent venv subprocess)
      agenthub/runtime/process_manager/executor.py:182
```

Direct method calls skip the solve stage: `AgentWrapper.__getattr__`
(wrapper.py:432) dispatches any declared method onto the same
MethodExecutor → runtime path.

## The four contracts

The system is organized around four promises. Tests should protect these,
not incidental structure.

### 1. Install — a GitHub repo becomes a local agent

`load_agent()` (agenthub/sdk/load_agent.py:15) loads from local storage;
a typed `AgentNotFoundError` (loader.py:14, never string-matching)
triggers auto-install. `AutoInstaller.install_agent`
(agenthub/github/auto_installer.py:101) runs a fixed sequence: parse spec
(`name@ref` pins) → clone → validate → create venv → install deps.
Installs are atomic (stage-then-swap, so a failed install preserves the
previous agent) and record provenance (`.agenthub-install.json`). Agents
live at `~/.agenthub/agents/<namespace>/<name>` (storage/local_storage.py).

### 2. Invocation — a declared interface, callable two ways

The manifest's `interface.methods` is the agent's public API. Both entry
points converge on `MethodExecutor.execute` (method_executor.py:25):
`solve()` lets an LLM select the method and extract parameters from a
natural-language query; `agent.method(...)` dynamic dispatch calls it
directly. Parameter mapping is positional-by-declared-order when a schema
exists; file-path resolution applies only to parameters whose manifest
type is `file`/`path`/`file_path`/`filepath`. Across the process
boundary the contract is JSON: the agent reads `{"method", "parameters"}`
from argv and writes `{"result" | "error"}` to stdout (the agent-author
side is specified in [CREATING_AGENTS](CREATING_AGENTS.md)).

### 3. Isolation — dependencies, not capability

Each agent gets its own virtual environment (environment/environment_setup.py),
so agents cannot conflict over dependency versions. Execution happens in
a subprocess started with `start_new_session=True`; a timeout kills the
whole process group (executor.py:334). This bounds dependency and
resource cleanup only — agent code runs with the user's privileges. The
trust boundary is defined in [SECURITY](SECURITY.md) and not restated
here.

### 4. Composition — tools and knowledge attach to any agent

Functions become tools via `@tool` (agenthub/core/tools/decorator.py:8),
which registers them in the process-wide `ToolRegistry`
(agenthub/core/tools/registry.py:43) and onto the FastMCP server served
by `run_resources()` (registry.py:496). `AgentToolManager`
(agenthub/core/mcp/agent_tool_manager.py:50) computes what an agent may
use (enabled built-ins + assigned external tools). Knowledge text
injected via `wrapper.inject_knowledge()` flows into the solve context.
`solve()` itself is a single LLM call that sees method names,
descriptions, and parameter schemas — which is why the manifest's typed
interface is the load-bearing artifact of the whole system.

## LLM provider layer

`LLMService` (agenthub/core/llm/service.py:30) is the composition root.
`ModelSelector` (llm/selection.py:31) probes providers in priority order
— Ollama → LM Studio → llama.cpp → cloud (LiteLLM) — lazily, overridable
via `AGENTHUB_LLM_MODEL` / `AGENTHUB_LLM_PROVIDER_PRIORITY`. Providers
implement `LLMProvider` (llm/base.py:63); the shared `chat()` template
method handles JSON-mode emulation and reasoning-tag stripping.
Structured JSON is recovered with one shared extractor
(llm/structured.py:17). Generation failures raise typed errors — the
layer never fabricates content, and `NoModelAvailableError` reports
exactly what was probed and how to fix it.

## Error model

Nearly all errors descend from `AgentHubError`
(agenthub/core/tools/exceptions.py:6), which carries `suggestions`
(user-actionable, rendered in `str()`) and `context` (machine-readable,
e.g. `execution_time`, `raw_response`). The main subtrees are `AgentError`
(`AgentSolveError`, `AgentLoadError` → `AgentNotFoundError`,
`AgentExecutionError`), `ToolError`, and the LLM tree
(agenthub/core/llm/errors.py:13). The policy (full text in
[CONTRIBUTING](CONTRIBUTING.md)):

1. Interior code catches only what it expects; everything else propagates.
2. Boundaries may catch broadly, but must log with `exc_info=True` or
   chain with `raise ... from e`, re-raise domain errors unchanged, and
   never fabricate success values.
3. No bare `except:`, no silent `pass`.
4. Control flow runs on exception types, never message text.
5. Fallback behavior belongs to the consumer; library code raises.

`solve()` is the reference implementation: the handler raises
`AgentSolveError`, the engine re-raises it unchanged, and the wrapper's
`raise_errors=False` shim (one release) converts it back to the legacy
`{"error", "execution_time"}` dict for existing callers.

## Module map

| Directory | Responsibility | Key anchors |
|---|---|---|
| `agenthub/sdk/` | Public entry point | `load_agent.py:15` |
| `agenthub/core/agents/` | Manifest, loader, wrapper, executor | `manifest.py:61`, `loader.py:96`, `wrapper.py:21` |
| `agenthub/core/agents/solve/` | LLM method selection | `engine.py:14`, `framework_handler.py:16` |
| `agenthub/core/llm/` | Provider-generalized LLM layer | `service.py:30`, `base.py:63`, `errors.py:13` |
| `agenthub/core/tools/` | `@tool`, registry, FastMCP server | `decorator.py:8`, `registry.py:43` |
| `agenthub/core/mcp/` | Agent-side tool access/execution | `agent_tool_manager.py:50` |
| `agenthub/core/knowledge/` | Knowledge injection/storage | `manager.py:12` |
| `agenthub/core/interfaces/` | `typing.Protocol` seams (cycle-breaking) | `agent_interfaces.py` |
| `agenthub/runtime/` | Subprocess execution, process lifecycle | `agent_runtime.py:16` |
| `agenthub/github/` | Clone, validate, auto-install, provenance | `auto_installer.py:101` |
| `agenthub/environment/` | Per-agent venv setup/maintenance | `environment_setup.py:99` |
| `agenthub/storage/` | `~/.agenthub` local storage | `local_storage.py:9` |
| `agenthub/cli/` | Click CLI (configures logging, owns the process) | `main.py` |

## Known limitations (honest list)

- `AgentToolManager.execute_tool` for external tools spawns a stdio
  subprocess that builds a fresh, empty `ToolRegistry`; tools registered
  in-process via `@tool` are invisible on that path. The working
  composition legs today are in-process execution
  (`ToolRegistry.execute_tool`, registry.py:303) and the MCP protocol
  against the running server. Tracked as a defect; do not build on the
  stdio path.
- A few exception types predate the taxonomy and inherit plain
  `Exception` (`InterfaceValidationError` in validator.py, `CloneError`
  in github/, `EnvironmentSetupError` in environment/); they are caught
  by name at their boundaries.
- `solve()` still returns legacy error dicts under the default
  `raise_errors=False` shim; raising becomes the only behavior in the
  next minor release.
- When no LLM is reachable, `solve()` falls back to the first declared
  method rather than failing — kept for compatibility, queued for an
  explicit opt-in.

## Out of scope here

RAG tool internals, the realtime WebSocket/A2A communication subsystem,
and the CLI command surface (see [README](README.md)).
