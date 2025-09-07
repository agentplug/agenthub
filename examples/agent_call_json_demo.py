#!/usr/bin/env python3
"""
Demo: Generate Agent Call JSON with Tool Context

This demonstrates how to generate the JSON format for calling agents
with tool context, similar to the example you provided.
"""

# First register some tools by importing the server
from examples.mcp_tool_server import *

# Now test with real agents
import agentmanager as amg

def main():
    print("🤖 Agent Call JSON Demo - Tool Context Integration")
    print("=" * 60)
    
    # Test 1: Load agent with tools
    print("\n📋 Test 1: Load Agent with Tools")
    print("-" * 40)
    
    try:
        # Load analysis agent with tools
        analysis_agent = amg.load_agent("agentplug/analysis-agent", tools=["add", "multiply", "process_text"])
        print(f"✅ Loaded analysis agent: {analysis_agent}")
        print(f"🔧 Assigned tools: {analysis_agent.get_assigned_tools()}")
        
    except Exception as e:
        print(f"❌ Error loading analysis agent: {e}")
        return
    
    # Test 2: Generate tool context JSON
    print("\n📋 Test 2: Generate Tool Context JSON")
    print("-" * 40)
    
    try:
        # Get tool context in JSON format
        tool_context = analysis_agent.get_tool_context_json()
        print("🔍 Tool Context JSON:")
        print(f"  - Available tools: {tool_context['available_tools']}")
        print(f"  - Tool descriptions: {tool_context['tool_descriptions']}")
        print(f"  - Tool usage examples: {tool_context['tool_usage_examples']}")
        
    except Exception as e:
        print(f"❌ Error generating tool context: {e}")
    
    # Test 3: Generate complete agent call JSON
    print("\n📋 Test 3: Generate Complete Agent Call JSON")
    print("-" * 40)
    
    try:
        # Generate agent call JSON like your example
        agent_call_json = analysis_agent.generate_agent_call_json(
            method="analyze_text",
            parameters={
                "text": "What are the latest AI trends?",
                "analysis_type": "general"
            }
        )
        
        print("📝 Complete Agent Call JSON:")
        print("=" * 50)
        print(agent_call_json)
        
    except Exception as e:
        print(f"❌ Error generating agent call JSON: {e}")
    
    # Test 4: Show different agent with different tools
    print("\n📋 Test 4: Different Agent, Different Tools")
    print("-" * 40)
    
    try:
        # Load coding agent with different tools
        coding_agent = amg.load_agent("agentplug/coding-agent", tools=["add", "subtract", "greet"])
        print(f"✅ Loaded coding agent: {coding_agent}")
        
        # Generate agent call JSON for coding agent
        coding_call_json = coding_agent.generate_agent_call_json(
            method="generate_code",
            parameters={
                "description": "Create a Python function that calculates compound interest",
                "language": "python"
            }
        )
        
        print("\n📝 Coding Agent Call JSON:")
        print("=" * 50)
        print(coding_call_json)
        
    except Exception as e:
        print(f"❌ Error generating coding agent call: {e}")
    
    # Test 5: Show how to use the JSON for actual agent calls
    print("\n📋 Test 5: How to Use the JSON for Agent Calls")
    print("-" * 40)
    
    try:
        # Generate the command that would be used to call the agent
        agent_path = "/Users/nguyennm/.agenthub/agents/agentplug/analysis-agent/agent.py"
        agent_call_json = analysis_agent.generate_agent_call_json(
            method="analyze_text",
            parameters={
                "text": "What are the latest AI trends?",
                "analysis_type": "general"
            }
        )
        
        # Escape the JSON for shell command
        import json
        escaped_json = json.dumps(agent_call_json)
        
        print("🐚 Shell Command to Call Agent:")
        print("=" * 50)
        print(f"python {agent_path} {escaped_json}")
        
        print("\n💡 This command would:")
        print("  - Call the analysis-agent with the analyze_text method")
        print("  - Pass the text and analysis_type parameters")
        print("  - Provide tool context with add, multiply, and process_text tools")
        print("  - Include tool descriptions and usage examples")
        
    except Exception as e:
        print(f"❌ Error generating shell command: {e}")
    
    # Test 6: Show tool context customization
    print("\n📋 Test 6: Tool Context Customization")
    print("-" * 40)
    
    try:
        print("🔧 You can customize the tool context by:")
        print("  - Assigning different tools to different agents")
        print("  - Modifying tool descriptions in the registry")
        print("  - Adding custom tool usage examples")
        print("  - Including additional context information")
        
        # Show how to get just the tool context part
        tool_context = analysis_agent.get_tool_context_json()
        print(f"\n📋 Tool Context Only:")
        print(f"  Available tools: {tool_context['available_tools']}")
        print(f"  Descriptions: {list(tool_context['tool_descriptions'].keys())}")
        print(f"  Usage examples: {list(tool_context['tool_usage_examples'].keys())}")
        
    except Exception as e:
        print(f"❌ Error showing customization: {e}")
    
    print("\n🎉 Agent Call JSON Demo Complete!")
    print("\n📊 Summary:")
    print("  ✅ Generate tool context in JSON format")
    print("  ✅ Create complete agent call JSON with method and parameters")
    print("  ✅ Support different agents with different tool sets")
    print("  ✅ Generate shell commands for agent execution")
    print("  ✅ Customize tool context per agent")
    print("  ✅ Compatible with existing agent execution format")

if __name__ == "__main__":
    main()
