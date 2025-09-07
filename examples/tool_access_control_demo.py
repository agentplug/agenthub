#!/usr/bin/env python3
"""
Tool Access Control Demo

This demonstrates how to limit tool access to specific agents.
When you do: agent = amg.load_agent(base_agent="agentplug/analysis_agent", tools=["web_search", "add"])
The agent will only have access to those specific tools.
"""

# First register some tools by importing the server
from examples.mcp_tool_server import *

# Now demonstrate tool access control
from agentmanager.core.tools import (
    assign_tools_to_agent, 
    get_agent_tools, 
    can_agent_access_tool,
    get_agent_tool_metadata,
    get_available_tools
)

def main():
    print("🔐 Tool Access Control Demo")
    print("=" * 50)
    
    # Show all available tools
    all_tools = get_available_tools()
    print(f"📋 All available tools: {all_tools}")
    
    # Create different agents with different tool access
    print("\n🤖 Creating agents with limited tool access...")
    
    # Agent 1: Analysis agent with text processing and weather tools
    analysis_agent_id = "analysis_agent"
    analysis_tools = ["process_text", "get_weather", "greet"]
    assign_tools_to_agent(analysis_agent_id, analysis_tools)
    
    # Agent 2: Math agent with only arithmetic tools
    math_agent_id = "math_agent"
    math_tools = ["add", "subtract", "multiply", "divide"]
    assign_tools_to_agent(math_agent_id, math_tools)
    
    # Agent 3: Weather agent with only weather tool
    weather_agent_id = "weather_agent"
    weather_tools = ["get_weather"]
    assign_tools_to_agent(weather_agent_id, weather_tools)
    
    # Show what each agent can access
    print(f"\n📊 Agent Tool Access:")
    
    for agent_id in [analysis_agent_id, math_agent_id, weather_agent_id]:
        agent_tools = get_agent_tools(agent_id)
        print(f"\n🔹 {agent_id}:")
        print(f"   Assigned tools: {agent_tools}")
        
        # Show tool metadata for this agent
        metadata = get_agent_tool_metadata(agent_id)
        for meta in metadata:
            print(f"   - {meta.name}: {meta.description}")
    
    # Test access control
    print(f"\n🔍 Testing Access Control:")
    
    # Test analysis agent access
    print(f"\nAnalysis Agent Access:")
    for tool in ["process_text", "add", "get_weather", "greet"]:
        can_access = can_agent_access_tool(analysis_agent_id, tool)
        status = "✅" if can_access else "❌"
        print(f"   {status} {tool}: {'Can access' if can_access else 'Cannot access'}")
    
    # Test math agent access
    print(f"\nMath Agent Access:")
    for tool in ["add", "subtract", "process_text", "get_weather"]:
        can_access = can_agent_access_tool(math_agent_id, tool)
        status = "✅" if can_access else "❌"
        print(f"   {status} {tool}: {'Can access' if can_access else 'Cannot access'}")
    
    # Test weather agent access
    print(f"\nWeather Agent Access:")
    for tool in ["get_weather", "add", "process_text"]:
        can_access = can_agent_access_tool(weather_agent_id, tool)
        status = "✅" if can_access else "❌"
        print(f"   {status} {tool}: {'Can access' if can_access else 'Cannot access'}")
    
    # Test actual tool execution with access control
    print(f"\n🧪 Testing Tool Execution with Access Control:")
    
    # Simulate agent tool execution
    def simulate_agent_tool_execution(agent_id: str, tool_name: str, *args, **kwargs):
        """Simulate an agent trying to execute a tool."""
        if can_agent_access_tool(agent_id, tool_name):
            # Get the tool function and execute it
            from agentmanager.core.tools import get_tool_function
            tool_func = get_tool_function(tool_name)
            if tool_func:
                try:
                    result = tool_func(*args, **kwargs)
                    print(f"   ✅ {agent_id} executed {tool_name}: {result}")
                    return result
                except Exception as e:
                    print(f"   ❌ {agent_id} error executing {tool_name}: {e}")
                    return None
            else:
                print(f"   ❌ {agent_id} tool function not found: {tool_name}")
                return None
        else:
            print(f"   🚫 {agent_id} ACCESS DENIED to {tool_name}")
            return None
    
    # Test analysis agent tool execution
    print(f"\n🔹 Analysis Agent Tool Execution:")
    simulate_agent_tool_execution(analysis_agent_id, "process_text", "hello world", "uppercase")
    simulate_agent_tool_execution(analysis_agent_id, "get_weather", "Paris", "celsius")
    simulate_agent_tool_execution(analysis_agent_id, "add", 5, 3)  # Should be denied
    simulate_agent_tool_execution(analysis_agent_id, "greet", "Alice")
    
    # Test math agent tool execution
    print(f"\n🔹 Math Agent Tool Execution:")
    simulate_agent_tool_execution(math_agent_id, "add", 10, 20)
    simulate_agent_tool_execution(math_agent_id, "multiply", 7, 8)
    simulate_agent_tool_execution(math_agent_id, "get_weather", "Tokyo")  # Should be denied
    simulate_agent_tool_execution(math_agent_id, "process_text", "test", "uppercase")  # Should be denied
    
    # Test weather agent tool execution
    print(f"\n🔹 Weather Agent Tool Execution:")
    simulate_agent_tool_execution(weather_agent_id, "get_weather", "London", "fahrenheit")
    simulate_agent_tool_execution(weather_agent_id, "add", 2, 3)  # Should be denied
    simulate_agent_tool_execution(weather_agent_id, "greet", "Bob")  # Should be denied
    
    print(f"\n✅ Tool access control demo complete!")
    print(f"\n💡 In your future code:")
    print(f"   agent = amg.load_agent(base_agent='agentplug/analysis_agent', tools=['web_search', 'add'])")
    print(f"   # The agent will only have access to 'web_search' and 'add' tools")

if __name__ == "__main__":
    main()
