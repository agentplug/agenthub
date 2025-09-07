#!/usr/bin/env python3
"""Step 2 Demo: MCP Server Integration

This demo shows the agent tool management and MCP integration capabilities.
"""

import asyncio
import requests
from agentmanager.core.tools import tool, get_available_tools
from agentmanager.core.mcp import get_tool_manager, get_tool_injector

# Define some tools for testing
@tool(name="web_search", description="Search the web for information using DuckDuckGo")
def web_search(query: str, max_results: int = 5) -> dict:
    """Real web search using DuckDuckGo API"""
    try:
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            },
            timeout=10
        )
        data = response.json()
        
        results = []
        if data.get("Abstract"):
            results.append({
                "title": data.get("Heading", "No title"),
                "snippet": data.get("Abstract", ""),
                "url": data.get("AbstractURL", "")
            })
        
        for topic in data.get("RelatedTopics", [])[:max_results-1]:
            if isinstance(topic, dict) and "Text" in topic:
                results.append({
                    "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " "),
                    "snippet": topic.get("Text", ""),
                    "url": topic.get("FirstURL", "")
                })
        
        return {
            "query": query,
            "results": results[:max_results],
            "total_found": len(results)
        }
    except Exception as e:
        return {
            "query": query,
            "error": str(e),
            "results": []
        }

@tool(name="calculator", description="Perform basic arithmetic operations")
def calculator(operation: str, a: float, b: float) -> dict:
    """Perform basic arithmetic operations."""
    operations = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else "Error: Division by zero"
    }
    
    if operation not in operations:
        return {"error": f"Unknown operation: {operation}"}
    
    return {
        "operation": operation,
        "a": a,
        "b": b,
        "result": operations[operation]
    }

@tool(name="text_processor", description="Process and analyze text")
def text_processor(text: str, operation: str = "uppercase") -> dict:
    """Process text in various ways."""
    operations = {
        "uppercase": text.upper(),
        "lowercase": text.lower(),
        "reverse": text[::-1],
        "word_count": len(text.split()),
        "char_count": len(text)
    }
    
    if operation not in operations:
        return {"error": f"Unknown operation: {operation}"}
    
    return {
        "original_text": text,
        "operation": operation,
        "result": operations[operation]
    }

async def main():
    """Demonstrate Step 2 capabilities."""
    print("🚀 Step 2 Demo: MCP Server Integration")
    print("=" * 50)
    
    # Show available tools
    print(f"📋 Available tools: {get_available_tools()}")
    
    # Get tool manager and injector
    tool_manager = get_tool_manager()
    tool_injector = get_tool_injector()
    
    print(f"\n🛠️  Tool Manager initialized")
    print(f"🔧 Tool Injector initialized")
    
    # Test 1: Tool Assignment
    print("\n📝 Test 1: Tool Assignment")
    print("-" * 30)
    
    # Assign different tools to different agents
    analysis_tools = tool_manager.assign_tools_to_agent("analysis_agent", ["web_search", "text_processor"])
    math_tools = tool_manager.assign_tools_to_agent("math_agent", ["calculator"])
    general_tools = tool_manager.assign_tools_to_agent("general_agent", ["web_search", "calculator", "text_processor"])
    
    print(f"✅ Analysis Agent tools: {analysis_tools}")
    print(f"✅ Math Agent tools: {math_tools}")
    print(f"✅ General Agent tools: {general_tools}")
    
    # Test 2: Tool Discovery
    print("\n📝 Test 2: Tool Discovery")
    print("-" * 30)
    
    for agent_id in ["analysis_agent", "math_agent", "general_agent"]:
        agent_tools = tool_manager.get_agent_tools(agent_id)
        print(f"🔍 {agent_id} has access to: {agent_tools}")
    
    # Test 3: Tool Access Control
    print("\n📝 Test 3: Tool Access Control")
    print("-" * 30)
    
    # Check access control
    print(f"🔒 Analysis Agent can use web_search: {tool_manager.has_tool_access('analysis_agent', 'web_search')}")
    print(f"🔒 Analysis Agent can use calculator: {tool_manager.has_tool_access('analysis_agent', 'calculator')}")
    print(f"🔒 Math Agent can use web_search: {tool_manager.has_tool_access('math_agent', 'web_search')}")
    print(f"🔒 Math Agent can use calculator: {tool_manager.has_tool_access('math_agent', 'calculator')}")
    
    # Test 4: Tool Execution via MCP
    print("\n📝 Test 4: Tool Execution via MCP")
    print("-" * 30)
    
    try:
        # Execute tools through MCP for different agents
        print("🔧 Executing calculator for math_agent...")
        calc_result = await tool_manager.execute_tool("math_agent", "calculator", {
            "operation": "multiply", 
            "a": 7, 
            "b": 6
        })
        print(f"   Result: {calc_result}")
        
        print("🔧 Executing text_processor for analysis_agent...")
        text_result = await tool_manager.execute_tool("analysis_agent", "text_processor", {
            "text": "Hello World", 
            "operation": "reverse"
        })
        print(f"   Result: {text_result}")
        
        print("🔧 Executing web_search for general_agent...")
        search_result = await tool_manager.execute_tool("general_agent", "web_search", {
            "query": "Python programming", 
            "max_results": 2
        })
        print(f"   Result: {search_result[:200]}...")
        
    except Exception as e:
        print(f"❌ Tool execution error: {e}")
    
    # Test 5: Tool Injection
    print("\n📝 Test 5: Tool Injection")
    print("-" * 30)
    
    # Inject tools into agent context
    injection_result = tool_injector.inject_tools_into_agent_context("analysis_agent", ["web_search", "text_processor"])
    print(f"✅ Injected {injection_result['tool_count']} tools into analysis_agent")
    print(f"📋 Available tools: {injection_result['available_tools']}")
    print(f"📝 System prompt preview: {injection_result['system_prompt'][:200]}...")
    
    # Test 6: Agent Tool Summary
    print("\n📝 Test 6: Agent Tool Summary")
    print("-" * 30)
    
    for agent_id in ["analysis_agent", "math_agent", "general_agent"]:
        summary = tool_injector.get_agent_tool_summary(agent_id)
        print(f"📊 {agent_id}: {summary['tool_count']} tools")
        for tool_info in summary['tools']:
            print(f"   - {tool_info['name']}: {tool_info['description']}")
    
    print("\n✅ Step 2 Demo Complete!")
    print("🎯 Key capabilities demonstrated:")
    print("   • Tool assignment to specific agents")
    print("   • Agent-specific tool access control")
    print("   • Tool execution through MCP client")
    print("   • Tool metadata injection into agent context")
    print("   • Tool discovery and management")
    print("\n🚀 Ready for Step 3: SDK Integration!")

if __name__ == "__main__":
    asyncio.run(main())
