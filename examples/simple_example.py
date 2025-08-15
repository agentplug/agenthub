#!/usr/bin/env python3
"""
Simple Example: Show how easy AgentHub is to use.

Just 3 lines of code to get AI-generated backpropagation!
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentmanager.core.agent_loader import AgentLoader  # noqa: E402
from agentmanager.core.agent_wrapper import AgentWrapper  # noqa: E402
from agentmanager.runtime.agent_runtime import AgentRuntime  # noqa: E402
from agentmanager.storage.local_storage import LocalStorage  # noqa: E402


def main():
    """Super simple: 3 lines to get AI-generated code!"""
    print("🚀 AgentHub: Super Simple to Use!")
    print("=" * 40)

    # Load agent (3 lines - super simple!)
    storage = LocalStorage()
    loader = AgentLoader(storage)
    agent = AgentWrapper(
        loader.load_agent("agentplug", "coding-agent"), runtime=AgentRuntime(storage)
    )

    # Generate code (1 line)
    result = agent.generate_code(prompt="Create a simple backpropagation algorithm")

    # Use the code (1 line)
    print(f"✅ Generated {len(result['result'])} chars of backpropagation code!")
    print("\n" + result["result"])


if __name__ == "__main__":
    main()
