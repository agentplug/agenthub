#!/usr/bin/env python3
"""
Simple Framework Demo - Complete workflow using working MCP client

This demonstrates the complete flow:
1. Tools are hosted in mcp_tool_server.py
2. Framework discovers tools through MCP protocol (using working client)
3. User declares agents with tool assignments
4. Framework generates agent call JSON with tool context
"""

import asyncio
import json
import subprocess
from pathlib import Path
from mcp.client.sse import sse_client
from mcp import ClientSession

class SimpleFrameworkDemo:
    """Simple framework demo using working MCP client approach."""
    
    def __init__(self, server_url: str = "http://localhost:8000/sse"):
        self.server_url = server_url
        self.discovered_tools = {}
        self.agents = {}
    
    async def discover_tools(self) -> dict:
        """Discover tools using the working client approach."""
        print("🔍 Discovering tools from MCP server...")
        
        try:
            async with sse_client(self.server_url) as (read, write):
                async with ClientSession(read, write) as session:
                    # List all available tools
                    tools = await session.list_tools()
                    
                    if hasattr(tools, 'tools'):
                        for tool in tools.tools:
                            tool_info = {
                                "name": tool.name,
                                "description": tool.description,
                                "input_schema": getattr(tool, 'inputSchema', {}),
                                "output_schema": getattr(tool, 'outputSchema', {}),
                                "available": True
                            }
                            self.discovered_tools[tool.name] = tool_info
                    
                    print(f"✅ Discovered {len(self.discovered_tools)} tools from MCP server")
                    return self.discovered_tools
                    
        except Exception as e:
            print(f"❌ Error discovering tools: {e}")
            return {}
    
    def declare_agents(self) -> dict:
        """Declare agents with tool assignments."""
        print("\n🤖 Declaring agents with tool assignments...")
        
        # Import agentmanager for agent declaration
        import agentmanager as amg
        
        agents = {}
        
        # Agent 1: Analysis Agent
        print("🔍 Declaring Analysis Agent...")
        try:
            analysis_agent = amg.load_agent(
                "agentplug/analysis-agent", 
                tools=["add", "multiply", "process_text"]
            )
            agents["analysis_agent"] = analysis_agent
            print(f"✅ Analysis Agent: {analysis_agent.name}")
            print(f"   Assigned tools: {analysis_agent.get_assigned_tools()}")
        except Exception as e:
            print(f"❌ Error declaring analysis agent: {e}")
        
        # Agent 2: Coding Agent
        print("\n💻 Declaring Coding Agent...")
        try:
            coding_agent = amg.load_agent(
                "agentplug/coding-agent", 
                tools=["add", "subtract", "greet"]
            )
            agents["coding_agent"] = coding_agent
            print(f"✅ Coding Agent: {coding_agent.name}")
            print(f"   Assigned tools: {coding_agent.get_assigned_tools()}")
        except Exception as e:
            print(f"❌ Error declaring coding agent: {e}")
        
        self.agents = agents
        return agents
    
    def generate_tool_context(self, assigned_tools: list) -> dict:
        """Generate tool context from discovered tools."""
        tool_descriptions = {}
        tool_usage_examples = {}
        
        for tool_name in assigned_tools:
            if tool_name in self.discovered_tools:
                tool_info = self.discovered_tools[tool_name]
                tool_descriptions[tool_name] = tool_info['description']
                
                # Generate usage examples based on tool type
                if tool_name in ["add", "subtract", "multiply", "divide"]:
                    tool_usage_examples[tool_name] = [f"{tool_name}({{\"a\": \"number1\", \"b\": \"number2\"}})"]
                elif tool_name == "greet":
                    tool_usage_examples[tool_name] = [f"{tool_name}({{\"name\": \"string\"}})"]
                elif tool_name == "get_weather":
                    tool_usage_examples[tool_name] = [f"{tool_name}({{\"location\": \"string\"}})"]
                elif tool_name == "process_text":
                    tool_usage_examples[tool_name] = [f"{tool_name}({{\"text\": \"string\", \"operation\": \"string\"}})"]
                else:
                    tool_usage_examples[tool_name] = [f"{tool_name}({{\"param\": \"value\"}})"]
            else:
                print(f"⚠️  Tool '{tool_name}' not found in discovered tools")
        
        return {
            "available_tools": assigned_tools,
            "tool_descriptions": tool_descriptions,
            "tool_usage_examples": tool_usage_examples
        }
    
    def generate_agent_call_json(self, agent_name: str, method: str, parameters: dict) -> str:
        """Generate complete agent call JSON with tool context."""
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found")
        
        agent = self.agents[agent_name]
        assigned_tools = agent.get_assigned_tools()
        
        # Generate tool context from discovered tools
        tool_context = self.generate_tool_context(assigned_tools)
        
        call_data = {
            "method": method,
            "parameters": parameters,
            "tool_context": tool_context
        }
        
        return json.dumps(call_data, indent=2)
    
    def show_agent_execution_command(self, agent_name: str, method: str, parameters: dict) -> str:
        """Show the command that would be used to execute the agent."""
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found")
        
        agent = self.agents[agent_name]
        
        # Get agent path
        agent_path = f"/Users/nguyennm/.agenthub/agents/{agent.namespace}/{agent.agent_name}/agent.py"
        
        # Generate agent call JSON
        agent_call_json = self.generate_agent_call_json(agent_name, method, parameters)
        
        # Escape the JSON for shell command
        escaped_json = json.dumps(agent_call_json)
        
        return f"python {agent_path} {escaped_json}"

async def main():
    """Main function demonstrating the complete framework integration."""
    print("🏗️ Simple Framework Demo - Complete Tool Discovery and Agent Declaration")
    print("=" * 80)
    
    # Create framework demo
    framework = SimpleFrameworkDemo()
    
    # Step 1: Discover available tools from MCP server
    print("\n📋 Step 1: Tool Discovery")
    print("-" * 40)
    tools = await framework.discover_tools()
    
    if not tools:
        print("❌ No tools discovered. Make sure mcp_tool_server.py is running!")
        print("💡 Run: python examples/mcp_tool_server.py")
        return
    
    # Show discovered tools
    print(f"\n🔍 Discovered {len(tools)} tools:")
    for tool_name, tool_info in tools.items():
        print(f"  • {tool_name}: {tool_info['description']}")
    
    # Step 2: Declare agents with tool assignments
    print("\n📋 Step 2: Agent Declaration")
    print("-" * 40)
    agents = framework.declare_agents()
    
    if not agents:
        print("❌ No agents declared successfully")
        return
    
    # Step 3: Generate agent call JSON with tool context
    print("\n📋 Step 3: Tool Context Generation")
    print("-" * 40)
    
    # Example 1: Analysis Agent
    print("🔍 Analysis Agent Call JSON:")
    analysis_json = framework.generate_agent_call_json(
        "analysis_agent",
        "analyze_text",
        {
            "text": "What are the latest AI trends?",
            "analysis_type": "general"
        }
    )
    print(analysis_json)
    
    # Example 2: Coding Agent
    print("\n💻 Coding Agent Call JSON:")
    coding_json = framework.generate_agent_call_json(
        "coding_agent",
        "generate_code",
        {
            "description": "Create a Python function that calculates compound interest",
            "language": "python"
        }
    )
    print(coding_json)
    
    # Step 4: Show execution commands
    print("\n📋 Step 4: Agent Execution Commands")
    print("-" * 40)
    
    # Analysis Agent command
    print("🔍 Analysis Agent Execution Command:")
    analysis_cmd = framework.show_agent_execution_command(
        "analysis_agent",
        "analyze_text",
        {
            "text": "What are the latest AI trends?",
            "analysis_type": "general"
        }
    )
    print(f"Command: {analysis_cmd}")
    
    # Coding Agent command
    print("\n💻 Coding Agent Execution Command:")
    coding_cmd = framework.show_agent_execution_command(
        "coding_agent",
        "generate_code",
        {
            "description": "Create a Python function that calculates compound interest",
            "language": "python"
        }
    )
    print(f"Command: {coding_cmd}")
    
    print("\n🎉 Simple Framework Demo Complete!")
    print("\n📊 Summary:")
    print("  ✅ Tools discovered from MCP server")
    print("  ✅ Agents declared with tool assignments")
    print("  ✅ Tool context generated from discovered tools")
    print("  ✅ Agent call JSON generated with tool injection")
    print("  ✅ Execution commands ready for agent calls")
    print("\n💡 This demonstrates your complete workflow:")
    print("  1. Tools hosted in mcp_tool_server.py")
    print("  2. Framework discovers tools through MCP protocol")
    print("  3. User declares agents with tool assignments")
    print("  4. Framework generates agent call JSON with tool context")
    print("  5. Agents executed with tool injection via command format")

if __name__ == "__main__":
    asyncio.run(main())
