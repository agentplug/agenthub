#!/usr/bin/env python3
"""Step 1 Demo: Modular Core Architecture and Tool System.

This demo shows the foundational components implemented in Step 1:
- @tool decorator system
- Tool registry
- Agent-Tools Tracker
- CLI commands
"""

from agentmanager.core.tools import tool, get_global_registry, get_agent_tools_tracker


def main():
    print("🚀 Step 1 Demo: Modular Core Architecture and Tool System")
    print("=" * 60)
    
    # Step 1: Define some tools using @tool decorator
    print("\n1. Defining tools with @tool decorator...")
    
    @tool(name="data_analyzer", description="Analyze data and provide insights", tags=["analysis", "data"])
    def analyze_data(data: str, format: str = "json") -> dict:
        """Analyze the provided data and return insights."""
        return {
            "insights": f"Analyzed {len(data)} characters of {format} data",
            "summary": f"Data appears to be {'valid' if data else 'empty'}",
            "recommendations": ["Consider data validation", "Add error handling"]
        }
    
    @tool(name="file_processor", description="Process files and return metadata", tags=["file", "processing"])
    def process_file(file_path: str, include_content: bool = False) -> dict:
        """Process a file and return metadata."""
        return {
            "file_path": file_path,
            "size": len(file_path) * 10,  # Simulated size
            "type": "text" if file_path.endswith('.txt') else "unknown",
            "content": file_path if include_content else None
        }
    
    @tool(name="code_generator", description="Generate code based on requirements", tags=["code", "generation"])
    def generate_code(requirements: str, language: str = "python") -> str:
        """Generate code based on requirements."""
        return f"# Generated {language} code for: {requirements}\nprint('Hello, World!')"
    
    print("✅ Tools defined and auto-registered!")
    
    # Step 2: Show tool registry
    print("\n2. Tool Registry Status...")
    registry = get_global_registry()
    tools = registry.list_tools()
    print(f"   Registered tools: {tools}")
    print(f"   Total tools: {registry.get_tool_count()}")
    
    # Step 3: Test tool execution
    print("\n3. Testing tool execution...")
    try:
        result1 = registry.execute_tool("data_analyzer", data="Hello, World!", format="text")
        print(f"   data_analyzer result: {result1}")
        
        result2 = registry.execute_tool("file_processor", file_path="test.txt", include_content=True)
        print(f"   file_processor result: {result2}")
        
        result3 = registry.execute_tool("code_generator", requirements="print hello", language="python")
        print(f"   code_generator result: {result3}")
    except Exception as e:
        print(f"   Error executing tools: {e}")
    
    # Step 4: Agent-Tools Tracker
    print("\n4. Agent-Tools Tracker...")
    tracker = get_agent_tools_tracker()
    
    # Assign tools to agents
    print("   Assigning tools to agents...")
    tracker.assign_tools_to_agent("analysis-agent", ["data_analyzer", "file_processor"])
    tracker.assign_tools_to_agent("coding-agent", ["code_generator", "file_processor"])
    tracker.assign_tools_to_agent("general-agent", ["data_analyzer", "code_generator"])
    
    # Show assignments
    assignments = tracker.get_all_assignments()
    print(f"   Agent assignments: {assignments}")
    
    # Show bidirectional lookup
    print("   Bidirectional lookup:")
    print(f"     analysis-agent tools: {tracker.get_agent_tools('analysis-agent')}")
    print(f"     Agents with data_analyzer: {tracker.get_agents_with_tool('data_analyzer')}")
    print(f"     Agents with file_processor: {tracker.get_agents_with_tool('file_processor')}")
    
    # Step 5: Usage tracking
    print("\n5. Usage tracking...")
    tracker.record_tool_usage("analysis-agent", "data_analyzer")
    tracker.record_tool_usage("analysis-agent", "data_analyzer")
    tracker.record_tool_usage("coding-agent", "code_generator")
    
    # Show usage stats
    tool_stats = tracker.get_tool_usage_stats()
    agent_stats = tracker.get_agent_usage_stats()
    print(f"   Tool usage stats: {tool_stats}")
    print(f"   Agent usage stats: {agent_stats}")
    
    # Step 6: Tracker status
    print("\n6. Tracker status...")
    status = tracker.get_tracker_status()
    print(f"   Total agents: {status['total_agents']}")
    print(f"   Active agents: {status['active_agents']}")
    print(f"   Total tools: {status['total_tools']}")
    print(f"   Total assignments: {status['total_assignments']}")
    
    print("\n✅ Step 1 Demo completed successfully!")
    print("\nNext steps:")
    print("- Run 'python -m agentmanager.cli.main tools list' to see CLI")
    print("- Run 'python -m agentmanager.cli.main tools tracker' to see tracker status")
    print("- Run 'python -m agentmanager.cli.main tools assign <agent> <tools>' to assign tools")


if __name__ == "__main__":
    main()

