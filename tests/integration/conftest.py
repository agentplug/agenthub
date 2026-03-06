"""Fixtures for integration tests.

Creates real agent directories on disk with proper structure
(agent.yaml + agent.py) so tests exercise the real loading pipeline.
"""

import shutil
import sys
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Minimal valid agent manifest (dict)
# ---------------------------------------------------------------------------
VALID_MANIFEST = {
    "name": "echo-agent",
    "version": "0.1.0",
    "description": "A minimal agent that echoes its input.",
    "author": "integration-tests",
    "license": "MIT",
    "python_version": "3.11+",
    "interface": {
        "methods": {
            "echo": {
                "description": "Return the input string back.",
                "parameters": {
                    "text": {
                        "type": "string",
                        "description": "Text to echo",
                        "required": True,
                    }
                },
                "returns": {"type": "string", "description": "Echoed text"},
            },
            "greet": {
                "description": "Return a greeting.",
                "parameters": {
                    "name": {
                        "type": "string",
                        "description": "Name to greet",
                        "required": True,
                    }
                },
                "returns": {"type": "string", "description": "Greeting message"},
            },
        }
    },
    "dependencies": [],
    "tags": ["test"],
}

# ---------------------------------------------------------------------------
# Minimal agent.py that reads JSON from argv, dispatches, prints JSON result.
# ---------------------------------------------------------------------------
AGENT_PY = '''\
#!/usr/bin/env python3
"""Minimal echo agent for integration tests."""
import json
import sys


class EchoAgent:
    def echo(self, text: str) -> str:
        return f"echo: {text}"

    def greet(self, name: str) -> str:
        return f"Hello, {name}!"


def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Expected exactly one JSON argument"}))
        sys.exit(1)

    try:
        input_data = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        print(json.dumps({"error": f"Bad JSON: {exc}"}))
        sys.exit(1)

    method = input_data.get("method")
    parameters = input_data.get("parameters", {})

    agent = EchoAgent()

    if method == "echo":
        result = agent.echo(parameters.get("text", ""))
        print(json.dumps({"result": result}))
    elif method == "greet":
        result = agent.greet(parameters.get("name", ""))
        print(json.dumps({"result": result}))
    else:
        print(json.dumps({"error": f"Unknown method: {method}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
'''


def _create_agent_dir(
    base: Path,
    namespace: str,
    agent_name: str,
    manifest: dict,
    agent_py: str,
    *,
    create_venv: bool = True,
) -> Path:
    """Create a fully-structured agent directory under *base*/agents/ns/name."""
    agent_dir = base / "agents" / namespace / agent_name
    agent_dir.mkdir(parents=True, exist_ok=True)

    # Write agent.yaml
    with open(agent_dir / "agent.yaml", "w") as fh:
        yaml.dump(manifest, fh)

    # Write agent.py
    with open(agent_dir / "agent.py", "w") as fh:
        fh.write(agent_py)
    (agent_dir / "agent.py").chmod(0o755)

    # Create a fake venv with a python symlink so structure validation passes
    if create_venv:
        if sys.platform == "win32":  # pyright: ignore[reportConstantRedefinition]
            bin_dir = agent_dir / ".venv" / "Scripts"
            python_name = "python.exe"
        else:
            bin_dir = agent_dir / ".venv" / "bin"
            python_name = "python"
        bin_dir.mkdir(parents=True, exist_ok=True)
        python_exe = bin_dir / python_name
        # Symlink to current interpreter so subprocess execution works
        python_exe.symlink_to(sys.executable)

    return agent_dir


# ---------------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def storage_dir() -> Generator[Path, None, None]:
    """Temporary directory that acts as ~/.agenthub for tests."""
    tmp = Path(tempfile.mkdtemp(prefix="agenthub_integ_"))
    try:
        yield tmp
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture()
def echo_agent_dir(storage_dir: Path) -> Path:
    """Create a valid echo-agent on disk and return its path."""
    return _create_agent_dir(
        storage_dir, "test-ns", "echo-agent", VALID_MANIFEST, AGENT_PY
    )


@pytest.fixture()
def local_storage(storage_dir: Path):
    """A LocalStorage instance pointing at the temporary directory."""
    from agenthub.storage.local_storage import LocalStorage

    return LocalStorage(base_dir=storage_dir)


@pytest.fixture()
def agent_loader(local_storage):
    """An AgentLoader wired to the temporary local storage."""
    from agenthub.core.agents.lifecycle.loader import AgentLoader

    return AgentLoader(storage=local_storage)


@pytest.fixture()
def loaded_agent_info(agent_loader, echo_agent_dir: Path):
    """Load the echo-agent through the real AgentLoader pipeline."""
    _ = echo_agent_dir  # fixture side-effect: creates agent dir on disk
    return agent_loader.load_agent("test-ns", "echo-agent")


@pytest.fixture()
def agent_wrapper(loaded_agent_info):
    """Create a real AgentWrapper from the loaded agent info (no runtime)."""
    from agenthub.core.agents.orchestration.wrapper import AgentWrapper

    return AgentWrapper(loaded_agent_info)


@pytest.fixture()
def agent_wrapper_with_runtime(loaded_agent_info, local_storage):
    """Create a real AgentWrapper backed by AgentRuntime for subprocess execution."""
    from agenthub.core.agents.orchestration.wrapper import AgentWrapper
    from agenthub.core.tools import get_tool_registry
    from agenthub.runtime.agent_runtime import AgentRuntime

    runtime = AgentRuntime(storage=local_storage)
    # Disable dynamic execution so the real subprocess path is used
    runtime.process_manager.use_dynamic_execution = False

    namespace = loaded_agent_info.get("namespace", "unknown")
    name = loaded_agent_info.get("name", "unknown")
    agent_id = f"{namespace}/{name}"

    return AgentWrapper(
        agent_info=loaded_agent_info,
        runtime=runtime,
        tool_registry=get_tool_registry(),
        agent_id=agent_id,
    )
