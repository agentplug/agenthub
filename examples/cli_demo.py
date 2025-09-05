#!/usr/bin/env python3
"""CLI Demo Script for Step 1 Components.

This script demonstrates the CLI functionality by directly calling the CLI functions.
"""

from agentmanager.cli.commands.tools.main import tools_list, tools_tracker, tools_agent, tools_stats
from agentmanager.core.tools import tool, get_global_registry, get_agent_tools_tracker


def setup_demo_environment():
    """Set up demo environment with tools and assignments."""
    print("🔧 Setting up demo environment...")
    
    # Clear existing state
    registry = get_global_registry()
    tracker = get_agent_tools_tracker()
    registry.clear()
    
    # Clear tracker assignments
    for agent_name in list(tracker._agent_assignments.keys()):
        tracker.remove_agent_tools(agent_name)
    tracker._usage_stats.clear()
    
    # Define demo tools
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
    
    # Set up agent assignments
    tracker.assign_tools_to_agent("analysis-agent", ["data_analyzer", "file_processor"])
    tracker.assign_tools_to_agent("coding-agent", ["code_generator", "file_processor"])
    tracker.assign_tools_to_agent("general-agent", ["data_analyzer", "code_generator"])
    
    # Record some usage
    tracker.record_tool_usage("analysis-agent", "data_analyzer")
    tracker.record_tool_usage("analysis-agent", "data_analyzer")
    tracker.record_tool_usage("coding-agent", "code_generator")
    tracker.record_tool_usage("general-agent", "data_analyzer")
    
    print("✅ Demo environment set up!")
    return registry, tracker


def demo_cli_commands():
    """Demonstrate CLI commands."""
    print("\n🧪 Demonstrating CLI Commands...")
    
    # Set up environment
    registry, tracker = setup_demo_environment()
    
    print("\n1. 'tools list' command:")
    print("   " + "="*50)
    tools_list()
    
    print("\n2. 'tools tracker' command:")
    print("   " + "="*50)
    tools_tracker()
    
    print("\n3. 'tools agent analysis-agent' command:")
    print("   " + "="*50)
    tools_agent("analysis-agent")
    
    print("\n4. 'tools stats' command:")
    print("   " + "="*50)
    tools_stats()
    
    print("\n5. Testing tool assignment:")
    print("   " + "="*50)
    # Assign tools to a new agent
    tracker.assign_tools_to_agent("new-agent", ["data_analyzer", "code_generator"])
    print("   Assigned data_analyzer and code_generator to new-agent")
    
    # Show the new agent's tools
    tools_agent("new-agent")
    
    print("\n6. Testing tool removal:")
    print("   " + "="*50)
    tracker.remove_agent_tools("new-agent")
    print("   Removed all tools from new-agent")
    
    # Show the agent's tools (should be empty)
    tools_agent("new-agent")


def main():
    """Main function."""
    print("🚀 CLI Demo for Step 1 Components")
    print("=" * 50)
    
    # Demonstrate CLI commands
    demo_cli_commands()
    
    print("\n✅ CLI demo completed!")
    print("\nThis demonstrates that all CLI commands work correctly with the tool system.")


if __name__ == "__main__":
    main()

