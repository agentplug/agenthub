# ADR 0002: Communication transport — WebSocket for monitoring, no A2A

- Status: Accepted
- Date: 2026-07-31
- Deciders: William Nguyen
- Related: `ARCHITECTURE.md` §Module map, `SECURITY.md` trust model

## Context

Phase 3.4 built a WebSocket subsystem with two ambitions fused together:

1. **Monitoring/user interaction** — streaming agent logs and progress to
   local clients, and routing user-input requests from agents to
   connected users. This is the only part with production consumers
   (`runtime/process_manager`, `monitoring/`).
2. **Agent-to-agent messaging** — a full A2A protocol (`protocol.py`:
   agent cards, task/status/result messages, adapter), a capability
   registry, and `agent_message`/`agent_request`/`agent_response` wire
   types in the router. No production consumers; agents in AgentHub
   compose through MCP tools, not by messaging each other.

The subsystem was exempt from mypy (24 errors) and its A2A half tracked
an external specification that is immature for this product: A2A targets
cross-organization interoperability while AgentHub's trust model is
trusted-code local execution (SECURITY.md); A2A authentication
correctness is currently the implementer's burden; the A2A WebSocket
binding itself is an experimental proposal.

## Decision

- **Amputate the A2A ambition.** Delete `core/communication/protocol.py`
  and its tests; remove the `agent_message`/`agent_request`/
  `agent_response` wire types, their router handlers, and the capability
  registry (`register_agent`/`discover_agents`). No external consumer
  used any of it.
- **Keep and harden the monitoring path.** `CommunicationServer`,
  `SessionManager`, and the router's session/user-input/status handling
  stay — they serve the monitoring contract. The package is no longer
  mypy-exempt: its errors are fixed (typing the websockets compat shim
  via `TYPE_CHECKING`, real `Optional`s, no unreachable code) and the
  override entries are removed from the debt register.
- **Revisit standards-based interop later.** If a real cross-agent
  interoperability requirement appears, evaluate A2A (or its successors)
  then — when the spec and its auth story are more mature, and when
  there is a user asking for it. Multi-agent orchestration with
  human-in-the-loop would be a new product contract designed fresh, not
  a revival of this code.

## Alternatives considered

- **Full removal, monitoring via SSE** — technically sufficient for
  one-way status streaming, but rewrites a working, tested
  (phase3.4 suite) path for no user-visible gain. WebSocket is also the
  defensible choice here: both ends are ours, latency matters, and
  user-input requests need server push.
- **Keep investing in A2A** — wrong trust model, immature spec, zero
  users, and it conflicts with the MCP composition story.
- **Shim the removed wire types** — nothing ever consumed them; there is
  no behavior to preserve.

## Consequences

- ~930 lines of protocol code and tests removed; the communication
  package drops from four modules to three with a single clear purpose.
- The mypy debt register loses all three `communication.*` entries
  (remaining: `rag.*`, `core.mcp.*`).
- The wire protocol no longer accepts agent-to-agent message types;
  hypothetical external clients using them would receive "Unknown
  message type". None are known to exist.
- Future orchestration work starts from requirements, not from this
  residue.
