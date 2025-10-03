#!/usr/bin/env python3
"""Test script to demonstrate real-time agent log streaming."""

import logging
import tempfile
from pathlib import Path

from agenthub.runtime.process_manager import ProcessManager

# Set up logging to see all the communication messages
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def test_realtime_log_streaming():
    """Test the real-time log streaming functionality."""
    print("=" * 60)
    print("🧪 TESTING REAL-TIME AGENT LOG STREAMING")
    print("=" * 60)

    # Test 1: Create ProcessManager with communication enabled
    print("\n1️⃣ Creating ProcessManager with real-time communication enabled...")
    manager = ProcessManager(realtime_communication=True)

    # Log the communication status
    print("\n📊 Current communication status:")
    manager.log_communication_status()

    # Test 2: Create a temporary agent that produces logs
    print("\n2️⃣ Creating temporary agent with logging output...")
    with tempfile.TemporaryDirectory() as temp_dir:
        agent_path = temp_dir
        agent_dir = Path(agent_path)

        # Create agent.yaml
        agent_yaml = agent_dir / "agent.yaml"
        agent_yaml.write_text("name: logging-test-agent\nversion: 1.0.0")

        # Create agent.py with logging output
        agent_py = agent_dir / "agent.py"
        agent_py.write_text(
            """
import json
import sys
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Agent:
    def test_method(self, param1):
        print(f"Starting execution with parameter: {param1}")

        # Simulate some work with logging
        for i in range(5):
            print(f"Processing step {i+1}/5...")
            logger.info(f"Processing step {i+1}/5")
            time.sleep(0.5)  # Simulate work

        print("Processing completed successfully")
        logger.info("Processing completed successfully")

        return {"result": f"Hello {param1}", "status": "success", "steps": 5}

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

        # Test 3: Execute agent and see the real-time log streaming
        print("\n3️⃣ Executing agent with real-time log streaming...")
        print("📡 Watch for real-time log messages below:")
        print("-" * 40)

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
                    parameters={"param1": "Real-time Logging"},
                )

            print("-" * 40)
            print(f"\n✅ Agent execution result: {result}")

        except Exception as e:
            print(f"\n❌ Agent execution failed: {e}")

    print("\n" + "=" * 60)
    print("🎉 REAL-TIME LOG STREAMING TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_realtime_log_streaming()
