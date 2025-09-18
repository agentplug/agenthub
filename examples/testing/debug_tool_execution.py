#!/usr/bin/env python3
"""
Tool Execution Debugging - User-Friendly Example

This example shows how to debug and understand tool execution
in a user-friendly way.
"""

import agenthub as ah


def main():
    """Demonstrate tool execution debugging."""
    print("🔧 Tool Execution Debugging")
    print("=" * 35)
    print("This example shows how to debug tool execution.\n")

    # Example 1: Basic tool execution
    print("📋 Example 1: Basic Tool Execution")
    print("-" * 35)

    try:
        # Load agent with math tools
        agent = ah.load_agent(
            "agentplug/analysis-agent", external_tools=["add", "multiply", "subtract"]
        )

        print(f"✅ Agent loaded with tools: {agent.get_assigned_tools()}")

        # Test simple math
        print("🧮 Testing: What is 15 + 7?")
        result = agent.analyze_text("What is 15 plus 7?")
        print(f"📊 Result: {result}")

    except Exception as e:
        print(f"⚠️  Error: {e}")

    print()

    # Example 2: Tool execution with detailed output
    print("📋 Example 2: Detailed Tool Execution")
    print("-" * 40)

    try:
        # Load agent with more tools
        agent = ah.load_agent(
            "agentplug/analysis-agent",
            external_tools=["add", "multiply", "subtract", "divide"],
        )

        print(f"🔧 Available tools: {agent.get_assigned_tools()}")

        # Test complex math
        print("🧮 Testing: What is (20 * 3) - 15?")
        result = agent.analyze_text("What is 20 times 3, then subtract 15?")
        print(f"📊 Result: {result}")

        # Show tool context
        print("\n🔍 Tool Context Information:")
        tool_context = agent.get_tool_context_json()
        print(f"📝 Tool context generated: {len(tool_context)} characters")

    except Exception as e:
        print(f"⚠️  Error: {e}")

    print()

    # Example 3: Error handling
    print("📋 Example 3: Error Handling")
    print("-" * 30)

    try:
        # Load agent with limited tools
        agent = ah.load_agent(
            "agentplug/analysis-agent", external_tools=["add"]  # Only addition tool
        )

        print(f"🔧 Available tools: {agent.get_assigned_tools()}")

        # Test something that might need more tools
        print("🧮 Testing: What is 10 * 5? (only have addition tool)")
        result = agent.analyze_text("What is 10 times 5?")
        print(f"📊 Result: {result}")

    except Exception as e:
        print(f"⚠️  Error: {e}")

    print()

    # Example 4: Tool availability check
    print("📋 Example 4: Tool Availability Check")
    print("-" * 40)

    try:
        agent = ah.load_agent(
            "agentplug/analysis-agent", external_tools=["add", "multiply", "web_search"]
        )

        print(f"🔧 Assigned tools: {agent.get_assigned_tools()}")

        # Check if specific tools are available
        tools_to_check = ["add", "multiply", "web_search", "divide"]
        for tool in tools_to_check:
            if agent.can_access_tool(tool):
                print(f"✅ Tool '{tool}' is available")
            else:
                print(f"❌ Tool '{tool}' is not available")

    except Exception as e:
        print(f"⚠️  Error: {e}")

    print()

    # Summary
    print("🎯 Debugging Summary")
    print("-" * 20)
    print("✅ Key debugging techniques:")
    print("• Check assigned tools with get_assigned_tools()")
    print("• Verify tool availability with can_access_tool()")
    print("• Review tool context with get_tool_context_json()")
    print("• Handle errors gracefully with try/except")
    print("• Test with simple examples first")

    print("\n💡 Common issues and solutions:")
    print("• Tool not found: Check tool name spelling")
    print("• Agent not responding: Verify agent is loaded correctly")
    print("• Unexpected results: Check tool parameters and context")
    print("• Performance issues: Limit number of tools if not needed")


if __name__ == "__main__":
    main()
