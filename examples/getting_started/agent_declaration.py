#!/usr/bin/env python3
"""
Agent Declaration - Simple Tool Assignment Examples

This example shows how to assign different tools to agents
for different use cases.
"""

import agenthub as ah


def main():
    """Demonstrate different agent configurations with tools."""
    print("🤖 Agent Declaration Examples")
    print("=" * 40)
    print("This shows how to configure agents with different tools.\n")

    # Example 1: Math-focused agent
    print("📋 Example 1: Math Agent")
    print("-" * 25)
    try:
        math_agent = ah.load_agent(
            "agentplug/analysis-agent",
            external_tools=["add", "subtract", "multiply", "divide"],
        )
        print(f"✅ Math Agent loaded with {len(math_agent.get_assigned_tools())} tools")
        print(f"🔧 Tools: {math_agent.get_assigned_tools()}")

        # Test the agent
        result = math_agent.analyze_text("What is 25 times 4?")
        print(f"📊 Result: {result}")

    except Exception as e:
        print(f"⚠️  Could not load math agent: {e}")

    print()

    # Example 2: Text processing agent
    print("📋 Example 2: Text Processing Agent")
    print("-" * 35)
    try:
        text_agent = ah.load_agent(
            "agentplug/analysis-agent", external_tools=["process_text", "greet"]
        )
        print(f"✅ Text Agent loaded with {len(text_agent.get_assigned_tools())} tools")
        print(f"🔧 Tools: {text_agent.get_assigned_tools()}")

        # Test the agent
        result = text_agent.analyze_text("Hello, how are you today?")
        print(f"📊 Result: {result}")

    except Exception as e:
        print(f"⚠️  Could not load text agent: {e}")

    print()

    # Example 3: Web-enabled agent
    print("📋 Example 3: Web-Enabled Agent")
    print("-" * 30)
    try:
        web_agent = ah.load_agent(
            "agentplug/analysis-agent", external_tools=["web_search", "add", "multiply"]
        )
        print(f"✅ Web Agent loaded with {len(web_agent.get_assigned_tools())} tools")
        print(f"🔧 Tools: {web_agent.get_assigned_tools()}")

        # Test the agent
        result = web_agent.analyze_text("What's the current weather like?")
        print(f"📊 Result: {result}")

    except Exception as e:
        print(f"⚠️  Could not load web agent: {e}")

    print()

    # Example 4: Agent with built-in tools disabled
    print("📋 Example 4: Agent with Disabled Built-in Tools")
    print("-" * 45)
    try:
        custom_agent = ah.load_agent(
            "agentplug/analysis-agent",
            external_tools=["add", "multiply"],
            disabled_builtin_tools=["some_builtin_tool"],  # Example
        )
        print("✅ Custom Agent loaded")
        print(f"🔧 External tools: {custom_agent.get_assigned_tools()}")

    except Exception as e:
        print(f"⚠️  Could not load custom agent: {e}")

    print()

    # Show tool context
    print("📋 Tool Context Information")
    print("-" * 30)
    try:
        if "math_agent" in locals():
            math_agent.get_tool_context_json()
            print("🔧 Tool context generated successfully")
            print("📝 This context is automatically injected into the agent")
        else:
            print("⚠️  No agent loaded to show tool context")

    except Exception as e:
        print(f"⚠️  Could not generate tool context: {e}")

    print("\n💡 Key Points:")
    print("• Use external_tools to add capabilities to agents")
    print("• Use disabled_builtin_tools to remove built-in capabilities")
    print("• Tools are automatically discovered and injected")
    print("• Each agent can have different tool configurations")


if __name__ == "__main__":
    main()
