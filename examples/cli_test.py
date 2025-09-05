#!/usr/bin/env python3
"""CLI Test Script for Step 1 Components.

This script demonstrates the CLI commands with actual tools.
"""

from agentmanager.core.tools import tool, get_global_registry, get_agent_tools_tracker


def setup_test_environment():
    """Set up test tools and assignments for CLI testing."""
    print("🔧 Setting up test environment...")
    
    # Check if tools are already registered
    registry = get_global_registry()
    existing_tools = registry.list_tools()
    
    if not existing_tools:
        # Define some test tools only if not already registered
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
    else:
        print("   Tools already registered, using existing ones...")
    
    # Set up agent assignments
    tracker = get_agent_tools_tracker()
    tracker.assign_tools_to_agent("analysis-agent", ["data_analyzer", "file_processor"])
    tracker.assign_tools_to_agent("coding-agent", ["code_generator", "file_processor"])
    tracker.assign_tools_to_agent("general-agent", ["data_analyzer", "code_generator"])
    
    # Record some usage
    tracker.record_tool_usage("analysis-agent", "data_analyzer")
    tracker.record_tool_usage("analysis-agent", "data_analyzer")
    tracker.record_tool_usage("coding-agent", "code_generator")
    tracker.record_tool_usage("general-agent", "data_analyzer")
    
    print("✅ Test environment set up!")
    return tracker


def test_cli_commands():
    """Test various CLI commands."""
    print("\n🧪 Testing CLI Commands...")
    
    # Set up environment
    tracker = setup_test_environment()
    
    print("\n1. Testing 'tools list' command:")
    print("   Run: python -m agentmanager.cli.main tools list")
    print("   This should show the 3 registered tools")
    
    print("\n2. Testing 'tools info' command:")
    print("   Run: python -m agentmanager.cli.main tools info data_analyzer")
    print("   This should show detailed info about the data_analyzer tool")
    
    print("\n3. Testing 'tools test' command:")
    print("   Run: python -m agentmanager.cli.main tools test data_analyzer --params '{\"data\": \"test\", \"format\": \"json\"}'")
    print("   This should execute the tool with the given parameters")
    
    print("\n4. Testing 'tools tracker' command:")
    print("   Run: python -m agentmanager.cli.main tools tracker")
    print("   This should show the agent-tool assignments")
    
    print("\n5. Testing 'tools agent' command:")
    print("   Run: python -m agentmanager.cli.main tools agent analysis-agent")
    print("   This should show tools assigned to analysis-agent")
    
    print("\n6. Testing 'tools stats' command:")
    print("   Run: python -m agentmanager.cli.main tools stats")
    print("   This should show usage statistics")
    
    print("\n7. Testing 'tools assign' command:")
    print("   Run: python -m agentmanager.cli.main tools assign new-agent data_analyzer code_generator")
    print("   This should assign tools to a new agent")
    
    print("\n8. Testing 'tools remove' command:")
    print("   Run: python -m agentmanager.cli.main tools remove new-agent")
    print("   This should remove all tools from the agent")


def show_current_state():
    """Show the current state of the system."""
    print("\n📊 Current System State:")
    
    registry = get_global_registry()
    tracker = get_agent_tools_tracker()
    
    print(f"   Registered tools: {registry.list_tools()}")
    print(f"   Total tools: {registry.get_tool_count()}")
    
    assignments = tracker.get_all_assignments()
    print(f"   Agent assignments: {assignments}")
    
    status = tracker.get_tracker_status()
    print(f"   Total agents: {status['total_agents']}")
    print(f"   Total assignments: {status['total_assignments']}")


def main():
    """Main function."""
    print("🚀 CLI Test for Step 1 Components")
    print("=" * 40)
    
    # Set up test environment
    setup_test_environment()
    
    # Show current state
    show_current_state()
    
    # Test CLI commands
    test_cli_commands()
    
    print("\n✅ CLI test setup complete!")
    print("\nNow you can run the CLI commands shown above to test the system.")


if __name__ == "__main__":
    main()
