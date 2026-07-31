# ADR 0001: Composition execution model — one in-process path, one assignment store

- Status: Accepted
- Date: 2026-07-31
- Deciders: William Nguyen
- Related: PR (composition convergence), `ARCHITECTURE.md` §Composition

## Context

Tool execution grew three parallel paths:

1. **In-process** — `ToolRegistry.execute_tool` calls the registered
   function directly. This is what `AgentWrapper.execute_tool` uses, and
   the only path that worked.
2. **MCP-over-stdio subprocess** — `AgentToolManager._ensure_client`
   spawned `python -c "...get_mcp_server().run_stdio()"`. The child
   process builds a fresh, empty `ToolRegistry`, so tools registered
   in-process via `@tool` were invisible on this path. It could never
   have worked for the primary use case, and it had no production
   callers — only mock-wired legacy tests.
3. **MCP-over-SSE** — used only for metadata discovery against a running
   `run_resources()` server.

Assignment state was likewise duplicated: `AgentToolManager.agent_tools`
(a dict on the manager) and `ToolAccessManager.agent_tool_access` (on the
registry) were both written by `AgentWrapper.assign_tools`, and
`add_external_tools` replaced one store while extending the other, so the
two could disagree about what an agent may use.

The supporting cast (`MCPClient`, `MCPConnectionPool`,
`AsyncToolExecutor`, `ToolInjector`, ~700 lines) existed only to serve
path 2 and had no production consumers.

## Decision

- **One execution path:** external tools execute in-process via
  `ToolRegistry.execute_tool`. `AgentToolManager.execute_tool` keeps its
  access check and error-JSON contract but delegates execution to the
  registry instead of spawning a subprocess.
- **One assignment store:** `ToolAccessManager` on the registry is the
  single source of truth; `AgentToolManager` delegates all external
  assignment reads/writes to it and keeps only built-in-tool state.
- **Delete the stdio machinery:** `mcp_client.py`,
  `connection_manager.py`, `async_tool_executor.py`, `tool_injector.py`
  and their tests. Same precedent as the never-functional custom-solve
  removal: code that cannot work does not get a deprecation shim.
- **Keep MCP for what it's good at:** the FastMCP server
  (`run_resources()`) for exposing tools, and the SSE discovery leg for
  metadata. The in-memory MCP round trip
  (`tests/core/mcp/test_tool_composition_e2e.py`) pins the protocol
  contract without network or subprocess.

## Consequences

- The composition contract (contract #4) works as documented for the
  first time; `AgentToolManager.execute_tool` is now a working,
  access-checked entry point rather than a broken placeholder.
- Importing `MCPClient`, `MCPConnectionPool`, `AsyncToolExecutor`, or
  `ToolInjector` from `agenthub.core` / `agenthub.core.mcp` now fails —
  an intentional breaking change in an 0.x release, called out in the
  changelog.
- Remote tool execution (an agent calling tools served by *another*
  process/host over MCP) is out of scope. When a real use case appears,
  the design should use a proper persistent client (or the in-memory
  session for same-process), never a per-call stdio spawn.
- `AgentWrapper.execute_tool` still bypasses the access check (it calls
  the registry directly). Tightening that is a separate authorization
  decision, not part of this convergence.

## Alternatives considered

- **Make the child import the parent's registrations** — requires
  pickling user functions or reconstructing import state in the child;
  fragile, and the path had no callers to justify the complexity.
- **Shim the stdio path for one release** — shims preserve behavior;
  there was no working behavior to preserve.
