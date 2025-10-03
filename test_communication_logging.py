#!/usr/bin/env python3
"""Test script to demonstrate ProcessManager communication logging."""

import logging
import tempfile
from pathlib import Path

from agenthub.runtime.process_manager import ProcessManager

# Set up logging to see all the communication messages
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def test_communication_logging():
    """Test the communication logging functionality."""
    print("=" * 60)
    print("🧪 TESTING PROCESSMANAGER COMMUNICATION LOGGING")
    print("=" * 60)

    # Test 1: Create ProcessManager with communication enabled
    print("\n1️⃣ Creating ProcessManager with real-time communication enabled...")
    manager = ProcessManager(realtime_communication=True)

    # Log the communication status
    print("\n📊 Current communication status:")
    manager.log_communication_status()

    # Test 2: Create a temporary agent for testing
    print("\n2️⃣ Creating temporary agent for testing...")
    with tempfile.TemporaryDirectory() as temp_dir:
        agent_path = temp_dir
        agent_dir = Path(agent_path)

        # Create agent.yaml
        agent_yaml = agent_dir / "agent.yaml"
        agent_yaml.write_text("name: test-agent\nversion: 1.0.0")

        # Create agent.py
        agent_py = agent_dir / "agent.py"
        agent_py.write_text(
            """
import json
import sys

class Agent:
    def test_method(self, param1):
        return {"result": f"Hello {param1}", "status": "success"}

if __name__ == "__main__":
    data = json.loads(sys.argv[1])
    method = data["method"]
    parameters = data["parameters"]

    agent = Agent()
    if hasattr(agent, method):
        result = getattr(agent, method)(**parameters)
        print(json.dumps(result))
    else:
        print(json.dumps({"error": f"Unknown method: {method}"}))
"""
        )

        # Test 3: Execute agent and see the logging
        print("\n3️⃣ Executing agent with communication logging...")
        try:
            # Mock environment manager to avoid venv requirements
            import unittest.mock

            with unittest.mock.patch.object(
                manager.environment_manager,
                "get_python_executable",
                return_value="python",
            ):
                result = manager.execute_agent(
                    agent_path=agent_path,
                    method="test_method",
                    parameters={"param1": "World"},
                )

            print(f"\n✅ Agent execution result: {result}")

        except Exception as e:
            print(f"\n❌ Agent execution failed: {e}")

    # Test 4: Test disabling communication
    print("\n4️⃣ Testing communication disable/enable...")
    manager.set_realtime_communication(False)
    manager.log_communication_status()

    manager.set_realtime_communication(True)
    manager.log_communication_status()

    print("\n" + "=" * 60)
    print("🎉 COMMUNICATION LOGGING TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_communication_logging()
