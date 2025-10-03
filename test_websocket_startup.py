#!/usr/bin/env python3
"""Test script to demonstrate WebSocket server startup and real-time streaming."""

import asyncio
import logging
import tempfile
from pathlib import Path

from agenthub.runtime.process_manager import ProcessManager

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


async def test_websocket_startup():
    """Test WebSocket server startup and real-time streaming."""
    print("=" * 60)
    print("🧪 TESTING WEBSOCKET SERVER STARTUP")
    print("=" * 60)

    # Create ProcessManager
    manager = ProcessManager(realtime_communication=True)

    print("\n1️⃣ Initial status:")
    manager.log_communication_status()

    # Manually start the WebSocket server
    print("\n2️⃣ Starting WebSocket server manually...")
    if manager.communication_server:
        success = await manager.communication_server.start()
        if success:
            print("✅ WebSocket server started successfully!")
        else:
            print("❌ Failed to start WebSocket server")

    print("\n3️⃣ Status after startup:")
    manager.log_communication_status()

    # Test agent execution with streaming
    print("\n4️⃣ Testing agent execution with streaming...")
    with tempfile.TemporaryDirectory() as temp_dir:
        agent_path = temp_dir
        agent_dir = Path(agent_path)

        # Create agent.yaml
        agent_yaml = agent_dir / "agent.yaml"
        agent_yaml.write_text("name: streaming-test-agent\nversion: 1.0.0")

        # Create agent.py
        agent_py = agent_dir / "agent.py"
        agent_py.write_text(
            """
import json
import sys
import time

class Agent:
    def streaming_method(self, task_name):
        print(f"🚀 Starting streaming task: {task_name}")

        for i in range(3):
            print(f"📡 Streaming step {i+1}/3: {task_name}")
            time.sleep(1)

        print(f"✅ Completed streaming task: {task_name}")
        return {"result": f"Streaming completed {task_name}", "status": "success"}

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

        try:
            import unittest.mock

            with unittest.mock.patch.object(
                manager.environment_manager,
                "get_python_executable",
                return_value="python",
            ):
                print("📡 Executing agent with real-time streaming...")
                result = manager.execute_agent(
                    agent_path=agent_path,
                    method="streaming_method",
                    parameters={"task_name": "Real-time Test"},
                )
                print(f"\n✅ Agent result: {result['result']['result']}")

        except Exception as e:
            print(f"\n❌ Agent execution failed: {e}")

    print("\n" + "=" * 60)
    print("🎉 WEBSOCKET STARTUP TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_websocket_startup())
