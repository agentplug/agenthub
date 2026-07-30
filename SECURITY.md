# Security Model

## Trust model for agents

**Installed agents are trusted code.** When you install an agent with
`agenthub install <developer>/<agent>` or `ah.load_agent(...)`, its Python
code executes on your machine with your user's privileges — the same trust
class as installing a package with `pip`. AgentHub isolates agent
*dependencies* (each agent gets its own virtual environment) but does **not**
sandbox agent *code*.

Consequences:

- Only install agents from developers you trust, exactly as you would with
  pip packages. The GitHub namespace (`developer/agent-name`) is the
  identity: the code comes from `github.com/<developer>/<agent-name>`.
- An agent can read and write your files, make network requests, and spawn
  processes. Subprocess isolation bounds resource cleanup (timeouts kill the
  agent's whole process group), not capability.
- Knowledge injected into agents is validated for size and (optionally,
  see below) suspicious content, but agents decide what to do with it.

## Hardening in place

Within that trust model, AgentHub defends the *integrity of agent
resolution* — an installed agent should be exactly what its repository
contains, loaded from where it claims to be:

- **Path containment**: agent scripts are resolved with symlinks followed;
  a script that resolves outside its own agent directory is refused.
- **Storage discovery**: agent directories under `~/.agenthub/agents` that
  are symlinks escaping the storage root are ignored.
- **Post-clone validation**: a cloned repository must contain the required
  agent files (`agent.yaml`/`agent.yml` and `agent.py`/`agent.na`), and
  symlinks inside the clone that resolve outside it are rejected — the
  clone is deleted and installation fails.
- **Import hygiene**: loading an agent no longer leaves the agent's
  directory permanently on `sys.path` (limits accidental or deliberate
  module shadowing of the host process).
- **No shell interpolation**: git operations run with argument lists, never
  `shell=True`.
- **Install provenance**: every install records the resolved commit SHA,
  source URL, and timestamp in `.agenthub-install.json` inside the agent
  directory — the auditable identity of the code that runs.
- **Pinned installs**: `agenthub install developer/agent@<sha|tag|branch>`
  (and `ah.load_agent("developer/agent@...")`) checks out exactly that ref
  before validation; an unresolvable ref fails the install and removes the
  clone.

## Knowledge content strictness

`AGENTHUB_KNOWLEDGE_STRICT=1` turns the suspicious-content check for
injected knowledge (eval/exec/import/URL patterns) from a warning into a
validation error.

## Out of scope (today)

- Sandboxing agent code (containers, seccomp, capability restriction).
  Planned as a separate project phase; contributions welcome.
- Verifying repository *contents* beyond structure: installs are
  SHA-recorded and pinnable (see above), but there is no signature
  scheme yet.

## Reporting a vulnerability

Open a private security advisory on GitHub
(`github.com/agentplug/agenthub` → Security → Advisories) or contact the
maintainer listed in `pyproject.toml`.
