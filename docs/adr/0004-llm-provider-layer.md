# ADR 0004: Provider-generalized LLM layer, local-first, never fabricating

- Status: Accepted (recorded retroactively; decision from the 0.1.5
  hardening arc)
- Deciders: William Nguyen
- Related: `agenthub/core/llm/`, `ARCHITECTURE.md` §LLM provider layer

## Context

`solve()` needs an LLM, but AgentHub users range from cloud-API shops to
fully local setups. The original implementation went through one vendor
SDK (aisuite), returned the literal string `"AISuite not available"` on
failure, and let fabricated content flow downstream as if generation had
succeeded.

## Decision

- **Provider-generalized layer**: `LLMService` → `ModelSelector` →
  `LLMProvider` implementations (Ollama, LM Studio, llama.cpp,
  OpenAI-compatible, cloud via LiteLLM). LiteLLM replaced the single-
  vendor SDK so cloud providers are configuration, not code.
- **Local-first detection**, lazy: probe Ollama → LM Studio → llama.cpp,
  then cloud keys; overridable via `AGENTHUB_LLM_MODEL` and
  `AGENTHUB_LLM_PROVIDER_PRIORITY`. Detection never happens at import or
  construction time.
- **Failures raise, never fabricate**: generation errors are typed
  (`LLMError` subtree) and consumers decide degradation. This is the
  rule that makes `solve()`'s error contract possible.
- **Shared mechanics in the base class**: JSON-mode emulation and
  reasoning-tag stripping live in `LLMProvider.chat()`; structured
  output recovery uses one extractor (`core/llm/structured.py`) across
  service, decision, and monitoring code.

## Consequences

- The LLM-outage behavior of `solve()` (fall back to the first declared
  method) is an explicit, logged consumer-side choice — currently kept
  for compatibility and queued for an opt-in flip.
- `CoreLLMService` remains as a one-release deprecated subclass; new
  code uses `LLMService` via `get_shared_llm_service()`.
