"""Test Step 1: Modular Core Architecture and Tool System.

This module tests the foundational components implemented in Step 1.
"""

import pytest
from datetime import datetime
from agentmanager.core.tools import (
    tool, register_tool, ToolMetadata, get_global_registry, 
    get_agent_tools_tracker, AgentToolsTracker, AgentToolAssignment
)


class TestToolDecoratorSystem:
    """Test the @tool decorator system."""
    
    def test_tool_decorator_basic(self):
        """Test basic @tool decorator functionality."""
        @tool(name="test_tool", description="A test tool")
        def test_function(x: int, y: str = "default") -> str:
            """Test function with parameters."""
            return f"{x}: {y}"
        
        # Check metadata was attached
        assert hasattr(test_function, '__tool_metadata__')
        metadata = getattr(test_function, '__tool_metadata__')
        
        assert metadata.name == "test_tool"
        assert metadata.description == "A test tool"
        assert metadata.parameters['x']['annotation'] == "<class 'int'>"
        assert metadata.parameters['y']['annotation'] == "<class 'str'>"
        assert metadata.parameters['y']['default'] == "default"
        assert metadata.return_type == str
        assert not metadata.is_async
    
    def test_tool_decorator_auto_register(self):
        """Test @tool decorator with auto-registration."""
        @tool(name="auto_tool", description="Auto-registered tool")
        def auto_function(data: str) -> dict:
            return {"result": data}
        
        # Check it was registered in global registry
        registry = get_global_registry()
        metadata = registry.get_tool("auto_tool")
        
        assert metadata is not None
        assert metadata.name == "auto_tool"
        assert metadata.description == "Auto-registered tool"
    
    def test_register_tool_decorator(self):
        """Test @register_tool decorator."""
        @register_tool
        def registered_function(value: int) -> int:
            """A registered function."""
            return value * 2
        
        # Check metadata was attached
        assert hasattr(registered_function, '__tool_metadata__')
        metadata = getattr(registered_function, '__tool_metadata__')
        
        assert metadata.name == "registered_function"
        assert metadata.description == "A registered function."


class TestToolRegistry:
    """Test the tool registry system."""
    
    def test_tool_registration(self):
        """Test tool registration and retrieval."""
        registry = get_global_registry()
        
        @tool(name="registry_test", description="Registry test tool")
        def registry_test_func(x: int) -> int:
            return x + 1
        
        # Check tool is registered
        metadata = registry.get_tool("registry_test")
        assert metadata is not None
        assert metadata.name == "registry_test"
        
        # Check function retrieval
        func = registry.get_function("registry_test")
        assert func is not None
        assert func(5) == 6
    
    def test_tool_execution(self):
        """Test tool execution through registry."""
        registry = get_global_registry()
        
        @tool(name="exec_test", description="Execution test tool")
        def exec_test_func(a: int, b: int) -> int:
            return a + b
        
        # Test execution
        result = registry.execute_tool("exec_test", a=3, b=4)
        assert result == 7
    
    def test_tool_listing(self):
        """Test tool listing functionality."""
        registry = get_global_registry()
        
        # Clear registry for clean test
        registry.clear()
        
        @tool(name="list_test_1", description="List test 1")
        def list_test_1():
            pass
        
        @tool(name="list_test_2", description="List test 2")
        def list_test_2():
            pass
        
        # Check listing
        tools = registry.list_tools()
        assert "list_test_1" in tools
        assert "list_test_2" in tools
        assert len(tools) >= 2


class TestAgentToolsTracker:
    """Test the agent-tools tracker system."""
    
    def test_agent_tool_assignment(self):
        """Test assigning tools to agents."""
        tracker = get_agent_tools_tracker()
        
        # Create some test tools first
        registry = get_global_registry()
        
        @tool(name="tracker_tool_1", description="Tracker test tool 1")
        def tracker_tool_1(x: int) -> int:
            return x * 2
        
        @tool(name="tracker_tool_2", description="Tracker test tool 2")
        def tracker_tool_2(y: str) -> str:
            return f"processed: {y}"
        
        # Test assignment
        tracker.assign_tools_to_agent("test_agent", ["tracker_tool_1", "tracker_tool_2"])
        
        # Check assignment
        tools = tracker.get_agent_tools("test_agent")
        assert "tracker_tool_1" in tools
        assert "tracker_tool_2" in tools
        assert len(tools) == 2
    
    def test_bidirectional_lookup(self):
        """Test bidirectional lookup (agent -> tools, tool -> agents)."""
        tracker = get_agent_tools_tracker()
        
        # Create test tools
        @tool(name="bidirectional_tool", description="Bidirectional test tool")
        def bidirectional_tool():
            pass
        
        # Assign tool to multiple agents
        tracker.assign_tools_to_agent("agent_1", ["bidirectional_tool"])
        tracker.assign_tools_to_agent("agent_2", ["bidirectional_tool"])
        
        # Test agent -> tools lookup
        agent_1_tools = tracker.get_agent_tools("agent_1")
        assert "bidirectional_tool" in agent_1_tools
        
        # Test tool -> agents lookup
        agents_with_tool = tracker.get_agents_with_tool("bidirectional_tool")
        assert "agent_1" in agents_with_tool
        assert "agent_2" in agents_with_tool
        assert len(agents_with_tool) == 2
    
    def test_tool_assignment_validation(self):
        """Test that tool assignment validates against global registry."""
        tracker = get_agent_tools_tracker()
        
        # Try to assign non-existent tool
        with pytest.raises(ValueError, match="Tool 'non_existent_tool' not found"):
            tracker.assign_tools_to_agent("test_agent", ["non_existent_tool"])
    
    def test_usage_tracking(self):
        """Test usage tracking functionality."""
        tracker = get_agent_tools_tracker()
        
        # Clear existing assignments for clean test
        if "usage_agent" in tracker._agent_assignments:
            tracker.remove_agent_tools("usage_agent")
        
        # Clear usage stats
        tracker._usage_stats.clear()
        
        # Create test tool
        @tool(name="usage_tool", description="Usage tracking test tool")
        def usage_tool():
            pass
        
        # Assign tool to agent
        tracker.assign_tools_to_agent("usage_agent", ["usage_tool"])
        
        # Record usage
        tracker.record_tool_usage("usage_agent", "usage_tool")
        tracker.record_tool_usage("usage_agent", "usage_tool")
        
        # Check usage stats
        assignment = tracker.get_assignment_info("usage_agent")
        assert assignment.usage_count == 2
        assert assignment.last_used is not None
        
        tool_stats = tracker.get_tool_usage_stats()
        assert tool_stats["usage_tool"] == 2
    
    def test_agent_removal(self):
        """Test removing tools from an agent."""
        tracker = get_agent_tools_tracker()
        
        # Create test tool
        @tool(name="removal_tool", description="Removal test tool")
        def removal_tool():
            pass
        
        # Assign tool to agent
        tracker.assign_tools_to_agent("removal_agent", ["removal_tool"])
        
        # Verify assignment exists
        tools = tracker.get_agent_tools("removal_agent")
        assert "removal_tool" in tools
        
        # Remove tools
        tracker.remove_agent_tools("removal_agent")
        
        # Verify removal
        tools = tracker.get_agent_tools("removal_agent")
        assert len(tools) == 0
        
        # Verify tool-to-agents mapping is updated
        agents_with_tool = tracker.get_agents_with_tool("removal_tool")
        assert "removal_agent" not in agents_with_tool
    
    def test_tracker_status(self):
        """Test tracker status reporting."""
        tracker = get_agent_tools_tracker()
        
        # Clear all existing assignments for clean test
        for agent_name in list(tracker._agent_assignments.keys()):
            tracker.remove_agent_tools(agent_name)
        
        # Create test tools and assignments
        @tool(name="status_tool_1", description="Status test tool 1")
        def status_tool_1():
            pass
        
        @tool(name="status_tool_2", description="Status test tool 2")
        def status_tool_2():
            pass
        
        tracker.assign_tools_to_agent("status_agent_1", ["status_tool_1"])
        tracker.assign_tools_to_agent("status_agent_2", ["status_tool_1", "status_tool_2"])
        
        # Get status
        status = tracker.get_tracker_status()
        
        assert status["total_agents"] == 2
        assert status["active_agents"] == 2
        assert status["total_tools"] == 2
        assert status["total_assignments"] == 3  # 1 + 2


class TestIntegration:
    """Test integration between components."""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from tool definition to agent usage."""
        # Step 1: Define tools
        @tool(name="workflow_tool", description="End-to-end workflow test tool")
        def workflow_tool(data: str, multiplier: int = 2) -> str:
            return f"{data} * {multiplier} = {data * multiplier}"
        
        # Step 2: Verify tool is registered
        registry = get_global_registry()
        metadata = registry.get_tool("workflow_tool")
        assert metadata is not None
        
        # Step 3: Assign tool to agent
        tracker = get_agent_tools_tracker()
        tracker.assign_tools_to_agent("workflow_agent", ["workflow_tool"])
        
        # Step 4: Verify assignment
        agent_tools = tracker.get_agent_tools("workflow_agent")
        assert "workflow_tool" in agent_tools
        
        # Step 5: Simulate agent using tool
        result = registry.execute_tool("workflow_tool", data="test", multiplier=3)
        assert result == "test * 3 = testtesttest"
        
        # Step 6: Record usage
        tracker.record_tool_usage("workflow_agent", "workflow_tool")
        
        # Step 7: Verify usage tracking
        assignment = tracker.get_assignment_info("workflow_agent")
        assert assignment.usage_count == 1


if __name__ == "__main__":
    pytest.main([__file__])
