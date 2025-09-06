#!/usr/bin/env python3
"""Step 1 Test: Core Tools Foundation

This test verifies that Step 1 implementation meets the success criteria:
- Tool registration works with @tool decorator
- MCP server is created and initialized
- Built-in tools (web_search, data_analyzer) are available
- Tools are registered with FastMCP, not just called directly
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentmanager.core.tools import tool, get_available_tools, get_mcp_server, web_search, data_analyzer
from agentmanager.core.tools.exceptions import ToolNameConflictError, ToolValidationError


def test_tool_registration():
    """Test 1: Tool registration works with @tool decorator"""
    print("=== Test 1: Tool Registration ===")
    
    @tool(name="test_tool", description="Test tool")
    def test_function(data: str) -> dict:
        return {"result": data}
    
    # Test that tool is registered
    available_tools = get_available_tools()
    print(f"Available tools: {available_tools}")
    assert "test_tool" in available_tools, "Test tool should be registered"
    print("✅ Tool registration works")
    
    # Test that function still works
    result = test_function("test data")
    assert result == {"result": "test data"}, "Function should still work"
    print("✅ Tool function works correctly")


def test_mcp_server_integration():
    """Test 2: MCP server is created and has tools"""
    print("\n=== Test 2: MCP Server Integration ===")
    
    # Test MCP server exists
    mcp_server = get_mcp_server()
    assert mcp_server is not None, "MCP server should exist"
    print(f"MCP server name: {mcp_server.name}")
    assert mcp_server.name == "AgentHub Tools", "MCP server should have correct name"
    print("✅ MCP server created with correct name")
    
    # Test that tools are registered with FastMCP
    print(f"Tools registered with MCP: {len(mcp_server._tool_manager._tools)}")
    assert len(mcp_server._tool_manager._tools) >= 1, "At least one tool should be registered with MCP"
    print("✅ Tools are registered with FastMCP")


def test_builtin_tools():
    """Test 3: Built-in tools are available"""
    print("\n=== Test 3: Built-in Tools ===")
    
    available_tools = get_available_tools()
    
    # Test web_search tool
    assert "web_search" in available_tools, "web_search should be available"
    print("✅ web_search tool is available")
    
    # Test data_analyzer tool
    assert "data_analyzer" in available_tools, "data_analyzer should be available"
    print("✅ data_analyzer tool is available")
    
    # Test that built-in tools work
    print("\nTesting web_search tool...")
    search_result = web_search("Python programming", max_results=2)
    assert isinstance(search_result, dict), "web_search should return dict"
    assert "query" in search_result, "web_search result should have query"
    print(f"Web search result keys: {list(search_result.keys())}")
    print("✅ web_search tool works")
    
    print("\nTesting data_analyzer tool...")
    analysis_result = data_analyzer("This is a great product! I love it.")
    assert isinstance(analysis_result, dict), "data_analyzer should return dict"
    assert "sentiment" in analysis_result, "data_analyzer result should have sentiment"
    assert analysis_result["sentiment"] == "positive", "Should detect positive sentiment"
    print(f"Data analysis result: {analysis_result}")
    print("✅ data_analyzer tool works")


def test_tool_validation():
    """Test 4: Tool validation works"""
    print("\n=== Test 4: Tool Validation ===")
    
    # Test duplicate tool name
    try:
        @tool(name="test_tool", description="Duplicate tool")
        def duplicate_tool(data: str) -> dict:
            return {"duplicate": True}
        assert False, "Should have raised ToolNameConflictError"
    except ToolNameConflictError as e:
        print(f"✅ Duplicate tool name caught: {e}")
    
    # Test invalid tool (no parameters)
    try:
        @tool(name="invalid_tool", description="Invalid tool")
        def invalid_tool():
            pass
        assert False, "Should have raised ToolValidationError"
    except ToolValidationError as e:
        print(f"✅ Invalid tool caught: {e}")
    
    # Test non-callable tool
    try:
        from agentmanager.core.tools.registry import _registry
        _registry.register_tool("non_callable", "not a function", "Invalid")
        assert False, "Should have raised ToolValidationError"
    except ToolValidationError as e:
        print(f"✅ Non-callable tool caught: {e}")


def test_mcp_tool_registration():
    """Test 5: Tools are registered with FastMCP, not just called directly"""
    print("\n=== Test 5: FastMCP Tool Registration ===")
    
    mcp_server = get_mcp_server()
    available_tools = get_available_tools()
    
    # Check that all registered tools are in MCP server
    for tool_name in available_tools:
        assert tool_name in mcp_server._tool_manager._tools, f"Tool {tool_name} should be in MCP server"
    
    print(f"✅ All {len(available_tools)} tools are registered with FastMCP")
    
    # Verify MCP server has the expected tools
    expected_tools = ["web_search", "data_analyzer"]
    for expected_tool in expected_tools:
        assert expected_tool in mcp_server._tool_manager._tools, f"{expected_tool} should be in MCP server"
    
    print("✅ Built-in tools are properly registered with FastMCP")


def main():
    """Run all Step 1 tests"""
    print("🚀 Starting Step 1 Tests: Core Tools Foundation")
    print("=" * 60)
    
    try:
        test_tool_registration()
        test_mcp_server_integration()
        test_builtin_tools()
        test_tool_validation()
        test_mcp_tool_registration()
        
        print("\n" + "=" * 60)
        print("🎉 ALL STEP 1 TESTS PASSED!")
        print("✅ Tool registration works with @tool decorator")
        print("✅ MCP server is created and initialized")
        print("✅ Built-in tools (web_search, data_analyzer) are available")
        print("✅ Tools are registered with FastMCP, not just called directly")
        print("✅ Tool validation works correctly")
        print("\n🎯 Step 1 Success Criteria: MET")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
