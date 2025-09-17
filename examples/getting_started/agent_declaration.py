#!/usr/bin/env python3
"""
Agent Declaration File - User declares agents with tool assignments

This is where users define their agents and assign tools to them.
The framework will automatically explore tool information and inject
it into agents via the command format.
"""

import agenthub as ah


def main():
    print("🤖 Agent Declaration - User-Defined Agent Configuration")
    print("=" * 65)
    print("📡 Tools are hosted separately in mcp_tool_server.py")
    print("🔍 Framework will discover tools dynamically from MCP server")
    print()

    # Tool exploration via MCP protocol
    print("🔍 Tool Exploration:")
    print("-" * 40)
    print("📡 Tools are hosted in mcp_tool_server.py")
    print("🔧 Framework discovers tools via MCP protocol")

    try:
        # Discover tools from MCP server
        available_tools = ah.get_available_tools()
        print(f"📋 Available tools (from MCP server): {len(available_tools)}")
        for tool_name in available_tools:
            print(f"   - {tool_name}")

        print("\n📊 Tool Descriptions (from MCP server):")
        for tool_name in available_tools:
            try:
                metadata = ah.get_tool_metadata(tool_name)
                if metadata:
                    description = getattr(
                        metadata, "description", "No description available"
                    )
                    print(f"   🔧 {tool_name}: {description}")
                else:
                    print(f"   🔧 {tool_name}: No metadata available")
            except Exception:
                print(f"   🔧 {tool_name}: No metadata available")

    except Exception as e:
        print(f"⚠️  Could not discover tools from MCP server: {e}")
        print("   Make sure mcp_tool_server.py is running!")
        print("   Falling back to demo mode...")

        # Fallback to demo tools
        demo_tools = [
            "add",
            "subtract",
            "multiply",
            "divide",
            "greet",
            "get_weather",
            "process_text",
        ]
        print(f"📋 Demo tools: {len(demo_tools)}")
        for tool_name in demo_tools:
            print(f"   - {tool_name}")

    print()

    # User declares agents with tool assignments
    print("📋 User Agent Declarations:")
    print("-" * 40)

    # Agent 1: Analysis Agent with specific tools
    print("🔍 Declaring Analysis Agent...")
    try:
        analysis_agent = ah.load_agent(
            "agentplug/analysis-agent", tools=["add", "multiply", "process_text"]
        )
        print(f"   ✅ Analysis Agent: {analysis_agent.name}")
        print(f"   🔧 Assigned tools: {analysis_agent.get_assigned_tools()}")
    except Exception as e:
        print(f"   ⚠️  Could not load agent: {e}")
        print("   📋 Agent: agentplug/analysis-agent")
        print("   🔧 Assigned tools: ['add', 'multiply', 'process_text']")

    # Agent 2: Coding Agent with different tools
    print("\n💻 Declaring Coding Agent...")
    try:
        coding_agent = ah.load_agent(
            "agentplug/coding-agent", tools=["add", "subtract", "greet"]
        )
        print(f"   ✅ Coding Agent: {coding_agent.name}")
        print(f"   🔧 Assigned tools: {coding_agent.get_assigned_tools()}")
    except Exception as e:
        print(f"   ⚠️  Could not load agent: {e}")
        print("   📋 Agent: agentplug/coding-agent")
        print("   🔧 Assigned tools: ['add', 'subtract', 'greet']")

    # Agent 3: Math Agent with math tools only
    print("\n🧮 Declaring Math Agent...")
    try:
        math_agent = ah.load_agent(
            "agentplug/analysis-agent",  # Reusing analysis agent for demo
            tools=["add", "subtract", "multiply", "divide"],
        )
        print(f"   ✅ Math Agent: {math_agent.name}")
        print(f"   🔧 Assigned tools: {math_agent.get_assigned_tools()}")
    except Exception as e:
        print(f"   ⚠️  Could not load agent: {e}")
        print("   📋 Agent: agentplug/analysis-agent")
        print("   🔧 Assigned tools: ['add', 'subtract', 'multiply', 'divide']")

    # Agent 4: Text Agent with text processing tools
    print("\n📝 Declaring Text Agent...")
    try:
        text_agent = ah.load_agent(
            "agentplug/coding-agent",  # Reusing coding agent for demo
            tools=["greet", "process_text", "get_weather"],
        )
        print(f"   ✅ Text Agent: {text_agent.name}")
        print(f"   🔧 Assigned tools: {text_agent.get_assigned_tools()}")
    except Exception as e:
        print(f"   ⚠️  Could not load agent: {e}")
        print("   📋 Agent: agentplug/coding-agent")
        print("   🔧 Assigned tools: ['greet', 'process_text', 'get_weather']")

    # Show tool context generation for agents
    print("\n🔧 Tool Context Generation:")
    print("-" * 40)

    # Show tool context for analysis agent
    print("📋 Analysis Agent Tool Context:")
    try:
        if "analysis_agent" in locals() and analysis_agent:
            tool_context = analysis_agent.get_tool_context_json()
            print(f"   🔧 Available tools: {tool_context.get('available_tools', [])}")
            print(
                f"   📝 Tool descriptions: "
                f"{list(tool_context.get('tool_descriptions', {}).keys())}"
            )
            print(
                f"   💡 Tool usage examples: "
                f"{list(tool_context.get('tool_usage_examples', {}).keys())}"
            )

            # Generate a sample agent call JSON
            sample_call = analysis_agent.generate_agent_call_json(
                method="analyze_text",
                parameters={
                    "text": "Sample text for analysis",
                    "analysis_type": "general",
                },
            )
            print("\n📄 Sample Agent Call JSON (first 200 chars):")
            print(f"   {sample_call[:200]}...")
        else:
            print("   ⚠️  Analysis agent not loaded, showing demo context")
            print("   🔧 Available tools: ['add', 'multiply', 'process_text']")
            print(
                "{'add': 'Add two numbers', 'multiply': 'Multiply numbers', "
                "'process_text': 'Process text'}"
            )
    except Exception as e:
        print(f"   ⚠️  Could not generate tool context: {e}")

    return {
        "analysis_agent": "agentplug/analysis-agent",
        "coding_agent": "agentplug/coding-agent",
        "math_agent": "agentplug/analysis-agent",
        "text_agent": "agentplug/coding-agent",
    }


if __name__ == "__main__":
    agents = main()
    print(f"\n🎉 Declared {len(agents)} agents with tool assignments!")
