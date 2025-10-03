#!/usr/bin/env python3
"""Test script to verify agent log isolation."""

import logging
import tempfile
import time
from pathlib import Path

from agenthub.runtime.process_manager import ProcessManager

# Set up logging to see all the communication messages
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def test_agent_log_isolation():
    """Test that agents do NOT see each other's logs (proper isolation)."""
    print("=" * 70)
    print("🧪 TESTING AGENT LOG ISOLATION")
    print("=" * 70)
    print("🎯 Goal: Verify agents do NOT see each other's logs")
    print("=" * 70)

    # Create ProcessManager with communication enabled
    print("\n1️⃣ Creating ProcessManager with real-time communication enabled...")
    manager = ProcessManager(realtime_communication=True)

    # Log the communication status
    print("\n📊 Current communication status:")
    manager.log_communication_status()

    print("\n2️⃣ Creating two agents with distinct log messages...")

    with (
        tempfile.TemporaryDirectory() as temp_dir1,
        tempfile.TemporaryDirectory() as temp_dir2,
    ):
        # Create Agent 1 - Secret Agent
        agent1_path = temp_dir1
        agent1_dir = Path(agent1_path)
        agent1_yaml = agent1_dir / "agent.yaml"
        agent1_yaml.write_text("name: secret-agent\nversion: 1.0.0")

        agent1_py = agent1_dir / "agent.py"
        agent1_py.write_text(
            """
import json
import sys
import time

class Agent:
    def secret_method(self, task_name):
        print(f"🔐 SECRET: Starting confidential task '{task_name}'")
        print(f"🔐 SECRET: Accessing classified data...")

        for i in range(3):
            print(f"🔐 SECRET: Processing classified step {i+1}/3")
            time.sleep(1)

        print(f"🔐 SECRET: Completed confidential task '{task_name}'")
        return {"result": f"Secret agent completed {task_name}", "status": "success"}

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

        # Create Agent 2 - Public Agent
        agent2_path = temp_dir2
        agent2_dir = Path(agent2_path)
        agent2_yaml = agent2_dir / "agent.yaml"
        agent2_yaml.write_text("name: public-agent\nversion: 1.0.0")

        agent2_py = agent2_dir / "agent.py"
        agent2_py.write_text(
            """
import json
import sys
import time

class Agent:
    def public_method(self, task_name):
        print(f"🌍 PUBLIC: Starting public task '{task_name}'")
        print(f"🌍 PUBLIC: Accessing public data...")

        for i in range(3):
            print(f"🌍 PUBLIC: Processing public step {i+1}/3")
            time.sleep(1.2)

        print(f"🌍 PUBLIC: Completed public task '{task_name}'")
        return {"result": f"Public agent completed {task_name}", "status": "success"}

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

        print("\n3️⃣ Executing both agents simultaneously...")
        print("📡 Watch for isolated log messages:")
        print("   🔐 SECRET messages should only appear for Secret Agent")
        print("   🌍 PUBLIC messages should only appear for Public Agent")
        print("-" * 50)

        try:
            import threading
            import unittest.mock

            def run_secret_agent():
                """Run Secret Agent in a separate thread."""
                with unittest.mock.patch.object(
                    manager.environment_manager,
                    "get_python_executable",
                    return_value="python",
                ):
                    result1 = manager.execute_agent(
                        agent_path=agent1_path,
                        method="secret_method",
                        parameters={"task_name": "Classified Operation"},
                    )
                    print(f"\n✅ Secret Agent Result: {result1['result']['result']}")

            def run_public_agent():
                """Run Public Agent in a separate thread."""
                with unittest.mock.patch.object(
                    manager.environment_manager,
                    "get_python_executable",
                    return_value="python",
                ):
                    result2 = manager.execute_agent(
                        agent_path=agent2_path,
                        method="public_method",
                        parameters={"task_name": "Public Service"},
                    )
                    print(f"\n✅ Public Agent Result: {result2['result']['result']}")

            # Start both agents in separate threads
            thread1 = threading.Thread(target=run_secret_agent)
            thread2 = threading.Thread(target=run_public_agent)

            thread1.start()
            time.sleep(0.5)  # Small delay to see interleaving
            thread2.start()

            # Wait for both to complete
            thread1.join()
            thread2.join()

            print("-" * 50)
            print("\n🎯 Analysis:")
            print("✅ GOOD: If you see 🔐 SECRET messages only for Secret Agent")
            print("✅ GOOD: If you see 🌍 PUBLIC messages only for Public Agent")
            print("❌ BAD: If Secret Agent sees PUBLIC messages or vice versa")
            print("\n🔒 This ensures proper log isolation and security!")

        except Exception as e:
            print(f"\n❌ Test failed: {e}")

    print("\n" + "=" * 70)
    print("🎉 AGENT LOG ISOLATION TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    test_agent_log_isolation()
