#!/usr/bin/env python3
"""
Demo: Tool Instructions Sent to Agents

This demonstrates how tool instructions are automatically generated
and injected into agents, showing them what tools are available
and how to use them.
"""

# First register some tools by importing the server
from examples.mcp_tool_server import *

# Now test with real agents
import agentmanager as amg

def main():
    print("🤖 Tool Instructions Demo - How Agents Learn About Tools")
    print("=" * 65)
    
    # Test 1: Load agent with tools and show instructions
    print("\n📋 Test 1: Load Agent with Tools")
    print("-" * 40)
    
    try:
        # Load analysis agent with math tools
        analysis_agent = amg.load_agent("agentplug/analysis-agent", tools=["add", "multiply", "process_text"])
        print(f"✅ Loaded analysis agent: {analysis_agent}")
        print(f"🔧 Assigned tools: {analysis_agent.get_assigned_tools()}")
        
        # Show tool instructions that would be sent to the agent
        print("\n📝 TOOL INSTRUCTIONS SENT TO AGENT:")
        print("=" * 50)
        instructions = analysis_agent.get_tool_instructions()
        print(instructions)
        
    except Exception as e:
        print(f"❌ Error loading analysis agent: {e}")
        return
    
    # Test 2: Load different agent with different tools
    print("\n📋 Test 2: Different Agent, Different Tools")
    print("-" * 40)
    
    try:
        # Load coding agent with different tools
        coding_agent = amg.load_agent("agentplug/coding-agent", tools=["add", "subtract", "greet"])
        print(f"✅ Loaded coding agent: {coding_agent}")
        print(f"🔧 Assigned tools: {coding_agent.get_assigned_tools()}")
        
        # Show different tool instructions
        print("\n📝 TOOL INSTRUCTIONS SENT TO CODING AGENT:")
        print("=" * 50)
        instructions = coding_agent.get_tool_instructions()
        print(instructions)
        
    except Exception as e:
        print(f"❌ Error loading coding agent: {e}")
        return
    
    # Test 3: Show tool context information
    print("\n📋 Test 3: Tool Context Information")
    print("-" * 40)
    
    try:
        # Get tool context for analysis agent
        context = analysis_agent.get_tool_context()
        print("🔍 Analysis Agent Tool Context:")
        print(f"  - Assigned tools: {context['assigned_tools']}")
        print(f"  - Has execute_tool method: {hasattr(context['execute_tool_method'], '__call__')}")
        print(f"  - Has can_access_tool method: {hasattr(context['can_access_tool_method'], '__call__')}")
        print(f"  - Has get_tool_metadata method: {hasattr(context['get_tool_metadata_method'], '__call__')}")
        
        # Get tool context for coding agent
        context = coding_agent.get_tool_context()
        print("\n🔍 Coding Agent Tool Context:")
        print(f"  - Assigned tools: {context['assigned_tools']}")
        print(f"  - Has execute_tool method: {hasattr(context['execute_tool_method'], '__call__')}")
        print(f"  - Has can_access_tool method: {hasattr(context['can_access_tool_method'], '__call__')}")
        print(f"  - Has get_tool_metadata method: {hasattr(context['get_tool_metadata_method'], '__call__')}")
        
    except Exception as e:
        print(f"❌ Error getting tool context: {e}")
    
    # Test 4: Demonstrate tool execution with instructions
    print("\n📋 Test 4: Tool Execution with Instructions")
    print("-" * 40)
    
    try:
        print("🔧 Analysis Agent Tool Execution:")
        print("  Based on instructions, the agent can now use tools like this:")
        
        # Simulate agent using tools based on instructions
        result = analysis_agent.execute_tool("add", 15, 25)
        print(f"  ✅ execute_tool('add', 15, 25) = {result}")
        
        result = analysis_agent.execute_tool("multiply", 6, 7)
        print(f"  ✅ execute_tool('multiply', 6, 7) = {result}")
        
        print("\n🔧 Coding Agent Tool Execution:")
        print("  Based on instructions, the agent can now use tools like this:")
        
        result = coding_agent.execute_tool("add", 100, 200)
        print(f"  ✅ execute_tool('add', 100, 200) = {result}")
        
        result = coding_agent.execute_tool("greet", "Developer")
        print(f"  ✅ execute_tool('greet', 'Developer') = {result}")
        
    except Exception as e:
        print(f"❌ Error executing tools: {e}")
    
    # Test 5: Show how instructions help with error handling
    print("\n📋 Test 5: Error Handling with Instructions")
    print("-" * 40)
    
    try:
        print("🚫 Testing denied tool access (as per instructions):")
        
        # Try to use a tool the agent doesn't have access to
        try:
            result = analysis_agent.execute_tool("greet", "User")
            print(f"  ❌ execute_tool('greet', 'User') = {result} (should be denied)")
        except PermissionError as e:
            print(f"  ✅ Correctly denied: {e}")
            print("  💡 The agent knows from instructions that it can't use 'greet'")
        
        try:
            result = coding_agent.execute_tool("multiply", 5, 6)
            print(f"  ❌ execute_tool('multiply', 5, 6) = {result} (should be denied)")
        except PermissionError as e:
            print(f"  ✅ Correctly denied: {e}")
            print("  💡 The agent knows from instructions that it can't use 'multiply'")
        
    except Exception as e:
        print(f"❌ Error testing denied access: {e}")
    
    print("\n🎉 Tool Instructions Demo Complete!")
    print("\n📊 Summary:")
    print("  ✅ Agents receive detailed tool instructions automatically")
    print("  ✅ Instructions include tool descriptions and usage examples")
    print("  ✅ Each agent gets instructions only for their assigned tools")
    print("  ✅ Instructions include usage guidelines and error handling")
    print("  ✅ Tool context is injected into agent environment")
    print("  ✅ Agents can execute tools based on the instructions")

if __name__ == "__main__":
    main()
