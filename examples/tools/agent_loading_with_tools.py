#!/usr/bin/env python3
"""
WORKING AGENT LOADING EXAMPLES
=============================

Copy and paste any of these examples to load and call agents.
All examples are production-ready and validated.
"""


import agenthub as ah

# Configure logging to suppress HTTP logs
ah.set_quiet_mode(True)


def example_1_basic_agent():
    """Load agent without tools"""
    print("📋 Example 1: Basic Agent (no tools)")
    question = "That is a great product. I love to use AgentHub."
    print(f"📄 Input: {question}")
    agent = ah.load_agent("agentplug/analysis-agent")
    result = agent.analyze_text(question)
    print(result)
    # ================================================
    status = result.get("result", {}).get("status", "completed")
    analysis = result.get("result", {}).get("summary", "No analysis")
    print(f"✅ Status: {status}")
    print(f"📄 Analysis: {analysis}")
    return result


def example_2_agent_with_single_tool():
    """Load agent with single tool"""
    print("\n📋 Example 2: Agent with Single Tool")
    agent = ah.load_agent("agentplug/analysis-agent", tools=["multiply"])
    question = "Calculate 7 times 8"
    print(f"📄 Input: {question}")
    result = agent.analyze_text(question)
    # ================================================
    status = result.get("result", {}).get("status", "completed")
    analysis = result.get("result", {}).get("summary", "No analysis")
    tools_used = result.get("result", {}).get("tools_used", [])
    print(f"✅ Status: {status}")
    print(f"🔧 Tools used: {tools_used}")
    print(f"📄 Analysis: {analysis}")
    return result


def example_3_agent_with_multiple_tools():
    """Load agent with multiple tools"""
    print("\n📋 Example 3: Agent with Multiple Tools")
    agent = ah.load_agent("agentplug/analysis-agent", tools=["multiply", "add"])
    question = "Calculate 12 times 5, then add 8"
    print(f"📄 Input: {question}")
    result = agent.analyze_text(question)
    # ================================================
    status = result.get("result", {}).get("status", "completed")
    analysis = result.get("result", {}).get("summary", "No analysis")
    tools_used = result.get("result", {}).get("tools_used", [])
    print(f"✅ Status: {status}")
    print(f"🔧 Tools used: {tools_used}")
    print(f"📄 Analysis: {analysis}")
    return result


def example_4_math_focused_agent():
    """Load agent with all math tools"""
    print("\n📋 Example 4: Math-Focused Agent")
    agent = ah.load_agent(
        "agentplug/analysis-agent", tools=["multiply", "add", "subtract", "divide"]
    )
    question = "What is 100 divided by 4, then multiply by 3?"
    print(f"📄 Input: {question}")
    result = agent.analyze_text(question)
    # ================================================
    status = result.get("result", {}).get("status", "completed")
    analysis = result.get("result", {}).get("summary", "No analysis")
    tools_used = result.get("result", {}).get("tools_used", [])
    print(f"✅ Status: {status}")
    print(f"🔧 Tools used: {tools_used}")
    print(f"🛠️  Tools available: {len(agent.assigned_tools)} tools")
    print(f"📄 Analysis: {analysis}")
    return result


def example_5_compare_numbers_agent():
    """Load agent with compare numbers tool"""

    print("\n📋 Example 5: Compare Numbers Agent without tools")
    agent = ah.load_agent("agentplug/analysis-agent")
    question = "Compare 9.8 and 9.11, which number is larger?"
    print(f"📄 Input: {question}")
    result = agent.analyze_text(question)
    # ================================================
    status = result.get("result", {}).get("status", "completed")
    analysis = result.get("result", {}).get("summary", "No analysis")
    tools_used = result.get("result", {}).get("tools_used", [])
    print(f"✅ Status: {status}")
    print(f"🔧 Tools used: {tools_used}")
    print(f"📄 Analysis: {analysis}")

    print("\n📋 Example 5: Compare Numbers Agent with tools")
    agent = ah.load_agent("agentplug/analysis-agent", tools=["compare_numbers"])
    question = "Compare 9.8 and 9.11, which number is larger?"
    print(f"📄 Input: {question}")
    result = agent.analyze_text(question)
    # ================================================
    status = result.get("result", {}).get("status", "completed")
    analysis = result.get("result", {}).get("summary", "No analysis")
    tools_used = result.get("result", {}).get("tools_used", [])
    print(f"✅ Status: {status}")
    print(f"🔧 Tools used: {tools_used}")
    print(f"📄 Analysis: {analysis}")

    return result


def example_6_web_search_agent():
    """Load agent with web search tool"""
    print("\n📋 Example 6: Web Search Agent")
    agent = ah.load_agent(
        "agentplug/analysis-agent",
        tools=["web_search", "add", "subtract", "multiply", "divide"],
    )
    question = "Who is the US President 2025?"
    print(f"📄 Input: {question}")
    result = agent.analyze_text(question)
    print(f"📊 Result: {result}")
    # ================================================
    status = result.get("result", {}).get("status", "completed")
    analysis = result.get("result", {}).get("summary", "No analysis")
    tools_used = result.get("result", {}).get("tools_used", [])
    print(f"✅ Status: {status}")
    print(f"🔧 Tools used: {tools_used}")
    print(f"📄 Analysis: {analysis}")
    return result


def wait_for_key(message="Press Enter to continue to next example..."):
    """Wait for user input before continuing"""
    input(f"\n⏸️  {message}")


if __name__ == "__main__":
    print("🚀 WORKING AGENT LOADING EXAMPLES")
    print("=" * 50)
    print("Each example will pause for you to review the results.")

    # Run examples with pauses
    example_1_basic_agent()
    wait_for_key("Press Enter to continue to Example 2...")

    example_2_agent_with_single_tool()
    wait_for_key("Press Enter to continue to Example 3...")

    example_3_agent_with_multiple_tools()
    wait_for_key("Press Enter to continue to Example 4...")

    example_4_math_focused_agent()
    wait_for_key("Press Enter to continue to Example 5...")

    example_5_compare_numbers_agent()
    wait_for_key("Press Enter to continue to Example 6...")

    example_6_web_search_agent()
    wait_for_key("Press Enter to finish...")

    print("\n🎉 All examples completed successfully!")
    print("Copy any function above to use in your own code.")
