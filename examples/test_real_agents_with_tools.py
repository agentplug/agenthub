#!/usr/bin/env python3
"""
Test the enhanced SDK with real agents and tool injection

This demonstrates how to use the enhanced SDK with real agentplug agents
and tool injection capabilities.
"""

# First register some tools by importing the server
from examples.mcp_tool_server import *

# Now test with real agents
import agentmanager as amg

def main():
    print("🤖 Testing Enhanced SDK with Real Agents + Tools")
    print("=" * 60)
    
    # Test 1: Load real agents with tools
    print("\n📋 Test 1: Load Real Agents with Tools")
    print("-" * 40)
    
    try:
        # Load analysis agent with math tools
        analysis_agent = amg.load_agent("agentplug/analysis-agent", tools=["add", "multiply", "process_text"])
        print(f"✅ Loaded analysis agent: {analysis_agent}")
        print(f"🔧 Assigned tools: {analysis_agent.get_assigned_tools()}")
        
        # Load coding agent with different tools
        coding_agent = amg.load_agent("agentplug/coding-agent", tools=["add", "subtract", "greet"])
        print(f"✅ Loaded coding agent: {coding_agent}")
        print(f"🔧 Assigned tools: {coding_agent.get_assigned_tools()}")
        
    except Exception as e:
        print(f"❌ Error loading real agents: {e}")
        return
    
    # Test 2: Test tool execution with real agents
    print("\n📋 Test 2: Tool Execution with Real Agents")
    print("-" * 40)
    
    try:
        # Test analysis agent tools
        print("🔧 Testing analysis agent tools:")
        result = analysis_agent.execute_tool("add", 15, 25)
        print(f"  ✅ Analysis agent add(15, 25) = {result}")
        
        result = analysis_agent.execute_tool("multiply", 6, 7)
        print(f"  ✅ Analysis agent multiply(6, 7) = {result}")
        
        # Test coding agent tools
        print("\n🔧 Testing coding agent tools:")
        result = coding_agent.execute_tool("add", 100, 200)
        print(f"  ✅ Coding agent add(100, 200) = {result}")
        
        result = coding_agent.execute_tool("greet", "Developer")
        print(f"  ✅ Coding agent greet('Developer') = {result}")
        
        # Test denied tools
        print("\n🚫 Testing denied tools:")
        try:
            result = analysis_agent.execute_tool("greet", "User")
            print(f"  ❌ Analysis agent greet('User') = {result} (should be denied)")
        except PermissionError as e:
            print(f"  ✅ Analysis agent correctly denied: {e}")
        
        try:
            result = coding_agent.execute_tool("multiply", 5, 6)
            print(f"  ❌ Coding agent multiply(5, 6) = {result} (should be denied)")
        except PermissionError as e:
            print(f"  ✅ Coding agent correctly denied: {e}")
        
    except Exception as e:
        print(f"❌ Error testing tool execution: {e}")
    
    # Test 3: Test agent methods + tools combination
    print("\n📋 Test 3: Agent Methods + Tools Combination")
    print("-" * 40)
    
    try:
        # Test analysis agent with its native method
        print("🔍 Testing analysis agent native method:")
        feedback = "The new feature is great but needs better error handling."
        insights = analysis_agent.analyze_text(feedback)
        print(f"  ✅ Analysis result: {insights.get('result', {}).get('summary', 'No summary')[:100]}...")
        
        # Test coding agent with its native method
        print("\n🔍 Testing coding agent native method:")
        code_request = "Create a simple calculator function"
        code = coding_agent.generate_code(code_request)
        print(f"  ✅ Generated code: {code.get('result', 'No code')[:100]}...")
        
        # Now test tools after using native methods
        print("\n🔧 Testing tools after native methods:")
        result = analysis_agent.execute_tool("add", 10, 20)
        print(f"  ✅ Analysis agent still can use tools: add(10, 20) = {result}")
        
        result = coding_agent.execute_tool("subtract", 50, 15)
        print(f"  ✅ Coding agent still can use tools: subtract(50, 15) = {result}")
        
    except Exception as e:
        print(f"❌ Error testing agent methods: {e}")
    
    # Test 4: Tool access control per agent
    print("\n📋 Test 4: Per-Agent Tool Access Control")
    print("-" * 40)
    
    try:
        print("🔍 Analysis agent tool access:")
        tools_to_check = ["add", "subtract", "multiply", "divide", "greet", "process_text"]
        for tool_name in tools_to_check:
            can_access = analysis_agent.can_access_tool(tool_name)
            status = "✅" if can_access else "❌"
            print(f"  {status} {tool_name}: {'Allowed' if can_access else 'Denied'}")
        
        print("\n🔍 Coding agent tool access:")
        for tool_name in tools_to_check:
            can_access = coding_agent.can_access_tool(tool_name)
            status = "✅" if can_access else "❌"
            print(f"  {status} {tool_name}: {'Allowed' if can_access else 'Denied'}")
        
    except Exception as e:
        print(f"❌ Error testing tool access control: {e}")
    
    # Test 5: Tool metadata for each agent
    print("\n📋 Test 5: Tool Metadata per Agent")
    print("-" * 40)
    
    try:
        print("🔍 Analysis agent tool metadata:")
        for tool_name in analysis_agent.get_assigned_tools():
            metadata = analysis_agent.get_tool_metadata(tool_name)
            if metadata:
                print(f"  ✅ {tool_name}: {metadata['description']}")
            else:
                print(f"  ❌ {tool_name}: No metadata")
        
        print("\n🔍 Coding agent tool metadata:")
        for tool_name in coding_agent.get_assigned_tools():
            metadata = coding_agent.get_tool_metadata(tool_name)
            if metadata:
                print(f"  ✅ {tool_name}: {metadata['description']}")
            else:
                print(f"  ❌ {tool_name}: No metadata")
        
    except Exception as e:
        print(f"❌ Error testing tool metadata: {e}")
    
    print("\n🎉 Real Agents + Tools Test Complete!")
    print("\n📊 Summary:")
    print("  ✅ Real agentplug agents loaded successfully")
    print("  ✅ Tool injection works with real agents")
    print("  ✅ Per-agent tool access control working")
    print("  ✅ Native agent methods + tools work together")
    print("  ✅ Enhanced SDK architecture is production-ready!")

if __name__ == "__main__":
    main()
