"""Pytest configuration for Phase 2.5 tool injection tests."""

import asyncio
from unittest.mock import MagicMock

import pytest

from agenthub.core.tools.registry import ToolRegistry


@pytest.fixture(autouse=True)
def reset_tool_registry():
    """Reset the tool registry before each test."""
    ToolRegistry._instance = None
    yield
    # Cleanup after test
    if ToolRegistry._instance:
        # Clear registered tools and agent assignments
        ToolRegistry._instance.registered_tools.clear()
        ToolRegistry._instance.agent_tool_access.clear()


@pytest.fixture
def tool_registry():
    """Provide a clean tool registry instance."""
    return ToolRegistry()


@pytest.fixture
def mock_agent_info():
    """Provide mock agent information."""
    return {
        "name": "test_agent",
        "path": "/path/to/agent",
        "manifest": {
            "name": "test_agent",
            "description": "Test agent",
            "version": "1.0.0",
            "entry_point": "agent.py",
            "methods": ["run", "analyze", "process"],
        },
    }


@pytest.fixture
def sample_tools(tool_registry):
    """Register sample tools for testing."""
    from agenthub.core.tools.decorator import tool

    @tool(name="sample_tool1", description="Sample tool 1")
    def sample_tool1(param: str) -> str:
        return f"result: {param}"

    @tool(name="sample_tool2", description="Sample tool 2")
    def sample_tool2(param: int) -> int:
        return param * 2

    @tool(name="sample_tool3", description="Sample tool 3")
    def sample_tool3(param1: str, param2: int = 10) -> dict:
        return {"param1": param1, "param2": param2}

    return ["sample_tool1", "sample_tool2", "sample_tool3"]


@pytest.fixture
def mock_mcp_client():
    """Provide a mock MCP client."""
    mock_client = MagicMock()
    mock_client.is_connected = True
    mock_client.connect = MagicMock(return_value=asyncio.coroutine(lambda: None)())
    mock_client.disconnect = MagicMock(return_value=asyncio.coroutine(lambda: None)())
    mock_client.list_tools = MagicMock(return_value=asyncio.coroutine(lambda: [])())
    mock_client.call_tool = MagicMock(
        return_value=asyncio.coroutine(lambda: "result")()
    )
    return mock_client


@pytest.fixture
def mock_agent_loader():
    """Provide a mock agent loader."""
    mock_loader = MagicMock()
    mock_loader.load_agent.return_value = {
        "name": "test_agent",
        "path": "/path/to/agent",
        "manifest": {
            "name": "test_agent",
            "description": "Test agent",
            "version": "1.0.0",
            "entry_point": "agent.py",
            "methods": ["run", "analyze", "process"],
        },
    }
    return mock_loader


@pytest.fixture
def mock_agent_wrapper():
    """Provide a mock agent wrapper."""
    mock_wrapper = MagicMock()
    mock_wrapper.assigned_tools = []
    mock_wrapper.assign_tools = MagicMock()
    mock_wrapper.execute_tool = MagicMock(return_value="result")
    mock_wrapper.get_available_tools = MagicMock(return_value=[])
    mock_wrapper.get_tool_metadata = MagicMock(return_value=None)
    mock_wrapper.get_tool_context_json = MagicMock(
        return_value='{"available_tools": []}'
    )
    mock_wrapper.generate_agent_call_json = MagicMock(
        return_value='{"method": "run", "parameters": {}}'
    )
    return mock_wrapper


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def performance_thresholds():
    """Provide performance thresholds for tests."""
    return {
        "tool_registration_time": 5.0,  # seconds
        "tool_execution_time": 1.0,  # seconds
        "metadata_retrieval_time": 0.5,  # seconds
        "concurrent_registration_time": 2.0,  # seconds
        "concurrent_execution_time": 2.0,  # seconds
        "memory_increase_mb": 50,  # MB
        "lookup_time": 1.0,  # seconds
        "assignment_time": 1.0,  # seconds
        "context_generation_time": 2.0,  # seconds
        "cleanup_time": 0.5,  # seconds
    }


@pytest.fixture
def test_data():
    """Provide test data for various scenarios."""
    return {
        "simple_tools": [
            {"name": "add", "description": "Add two numbers", "params": ["a", "b"]},
            {
                "name": "multiply",
                "description": "Multiply two numbers",
                "params": ["a", "b"],
            },
            {"name": "greet", "description": "Generate greeting", "params": ["name"]},
        ],
        "complex_tools": [
            {
                "name": "data_analyzer",
                "description": "Analyze data",
                "params": ["data", "analysis_type"],
            },
            {
                "name": "file_processor",
                "description": "Process files",
                "params": ["file_path", "operation"],
            },
            {
                "name": "web_search",
                "description": "Search the web",
                "params": ["query", "max_results"],
            },
        ],
        "agent_configs": [
            {"name": "analysis_agent", "tools": ["data_analyzer", "file_processor"]},
            {"name": "math_agent", "tools": ["add", "multiply"]},
            {"name": "greeting_agent", "tools": ["greet"]},
        ],
    }


# Pytest markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "mcp: Tests requiring MCP server")
    config.addinivalue_line("markers", "concurrent: Concurrent execution tests")


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add markers based on test class/module names
        if "performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        if "concurrent" in item.nodeid or "concurrent" in item.name:
            item.add_marker(pytest.mark.concurrent)
        if "mcp" in item.nodeid or "mcp" in item.name:
            item.add_marker(pytest.mark.mcp)
        if "slow" in item.name or "benchmark" in item.name:
            item.add_marker(pytest.mark.slow)
