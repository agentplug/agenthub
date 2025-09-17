#!/usr/bin/env python3
"""
Debug Tool Execution Demo

This demo shows the actual tool execution process with detailed logging.
"""

import asyncio
import json

import agenthub as ah
from agenthub.core.tools import get_available_tools, tool


# Define tools with detailed logging
@tool(name="web_search", description="Search the web for real-time information")
def web_search(query: str, max_results: int = 5) -> dict:
    """Web search with detailed logging"""
    print(
        f"🔍 [TOOL] web_search called with query='{query}', max_results={max_results}"
    )

    # Simulate web search (using mock data for reliability)
    results = [
        {
            "title": f"Latest AI Trends 2024 - {query}",
            "snippet": (
                f"Latest trends of {query} showing major developments in "
                f"artificial intelligence and machine learning."
            ),
            "url": "https://example.com/ai-trends-2024",
        },
        {
            "title": f"Machine Learning Advances - {query}",
            "snippet": (
                f"Recent breakthroughs in {query} including new algorithms "
                f"and applications."
            ),
            "url": "https://example.com/ml-advances",
        },
    ]

    result = {
        "query": query,
        "results": results[:max_results],
        "total_found": len(results),
    }

    print(f"✅ [TOOL] web_search returned {len(results)} results")
    return result


@tool(name="data_analyzer", description="Analyze data and provide insights")
def data_analyzer(data: str, analysis_type: str = "general") -> dict:
    """Data analyzer with detailed logging"""
    print(
        f"🔍 [TOOL] data_analyzer called with data='{data[:30]}...', "
        f"type='{analysis_type}'"
    )

    result = {
        "data": data,
        "analysis_type": analysis_type,
        "insights": [
            f"Data length: {len(data)} characters",
            f"Word count: {len(data.split())} words",
            f"Analysis type: {analysis_type}",
            "Key patterns identified",
            "Statistical analysis completed",
        ],
        "summary": f"Analyzed {len(data)} characters of {analysis_type} data",
    }

    print(f"✅ [TOOL] data_analyzer returned {len(result['insights'])} insights")
    return result


async def main():
    """Debug the complete tool execution flow."""
    print("🐛 DEBUG TOOL EXECUTION DEMO")
    print("=" * 50)

    # Show available tools
    print(f"📋 Available tools: {get_available_tools()}")

    # Load agent with tools
    print("\n🤖 Loading agent with tools...")
    agent = ah.load_agent(
        agent_name="agentplug/analysis-agent", tools=["web_search", "data_analyzer"]
    )

    print(f"✅ Agent loaded: {type(agent).__name__}")
    print(f"📋 Available methods: {agent.get_available_methods()}")
    print(f"🔧 Assigned tools: {agent.get_assigned_tools()}")

    # Test 1: Text that should trigger web search
    print("\n" + "=" * 50)
    print("TEST 1: Text that should trigger web search")
    print("=" * 50)

    text1 = "What are the latest trends in artificial intelligence?"
    print(f"📝 Input: {text1}")
    print("\n🤖 Agent processing...")

    result1 = agent.analyze_text(text1, analysis_type="general")
    print(f"\n📊 Result: {json.dumps(result1, indent=2)}")

    # Test 2: Text that might trigger data analysis
    print("\n" + "=" * 50)
    print("TEST 2: Text that might trigger data analysis")
    print("=" * 50)

    text2 = (
        "Analyze this data: 'Sales increased by 25% this quarter, "
        "customer satisfaction is at 95%, and we have 1000 new users.'"
    )
    print(f"📝 Input: {text2}")
    print("\n🤖 Agent processing...")

    result2 = agent.analyze_text(text2, analysis_type="general")
    print(f"\n📊 Result: {json.dumps(result2, indent=2)}")

    # Test 3: Simple text that shouldn't need tools
    print("\n" + "=" * 50)
    print("TEST 3: Simple text that shouldn't need tools")
    print("=" * 50)

    text3 = "This is a simple greeting message."
    print(f"📝 Input: {text3}")
    print("\n🤖 Agent processing...")

    result3 = agent.analyze_text(text3, analysis_type="general")
    print(f"\n📊 Result: {json.dumps(result3, indent=2)}")

    print("\n🎉 Debug demo complete!")


if __name__ == "__main__":
    asyncio.run(main())
