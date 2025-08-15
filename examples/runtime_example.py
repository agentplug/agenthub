#!/usr/bin/env python3
"""
Runtime Module Example: Complete agent execution system demonstration.

This example shows how to use the Runtime Module to execute AI agents
with proper storage integration, process isolation, and error handling.
"""

import sys
from pathlib import Path

# Add the project root to Python path so we can import agentmanager
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentmanager.runtime.agent_runtime import AgentRuntime  # noqa: E402
from agentmanager.storage.local_storage import LocalStorage  # noqa: E402


def main():
    """Demonstrate complete Runtime Module functionality."""
    print("🚀 Runtime Module Example")
    print("=" * 50)

    # Initialize storage and runtime
    print("\n1. Initializing Storage and Runtime...")
    storage = LocalStorage()
    runtime = AgentRuntime(storage=storage)

    # Discover available agents
    print("\n2. Discovering available agents...")
    agents = storage.discover_agents()
    print(f"Found {len(agents)} agents:")
    for agent in agents:
        version = agent.get("version", "unknown")
        print(f"   - {agent['namespace']}/{agent['name']} (v{version})")

    if not agents:
        print("❌ No agents found! Please ensure seed agents are created first.")
        print(
            "Run: python -c 'from setup_seed_agents import "
            "create_seed_agents; create_seed_agents()'"
        )
        return

    # Example 1: Execute coding agent
    print("\n3. Executing Coding Agent...")
    print("-" * 30)
    try:
        result = runtime.execute_agent(
            "agentplug",
            "coding-agent",
            "generate_code",
            {"prompt": "Create a simple calculator class"},
        )

        if "result" in result:
            print("✅ Success!")
            print("Generated code:")
            print(
                result["result"][:200] + "..."
                if len(result["result"]) > 200
                else result["result"]
            )
            print(f"Execution time: {result.get('execution_time', 0):.2f}s")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Exception: {e}")

    # Example 2: Execute analysis agent
    print("\n4. Executing Analysis Agent...")
    print("-" * 30)
    try:
        result = runtime.execute_agent(
            "agentplug",
            "analysis-agent",
            "analyze_text",
            {"text": "I love Python programming!", "analysis_type": "sentiment"},
        )

        if "result" in result:
            print("✅ Success!")
            print(f"Analysis result: {result['result']}")
            print(f"Execution time: {result.get('execution_time', 0):.2f}s")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Exception: {e}")

    # Example 3: Test error handling
    print("\n5. Testing Error Handling...")
    print("-" * 30)

    # Test invalid method
    result = runtime.execute_agent("agentplug", "coding-agent", "invalid_method", {})
    print(f"Invalid method: {result.get('error', 'No error')}")

    # Test nonexistent agent
    result = runtime.execute_agent("agentplug", "nonexistent-agent", "some_method", {})
    print(f"Nonexistent agent: {result.get('error', 'No error')}")

    # Example 4: Get agent information
    print("\n6. Getting Agent Information...")
    print("-" * 30)

    for agent in agents:
        namespace = agent["namespace"]
        name = agent["name"]
        agent_path = str(storage.get_agent_path(namespace, name))

        info = runtime.get_agent_info(agent_path)
        print(f"\n📋 {namespace}/{name}:")
        print(f"   Version: {info.get('version', 'unknown')}")
        print(f"   Description: {info.get('description', 'No description')}")
        print(f"   Available methods: {', '.join(info.get('methods', []))}")
        print(f"   Valid structure: {info.get('valid_structure', False)}")

    print("\n🎉 Runtime Module example completed successfully!")
    print("\nKey features demonstrated:")
    print("✅ Agent discovery via Storage Module")
    print("✅ Process isolation and virtual environment management")
    print("✅ Real AI agent execution with actual results")
    print("✅ Comprehensive error handling")
    print("✅ Agent metadata and interface inspection")


if __name__ == "__main__":
    main()
