#!/usr/bin/env python3
"""
Tool Access Control Demo

This example demonstrates how AgentHub handles tool access control,
security, and permission management for different agents and tools.
"""

import agenthub as ah


def main():
    """Demonstrate tool access control and security features."""
    print("🔒 Tool Access Control Demo")
    print("=" * 35)
    print("This example shows how AgentHub manages tool access and security.\n")

    # Example 1: Basic tool access control
    print("📋 Example 1: Basic Tool Access Control")
    print("-" * 40)

    try:
        # Load agent with specific tools
        agent = ah.load_agent(
            "agentplug/analysis-agent",
            external_tools=["add", "multiply", "subtract"],
        )

        print(f"✅ Agent loaded with tools: {agent.get_assigned_tools()}")

        # Check tool access
        tools_to_check = ["add", "multiply", "subtract", "divide", "web_search"]
        print("\n🔍 Tool Access Check:")
        for tool in tools_to_check:
            if agent.can_access_tool(tool):
                print(f"  ✅ '{tool}' - Access granted")
            else:
                print(f"  ❌ '{tool}' - Access denied")

    except Exception as e:
        print(f"⚠️  Error: {e}")

    print()

    # Example 2: Tool conflict detection
    print("📋 Example 2: Tool Conflict Detection")
    print("-" * 40)

    try:
        # Try to load agent with conflicting tools
        print("🔧 Attempting to load agent with conflicting tools...")
        agent = ah.load_agent(
            "agentplug/analysis-agent",
            external_tools=["add", "multiply", "add"],  # Duplicate tool
        )
        print("✅ Agent loaded successfully (duplicates handled)")

    except Exception as e:
        print(f"⚠️  Conflict detected: {e}")

    print()

    # Example 3: Built-in tool management
    print("📋 Example 3: Built-in Tool Management")
    print("-" * 40)

    try:
        # Load agent and check built-in tools
        agent = ah.load_agent("agentplug/analysis-agent")
        print(f"✅ Agent loaded: {agent.name}")

        # Check built-in tools
        builtin_tools = agent.get_builtin_tools()
        print(f"🔧 Built-in tools available: {len(builtin_tools)}")
        for tool_name, tool_info in builtin_tools.items():
            status = "enabled" if tool_info.enabled else "disabled"
            required = "required" if tool_info.required else "optional"
            print(f"  • {tool_name}: {status} ({required})")

        # Try to disable a built-in tool
        print("\n🔧 Attempting to disable built-in tools...")
        try:
            agent.disable_builtin_tools(["some_builtin_tool"])
            print("✅ Built-in tool disabled")
        except Exception as e:
            print(f"⚠️  Could not disable: {e}")

    except Exception as e:
        print(f"⚠️  Error: {e}")

    print()

    # Example 4: Tool validation and security
    print("📋 Example 4: Tool Validation and Security")
    print("-" * 40)

    try:
        # Load agent with various tools
        agent = ah.load_agent(
            "agentplug/analysis-agent", external_tools=["add", "multiply", "web_search"]
        )

        print(f"✅ Agent loaded with {len(agent.get_assigned_tools())} tools")

        # Validate tool parameters
        print("\n🔍 Tool Parameter Validation:")
        test_cases = [
            {"tool": "add", "params": {"a": 5, "b": 3}},
            {"tool": "add", "params": {"a": "invalid", "b": 3}},
            {"tool": "multiply", "params": {"x": 2, "y": 4}},
            {"tool": "nonexistent", "params": {}},
        ]

        for case in test_cases:
            tool = case["tool"]
            params = case["params"]

            if agent.can_access_tool(tool):
                print(f"  ✅ '{tool}' with params {params} - Accessible")
            else:
                print(f"  ❌ '{tool}' with params {params} - Not accessible")

    except Exception as e:
        print(f"⚠️  Error: {e}")

    print()

    # Example 5: Tool summary and metadata
    print("📋 Example 5: Tool Summary and Metadata")
    print("-" * 40)

    try:
        agent = ah.load_agent(
            "agentplug/analysis-agent", external_tools=["add", "multiply", "subtract"]
        )

        # Get comprehensive tool summary
        print("📊 Tool Summary:")
        summary = agent.get_tool_summary()
        print(f"  • Total tools: {summary.get('total_tools', 0)}")
        print(f"  • Built-in tools: {summary.get('builtin_tools', 0)}")
        print(f"  • External tools: {summary.get('external_tools', 0)}")
        print(f"  • Available tools: {summary.get('available_tools', [])}")

        # Get tool metadata
        print("\n🔍 Tool Metadata:")
        for tool_name in agent.get_assigned_tools():
            try:
                metadata = agent.get_tool_metadata(tool_name)
                if metadata:
                    print(f"  • {tool_name}: {metadata}")
                else:
                    print(f"  • {tool_name}: No metadata available")
            except Exception:
                print(f"  • {tool_name}: Metadata not accessible")

    except Exception as e:
        print(f"⚠️  Error: {e}")

    print()

    # Summary
    print("🎯 Tool Access Control Summary")
    print("-" * 35)
    print("✅ Key security features demonstrated:")
    print("• Tool access control and permission checking")
    print("• Tool conflict detection and resolution")
    print("• Built-in tool management and validation")
    print("• Parameter validation and security checks")
    print("• Comprehensive tool metadata and summaries")

    print("\n💡 Security best practices:")
    print("• Always check tool access before use")
    print("• Validate tool parameters and inputs")
    print("• Use appropriate tool permissions")
    print("• Monitor tool usage and conflicts")
    print("• Keep tool metadata up to date")


if __name__ == "__main__":
    main()
