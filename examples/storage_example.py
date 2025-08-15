#!/usr/bin/env python3
"""
Storage Module Example: Agent discovery and storage management.

This example demonstrates how to use the Storage Module to discover agents,
manage the AgentHub directory structure, and inspect agent metadata.
"""

import sys
from pathlib import Path

# Add the project root to Python path so we can import agentmanager
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentmanager.storage.local_storage import LocalStorage  # noqa: E402


def main():
    """Demonstrate complete Storage Module functionality."""
    print("📦 Storage Module Example")
    print("=" * 50)

    # Initialize storage
    print("\n1. Initializing Local Storage...")
    storage = LocalStorage()

    # Show directory structure
    print(f"AgentHub directory: {storage.get_agenthub_dir()}")
    print(f"Agents directory: {storage.get_agents_dir()}")

    # Initialize storage (create directories if needed)
    print("\n2. Initializing storage structure...")
    storage.initialize_storage()
    print("✅ Storage structure initialized")

    # Discover agents
    print("\n3. Discovering installed agents...")
    agents = storage.discover_agents()

    if not agents:
        print("❌ No agents found!")
        print("Please install seed agents first by running the seed agents setup.")
        return

    print(f"Found {len(agents)} agents:")
    for agent in agents:
        print(f"   📱 {agent['namespace']}/{agent['name']}")
        print(f"      Version: {agent.get('version', 'unknown')}")
        print(f"      Path: {agent['path']}")
        print()

    # Test specific agent operations
    print("4. Testing Agent-Specific Operations...")
    print("-" * 40)

    for agent in agents:
        namespace = agent["namespace"]
        name = agent["name"]

        print(f"\n🔍 Testing {namespace}/{name}:")

        # Check if agent exists
        exists = storage.agent_exists(namespace, name)
        print(f"   Agent exists: {exists}")

        # Get agent path
        agent_path = storage.get_agent_path(namespace, name)
        print(f"   Agent path: {agent_path}")

        # Check agent directory contents
        if agent_path.exists():
            contents = list(agent_path.iterdir())
            print("   Directory contents:")
            for item in sorted(contents):
                if item.is_file():
                    print(f"      📄 {item.name}")
                elif item.is_dir():
                    print(f"      📁 {item.name}/")

    # Test with nonexistent agent
    print("\n5. Testing with nonexistent agent...")
    print("-" * 40)

    fake_exists = storage.agent_exists("fake", "nonexistent-agent")
    print(f"Fake agent exists: {fake_exists}")

    fake_path = storage.get_agent_path("fake", "nonexistent-agent")
    print(f"Fake agent path: {fake_path}")
    print(f"Fake path exists: {fake_path.exists()}")

    # Storage statistics
    print("\n6. Storage Statistics...")
    print("-" * 40)

    total_agents = len(agents)
    namespaces = {agent["namespace"] for agent in agents}

    print(f"Total agents: {total_agents}")
    print(f"Unique namespaces: {len(namespaces)}")
    print(f"Namespaces: {', '.join(sorted(namespaces))}")

    # Calculate total storage usage (rough estimate)
    total_size = 0
    for agent in agents:
        agent_path = Path(agent["path"])
        if agent_path.exists():
            for file_path in agent_path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size

    print(f"Approximate storage usage: {total_size / (1024*1024):.2f} MB")

    print("\n🎉 Storage Module example completed successfully!")
    print("\nKey features demonstrated:")
    print("✅ AgentHub directory structure management")
    print("✅ Agent discovery with metadata extraction")
    print("✅ Agent existence checking")
    print("✅ Path resolution and validation")
    print("✅ Directory content inspection")
    print("✅ Storage statistics and monitoring")


if __name__ == "__main__":
    main()
