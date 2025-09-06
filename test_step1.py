#!/usr/bin/env python3
"""
Step 1 Test: Core Tools Foundation
Tests tool registration, MCP server integration, and built-in tools.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from agentmanager.core.tools import tool, get_available_tools, get_mcp_server, get_tool_metadata
from agentmanager.core.tools import web_search, data_analyzer
from agentmanager.core.tools.exceptions import ToolNameConflictError, ToolValidationError

def test_tool_registration():
    """Test tool registration with @tool decorator."""
    print("=== Testing Tool Registration ===")
    
    @tool(name="test_tool", description="Test tool for Step 1")
    def test_function(data: str) -> dict:
        return {"result": data, "step": 1}
    
    # Test 1: Tool is registered
    available_tools = get_available_tools()
    assert "test_tool" in available_tools, f"test_tool not found in {available_tools}"
    print("✅ Tool registration works")
    
    # Test 2: Tool metadata is correct
    metadata = get_tool_metadata("test_tool")
    assert metadata is not None, "Tool metadata is None"
    assert metadata.name == "test_tool", f"Expected 'test_tool', got '{metadata.name}'"
    assert metadata.description == "Test tool for Step 1", f"Expected 'Test tool for Step 1', got '{metadata.description}'"
    assert metadata.namespace == "custom", f"Expected 'custom', got '{metadata.namespace}'"
    print("✅ Tool metadata is correct")
    
    # Test 3: Tool function works
    result = test_function("test_data")
    assert result == {"result": "test_data", "step": 1}, f"Expected specific result, got {result}"
    print("✅ Tool function execution works")

def test_mcp_server_integration():
    """Test MCP server integration."""
    print("\n=== Testing MCP Server Integration ===")
    
    # Test 1: MCP server exists
    mcp_server = get_mcp_server()
    assert mcp_server is not None, "MCP server is None"
    print("✅ MCP server is created")
    
    # Test 2: MCP server has correct name
    assert mcp_server.name == "AgentHub Tools", f"Expected 'AgentHub Tools', got '{mcp_server.name}'"
    print("✅ MCP server has correct name")
    
    # Test 3: MCP server has tools registered
    assert hasattr(mcp_server, '_tools'), "MCP server doesn't have _tools attribute"
    tool_count = len(mcp_server._tools)
    assert tool_count >= 3, f"Expected at least 3 tools, got {tool_count}"  # test_tool + web_search + data_analyzer
    print(f"✅ MCP server has {tool_count} tools registered")
    
    # Test 4: Our test tool is in MCP server
    tool_names = [tool.__name__ for tool in mcp_server._tools]
    assert "test_tool" in tool_names, f"test_tool not found in MCP server tools: {tool_names}"
    print("✅ Test tool is registered with MCP server")

def test_builtin_tools():
    """Test built-in tools."""
    print("\n=== Testing Built-in Tools ===")
    
    # Test 1: Built-in tools are available
    available_tools = get_available_tools()
    assert "web_search" in available_tools, f"web_search not found in {available_tools}"
    assert "data_analyzer" in available_tools, f"data_analyzer not found in {available_tools}"
    print("✅ Built-in tools are available")
    
    # Test 2: Web search tool works
    search_result = web_search("Python programming", max_results=2)
    assert isinstance(search_result, dict), f"Expected dict, got {type(search_result)}"
    assert "query" in search_result, f"Expected 'query' key, got {list(search_result.keys())}"
    assert search_result["query"] == "Python programming", f"Expected 'Python programming', got '{search_result['query']}'"
    print("✅ Web search tool works")
    
    # Test 3: Data analyzer tool works
    analysis_result = data_analyzer("This is a great product! I love it.")
    assert isinstance(analysis_result, dict), f"Expected dict, got {type(analysis_result)}"
    assert "sentiment" in analysis_result, f"Expected 'sentiment' key, got {list(analysis_result.keys())}"
    assert analysis_result["sentiment"] in ["positive", "negative", "neutral"], f"Expected valid sentiment, got '{analysis_result['sentiment']}'"
    print("✅ Data analyzer tool works")

def test_error_handling():
    """Test error handling."""
    print("\n=== Testing Error Handling ===")
    
    # Test 1: Duplicate tool name
    try:
        @tool(name="test_tool", description="Duplicate tool")
        def duplicate_tool(data: str) -> dict:
            return {"duplicate": True}
        assert False, "Should have raised ToolNameConflictError"
    except ValueError as e:
        assert "already registered" in str(e), f"Expected 'already registered' error, got '{e}'"
        print("✅ Duplicate tool name error handled")
    
    # Test 2: Invalid tool name
    try:
        @tool(name="", description="Empty name tool")
        def empty_name_tool(data: str) -> dict:
            return {"empty": True}
        assert False, "Should have raised ValueError for empty name"
    except ValueError as e:
        assert "non-empty string" in str(e), f"Expected 'non-empty string' error, got '{e}'"
        print("✅ Empty tool name error handled")
    
    # Test 3: Non-callable tool
    try:
        from agentmanager.core.tools import ToolRegistry
        registry = ToolRegistry()
        registry.register_tool("invalid_tool", "not_callable", "Invalid tool")
        assert False, "Should have raised ValueError for non-callable"
    except ValueError as e:
        assert "callable" in str(e), f"Expected 'callable' error, got '{e}'"
        print("✅ Non-callable tool error handled")

def test_tool_metadata():
    """Test tool metadata extraction."""
    print("\n=== Testing Tool Metadata ===")
    
    @tool(name="metadata_test_tool", description="Tool for testing metadata")
    def metadata_tool(text: str, count: int = 5) -> dict:
        """Tool with parameters and return type."""
        return {"text": text, "count": count}
    
    metadata = get_tool_metadata("metadata_test_tool")
    assert metadata is not None, "Metadata is None"
    
    # Test parameters
    assert "text" in metadata.parameters, f"Expected 'text' parameter, got {list(metadata.parameters.keys())}"
    assert "count" in metadata.parameters, f"Expected 'count' parameter, got {list(metadata.parameters.keys())}"
    
    # Test parameter details
    text_param = metadata.parameters["text"]
    assert text_param["required"] == True, f"Expected text to be required, got {text_param['required']}"
    assert text_param["type"] == str, f"Expected str type, got {text_param['type']}"
    
    count_param = metadata.parameters["count"]
    assert count_param["required"] == False, f"Expected count to be optional, got {count_param['required']}"
    assert count_param["default"] == 5, f"Expected default 5, got {count_param['default']}"
    
    # Test examples
    assert len(metadata.examples) > 0, "Expected examples to be generated"
    print("✅ Tool metadata extraction works")

def main():
    """Run all Step 1 tests."""
    print("🚀 Starting Step 1 Tests: Core Tools Foundation\n")
    
    try:
        test_tool_registration()
        test_mcp_server_integration()
        test_builtin_tools()
        test_error_handling()
        test_tool_metadata()
        
        print("\n🎉 All Step 1 tests passed!")
        print("\n✅ Success Criteria Met:")
        print("  - Tool registration works with @tool decorator")
        print("  - MCP server is created and initialized")
        print("  - Built-in tools (web_search, data_analyzer) are available")
        print("  - Tools are registered with FastMCP, not just called directly")
        print("  - Error handling works correctly")
        print("  - Tool metadata extraction works")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
