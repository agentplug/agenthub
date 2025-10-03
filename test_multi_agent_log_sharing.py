#!/usr/bin/env python3
"""Test script to demonstrate multi-agent real-time log sharing via WebSocket."""

import logging
import tempfile
import time
from pathlib import Path

from agenthub.runtime.process_manager import ProcessManager

# Set up logging to see all the communication messages
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def test_multi_agent_log_sharing():
    """Test if multiple agents can see each other's logs in real-time."""
    print("=" * 70)
    print("🧪 TESTING MULTI-AGENT REAL-TIME LOG SHARING")
    print("=" * 70)

    # Create ProcessManager with communication enabled
    print("\n1️⃣ Creating ProcessManager with real-time communication enabled...")
    manager = ProcessManager(realtime_communication=True)

    # Log the communication status
    print("\n📊 Current communication status:")
    manager.log_communication_status()

    print("\n2️⃣ Creating two agents that will run simultaneously...")

    # Create temporary directories that won't be cleaned up immediately
    temp_dir1 = tempfile.mkdtemp()
    temp_dir2 = tempfile.mkdtemp()

    try:
        # Create Agent 1
        agent1_path = temp_dir1
        agent1_dir = Path(agent1_path)
        agent1_yaml = agent1_dir / "agent.yaml"
        agent1_yaml.write_text("name: agent-1\nversion: 1.0.0")

        agent1_py = agent1_dir / "agent.py"
        agent1_py.write_text(
            """
import json
import sys
import time

class Agent:
    def work_method(self, task_name):
        print(f"🤖 Agent 1: Starting task '{task_name}'")

        for i in range(3):
            print(f"🤖 Agent 1: Working on step {i+1}/3 for '{task_name}'")
            time.sleep(1)  # Simulate work

        print(f"🤖 Agent 1: Completed task '{task_name}'")
        return {"result": f"Agent 1 completed {task_name}", "status": "success"}

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

        # Create Agent 2
        agent2_path = temp_dir2
        agent2_dir = Path(agent2_path)
        agent2_yaml = agent2_dir / "agent.yaml"
        agent2_yaml.write_text("name: agent-2\nversion: 1.0.0")

        agent2_py = agent2_dir / "agent.py"
        agent2_py.write_text(
            """
import json
import sys
import time

class Agent:
    def work_method(self, task_name):
        print(f"🚀 Agent 2: Starting task '{task_name}'")

        for i in range(3):
            print(f"🚀 Agent 2: Working on step {i+1}/3 for '{task_name}'")
            time.sleep(1.2)  # Slightly different timing

        print(f"🚀 Agent 2: Completed task '{task_name}'")
        return {"result": f"Agent 2 completed {task_name}", "status": "success"}

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

        print("\n3️⃣ Starting WebSocket server in main thread...")
        server_started = manager.start_websocket_server()
        if server_started:
            print("✅ WebSocket server started successfully!")
            manager.log_communication_status()
        else:
            print("❌ Failed to start WebSocket server, using fallback")

        print("\n4️⃣ Executing both agents simultaneously...")
        print("📡 Watch for interleaved log messages from both agents:")
        print("-" * 50)

        import threading
        import unittest.mock

        def run_agent1():
            """Run Agent 1 in a separate thread."""
            with unittest.mock.patch.object(
                manager.environment_manager,
                "get_python_executable",
                return_value="python",
            ):
                result1 = manager.execute_agent(
                    agent_path=agent1_path,
                    method="work_method",
                    parameters={"task_name": "Data Processing"},
                )
                print(f"\n✅ Agent 1 Result: {result1['result']['result']}")

        def run_agent2():
            """Run Agent 2 in a separate thread."""
            with unittest.mock.patch.object(
                manager.environment_manager,
                "get_python_executable",
                return_value="python",
            ):
                result2 = manager.execute_agent(
                    agent_path=agent2_path,
                    method="work_method",
                    parameters={"task_name": "Image Analysis"},
                )
                print(f"\n✅ Agent 2 Result: {result2['result']['result']}")

        # Start both agents in separate threads
        thread1 = threading.Thread(target=run_agent1)
        thread2 = threading.Thread(target=run_agent2)

        thread1.start()
        time.sleep(0.5)  # Small delay to see interleaving
        thread2.start()

        # Wait for both to complete
        thread1.join()
        thread2.join()

        print("-" * 50)
        print("\n🎯 Analysis:")
        print("If you see interleaved messages from both agents above,")
        print("it means they can see each other's logs in real-time!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
    finally:
        # Clean up temporary directories
        import shutil

        shutil.rmtree(temp_dir1, ignore_errors=True)
        shutil.rmtree(temp_dir2, ignore_errors=True)

    print("\n" + "=" * 70)
    print("🎉 MULTI-AGENT LOG SHARING TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    test_multi_agent_log_sharing()
