"""Shared test configuration and fixtures for all tests."""

import asyncio
import logging
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

logger = logging.getLogger(__name__)


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path)


@pytest.fixture
def sample_agent_manifest() -> dict:
    """Sample agent manifest for testing."""
    return {
        "name": "test-agent",
        "version": "1.0.0",
        "description": "Test agent for unit testing",
        "author": "test",
        "license": "MIT",
        "python_version": "3.11+",
        "interface": {
            "methods": {
                "test_method": {
                    "description": "Test method",
                    "parameters": {
                        "input": {
                            "type": "string",
                            "description": "Test input",
                            "required": True,
                        }
                    },
                    "returns": {"type": "string", "description": "Test output"},
                }
            }
        },
        "dependencies": ["pytest"],
        "tags": ["test"],
    }


@pytest.fixture
def mock_agent_directory(temp_dir: Path, sample_agent_manifest: dict) -> Path:
    """Create a mock agent directory structure for testing."""
    agent_dir = temp_dir / "agents" / "test" / "test-agent"
    agent_dir.mkdir(parents=True)

    # Create agent.yaml
    import yaml

    with open(agent_dir / "agent.yaml", "w") as f:
        yaml.dump(sample_agent_manifest, f)

    # Create simple agent.py with a class
    agent_py_content = """#!/usr/bin/env python3
import json
import sys

class TestAgent:
    def test_method(self, input: str) -> str:
        return f"Test output: {input}"

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Invalid arguments"}))
        sys.exit(1)

    try:
        input_data = json.loads(sys.argv[1])
        method = input_data.get("method")
        parameters = input_data.get("parameters", {})

        agent = TestAgent()
        if method == "test_method":
            result = agent.test_method(parameters.get("input", ""))
            print(json.dumps({"result": result}))
        else:
            print(json.dumps({"error": f"Unknown method: {method}"}))
            sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
"""

    with open(agent_dir / "agent.py", "w") as f:
        f.write(agent_py_content)

    # Make agent.py executable
    (agent_dir / "agent.py").chmod(0o755)

    return agent_dir


@pytest.fixture(autouse=True)
def cleanup_websocket_servers():
    """Automatically clean up WebSocket servers between tests."""
    yield  # Run the test

    try:
        from agenthub.core.communication.server import CommunicationServer
    except ImportError:
        return  # WebSocket module not available, nothing to clean

    # Stop a running server BEFORE resetting the singleton — previously the
    # instance was nulled first, making the stop logic unreachable
    server = getattr(CommunicationServer, "_instance", None)
    if server is not None and getattr(server, "is_running", False):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(server.stop())
            loop.close()
        except Exception as e:
            logger.debug(f"WebSocket server cleanup failed: {e}")

    CommunicationServer._instance = None
    CommunicationServer._initialized = False
