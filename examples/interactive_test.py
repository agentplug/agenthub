#!/usr/bin/env python3
"""Interactive Test Script for Step 1 Components.

This script allows you to interactively test the tool system components.
"""

from agentmanager.core.tools import tool, get_global_registry, get_agent_tools_tracker


def test_tool_definition():
    """Test tool definition and registration."""
    print("🔧 Testing Tool Definition...")
    
    @tool(name="calculator", description="Basic calculator operations", tags=["math", "calculation"])
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b
    
    @tool(name="text_processor", description="Process text strings", tags=["text", "processing"])
    def process_text(text: str, operation: str = "uppercase") -> str:
        """Process text with various operations."""
        if operation == "uppercase":
            return text.upper()
        elif operation == "lowercase":
            return text.lower()
        elif operation == "reverse":
            return text[::-1]
        else:
            return text
    
    print("✅ Tools defined!")
    return ["calculator", "text_processor"]


def test_tool_registry(tool_names):
    """Test tool registry functionality."""
    print("\n📋 Testing Tool Registry...")
    
    registry = get_global_registry()
    
    # List all tools
    print(f"   Registered tools: {registry.list_tools()}")
    print(f"   Total tools: {registry.get_tool_count()}")
    
    # Test tool execution
    print("\n   Testing tool execution:")
    try:
        result1 = registry.execute_tool("calculator", a=5, b=3)
        print(f"   calculator(5, 3) = {result1}")
        
        result2 = registry.execute_tool("text_processor", text="Hello World", operation="uppercase")
        print(f"   text_processor('Hello World', 'uppercase') = {result2}")
        
        result3 = registry.execute_tool("text_processor", text="Hello World", operation="reverse")
        print(f"   text_processor('Hello World', 'reverse') = {result3}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    return registry


def test_agent_tools_tracker(tool_names):
    """Test agent-tools tracker functionality."""
    print("\n🎯 Testing Agent-Tools Tracker...")
    
    tracker = get_agent_tools_tracker()
    
    # Assign tools to different agents
    print("   Assigning tools to agents...")
    tracker.assign_tools_to_agent("math_agent", ["calculator"])
    tracker.assign_tools_to_agent("text_agent", ["text_processor"])
    tracker.assign_tools_to_agent("general_agent", ["calculator", "text_processor"])
    
    # Show assignments
    assignments = tracker.get_all_assignments()
    print(f"   Agent assignments: {assignments}")
    
    # Test bidirectional lookup
    print("\n   Bidirectional lookup:")
    print(f"     math_agent tools: {tracker.get_agent_tools('math_agent')}")
    print(f"     text_agent tools: {tracker.get_agent_tools('text_agent')}")
    print(f"     general_agent tools: {tracker.get_agent_tools('general_agent')}")
    
    print(f"     Agents with calculator: {tracker.get_agents_with_tool('calculator')}")
    print(f"     Agents with text_processor: {tracker.get_agents_with_tool('text_processor')}")
    
    # Test usage tracking
    print("\n   Testing usage tracking...")
    tracker.record_tool_usage("math_agent", "calculator")
    tracker.record_tool_usage("math_agent", "calculator")
    tracker.record_tool_usage("text_agent", "text_processor")
    tracker.record_tool_usage("general_agent", "calculator")
    
    # Show usage stats
    tool_stats = tracker.get_tool_usage_stats()
    agent_stats = tracker.get_agent_usage_stats()
    print(f"   Tool usage stats: {tool_stats}")
    print(f"   Agent usage stats: {agent_stats}")
    
    # Show tracker status
    status = tracker.get_tracker_status()
    print(f"\n   Tracker status:")
    print(f"     Total agents: {status['total_agents']}")
    print(f"     Active agents: {status['active_agents']}")
    print(f"     Total tools: {status['total_tools']}")
    print(f"     Total assignments: {status['total_assignments']}")
    
    return tracker


def test_error_handling():
    """Test error handling scenarios."""
    print("\n⚠️  Testing Error Handling...")
    
    tracker = get_agent_tools_tracker()
    
    # Test assigning non-existent tool
    print("   Testing assignment of non-existent tool...")
    try:
        tracker.assign_tools_to_agent("test_agent", ["non_existent_tool"])
        print("   ❌ Should have failed!")
    except ValueError as e:
        print(f"   ✅ Correctly caught error: {e}")
    
    # Test getting tools for non-existent agent
    print("   Testing tools for non-existent agent...")
    tools = tracker.get_agent_tools("non_existent_agent")
    print(f"   ✅ Non-existent agent tools: {tools}")
    
    # Test getting agents for non-existent tool
    print("   Testing agents for non-existent tool...")
    agents = tracker.get_agents_with_tool("non_existent_tool")
    print(f"   ✅ Non-existent tool agents: {agents}")


def main():
    """Main test function."""
    print("🚀 Interactive Test for Step 1 Components")
    print("=" * 50)
    
    # Test tool definition
    tool_names = test_tool_definition()
    
    # Test tool registry
    registry = test_tool_registry(tool_names)
    
    # Test agent-tools tracker
    tracker = test_agent_tools_tracker(tool_names)
    
    # Test error handling
    test_error_handling()
    
    print("\n✅ All tests completed!")
    print("\nNext steps:")
    print("- Try the CLI commands: python -m agentmanager.cli.main tools list")
    print("- Run the full test suite: python -m pytest tests/phase2_5_semantic_tools/test_step1_foundation.py -v")
    print("- Check the demo: python examples/step1_demo.py")


if __name__ == "__main__":
    main()

