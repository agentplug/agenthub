# ADR 0005: Manifest schema v1 — permissive today, precise errors

- Status: Accepted (recorded retroactively; decision from the 0.1.5
  hardening arc)
- Deciders: William Nguyen
- Related: `agenthub/core/agents/manifest.py`,
  [CREATING_AGENTS](../../CREATING_AGENTS.md)

## Context

`agent.yaml` is the distribution contract: it declares the agent's
typed interface, which `solve()` needs for method selection and which
install/load validation both depend on. Validation was ad-hoc dict
checking with generic "invalid manifest" failures.

## Decision

- A pydantic `AgentManifest` (schema v1) with `extra="allow"` at every
  level: unknown fields are preserved, never rejected. Existing agents
  must not become invalid as the schema evolves — tightening happens in
  future schema *versions* (`schema_version` field), never by breaking
  v1.
- Field-precise errors: validation reports exactly which field failed
  and why, via friendly messages, at both validation points (install
  time and load time share the same schema, so an agent that installs
  also loads).
- Parameter declarations carry a free-form `type` slot (default
  `"string"`); the file-path resolution feature keys off
  `file`/`path`/`file_path`/`filepath` values without constraining the
  vocabulary for everything else.

## Consequences

- The manifest is the load-bearing artifact of the whole system: it
  drives method selection, parameter mapping, file-path resolution, and
  tool requirements from one source.
- A future v2 can tighten (constrained type vocabulary, required
  descriptions) while v1 agents keep working.
