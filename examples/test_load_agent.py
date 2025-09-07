#!/usr/bin/env python3
"""
Test amg.load_agent with tool access control using enhanced existing classes

This demonstrates how to use amg.load_agent with tool access control,
showing both allowed and denied tool access using the enhanced AgentLoader.
"""

# First register some tools by importing the server
from examples.mcp_tool_server import *

# Now test the load_agent functionality
import agentmanager as amg

def main():
    print("🤖 Testing amg.load_agent with Tool Access Control")
    print("=" * 60)
    
    # Show all available tools
    from agentmanager.core.tools import get_available_tools
    all_tools = get_available_tools()
    print(f"📋 All available tools: {all_tools}")
    
    # Test 1: Create agent with specific tools
    print(f"\n🔹 Test 1: Creating agent with limited tools")
    try:
        agent1 = amg.load_agent(
            base_agent="test_agent_1", 
            tools=["add", "multiply", "greet"]
        )
        print(f"✅ Agent created successfully!")
        print(f"   Assigned tools: {agent1.get_assigned_tools()}")
        
        # Test tool execution
        print(f"\n🧪 Testing tool execution:")
        
        # Allowed tools
        print(f"   Testing allowed tools:")
        try:
            result = agent1.execute_tool("add", 5, 3)
            print(f"   ✅ add(5, 3) = {result}")
        except Exception as e:
            print(f"   ❌ add error: {e}")
        
        try:
            result = agent1.execute_tool("multiply", 4, 7)
            print(f"   ✅ multiply(4, 7) = {result}")
        except Exception as e:
            print(f"   ❌ multiply error: {e}")
        
        try:
            result = agent1.execute_tool("greet", "Alice")
            print(f"   ✅ greet('Alice') = {result}")
        except Exception as e:
            print(f"   ❌ greet error: {e}")
        
        # Denied tools
        print(f"   Testing denied tools:")
        try:
            result = agent1.execute_tool("get_weather", "Paris")
            print(f"   ❌ get_weather should be denied: {result}")
        except PermissionError as e:
            print(f"   ✅ get_weather correctly denied: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
        
        try:
            result = agent1.execute_tool("process_text", "hello", "uppercase")
            print(f"   ❌ process_text should be denied: {result}")
        except PermissionError as e:
            print(f"   ✅ process_text correctly denied: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
        
        # Test access checking
        print(f"\n🔍 Testing access control:")
        for tool in ["add", "multiply", "greet", "get_weather", "process_text"]:
            can_access = agent1.can_access_tool(tool)
            status = "✅" if can_access else "❌"
            print(f"   {status} {tool}: {'Can access' if can_access else 'Cannot access'}")
        
        # Test tool metadata
        print(f"\n📊 Testing tool metadata:")
        for tool in ["add", "get_weather"]:
            metadata = agent1.get_tool_metadata(tool)
            if metadata:
                print(f"   ✅ {tool}: {metadata['description']}")
            else:
                print(f"   ❌ {tool}: No access or not found")
        
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
    
    # Test 2: Create agent with different tools
    print(f"\n🔹 Test 2: Creating agent with different tools")
    try:
        agent2 = amg.load_agent(
            base_agent="test_agent_2", 
            tools=["get_weather", "process_text"]
        )
        print(f"✅ Agent created successfully!")
        print(f"   Assigned tools: {agent2.get_assigned_tools()}")
        
        # Test tool execution
        print(f"\n🧪 Testing tool execution:")
        
        # Allowed tools
        try:
            result = agent2.execute_tool("get_weather", "Tokyo", "celsius")
            print(f"   ✅ get_weather('Tokyo', 'celsius') = {result}")
        except Exception as e:
            print(f"   ❌ get_weather error: {e}")
        
        try:
            result = agent2.execute_tool("process_text", "hello world", "uppercase")
            print(f"   ✅ process_text('hello world', 'uppercase') = {result}")
        except Exception as e:
            print(f"   ❌ process_text error: {e}")
        
        # Denied tools
        try:
            result = agent2.execute_tool("add", 2, 3)
            print(f"   ❌ add should be denied: {result}")
        except PermissionError as e:
            print(f"   ✅ add correctly denied: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
        
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
    
    # Test 3: Create agent with no tools
    print(f"\n🔹 Test 3: Creating agent with no tools")
    try:
        agent3 = amg.load_agent(base_agent="test_agent_3")
        print(f"✅ Agent created successfully!")
        print(f"   Assigned tools: {agent3.get_assigned_tools()}")
        
        # Test tool execution (should all be denied)
        print(f"\n🧪 Testing tool execution (should all be denied):")
        for tool in ["add", "get_weather", "greet"]:
            try:
                result = agent3.execute_tool(tool, "test")
                print(f"   ❌ {tool} should be denied: {result}")
            except PermissionError as e:
                print(f"   ✅ {tool} correctly denied: {e}")
            except Exception as e:
                print(f"   ❌ Unexpected error: {e}")
        
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
    
    print(f"\n✅ All tests completed!")
    print(f"\n💡 Usage Summary:")
    print(f"   agent = amg.load_agent(base_agent='my_agent', tools=['add', 'multiply'])")
    print(f"   result = agent.execute_tool('add', 5, 3)  # ✅ Allowed")
    print(f"   result = agent.execute_tool('get_weather', 'Paris')  # ❌ Denied")

if __name__ == "__main__":
    main()
