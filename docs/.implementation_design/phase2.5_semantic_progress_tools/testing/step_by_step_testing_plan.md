# Step-by-Step Testing Plan - Phase 2.5 Tool Injection

**Document Type**: Testing Plan  
**Module**: testing  
**Phase**: 2.5  
**Status**: Draft  

## 🎯 **Purpose**

This document outlines the specific testing requirements for each implementation step in Phase 2.5, ensuring that each step is properly validated before proceeding to the next.

## 📋 **Implementation Steps & Testing Requirements**

### **Step 1: Core Tools Foundation**
**Goal**: Create basic tool registry and `@tool` decorator

#### **What to Implement**:
- `ToolRegistry` singleton class
- `@tool` decorator for user functions
- FastMCP server integration
- Built-in tools (web_search, data_analyzer)

#### **Success Criteria - What Must Be Tested**:

✅ **Tool Registration Test**:
```python
# test_step1_tool_registration.py
from agentmanager.core.tools import tool, get_available_tools, get_mcp_server

@tool(name="test_tool", description="Test tool")
def test_function(data: str) -> dict:
    return {"result": data}

# Test 1: Tool is registered
assert "test_tool" in get_available_tools()

# Test 2: MCP server exists and has tools
mcp_server = get_mcp_server()
assert mcp_server is not None
assert mcp_server.name == "AgentHub Tools"
assert len(mcp_server._tool_manager._tools) >= 1  # At least our test tool

# Test 3: Custom tools work correctly
result = test_function("test data")
assert result == {"result": "test data"}
```

✅ **MCP Server Integration Test**:
```python
# test_step1_mcp_integration.py
from agentmanager.core.tools import get_mcp_server, web_search

# Test 1: MCP server is properly initialized
mcp_server = get_mcp_server()
assert mcp_server is not None
assert hasattr(mcp_server, '_tools')

# Test 2: Tools are registered with FastMCP
assert len(mcp_server._tools) >= 2  # web_search + data_analyzer

# Test 3: Built-in tools work
result = web_search("Python programming", max_results=3)
assert isinstance(result, dict)
assert "query" in result
assert "results" in result
```

**Gate**: User can register custom tools and they are available via MCP server.

---

### **Step 2: MCP Server Integration**
**Goal**: Add MCP server management and tool execution via MCP

#### **What to Implement**:
- `AgentToolManager` class
- Tool assignment to agents
- MCP client for tool execution
- Tool execution via FastMCP

#### **Success Criteria - What Must Be Tested**:

✅ **Tool Assignment Test**:
```python
# test_step2_tool_assignment.py
from agentmanager.core.mcp import get_tool_manager
from agentmanager.core.tools import tool

@tool(name="assignment_test_tool", description="Assignment test")
def assignment_tool(data: str) -> dict:
    return {"assigned": True, "data": data}

async def test_tool_assignment():
    manager = get_tool_manager()
    
    # Test 1: Tool assignment works
    assigned = manager.assign_tools_to_agent("agent_1", ["assignment_test_tool", "web_search"])
    assert "assignment_test_tool" in assigned
    assert "web_search" in assigned
    
    # Test 2: Agent tools are tracked
    agent_tools = manager.get_agent_tools("agent_1")
    assert "assignment_test_tool" in agent_tools
    assert "web_search" in agent_tools
```

✅ **MCP Tool Execution Test**:
```python
# test_step2_mcp_execution.py
import asyncio
from agentmanager.core.mcp import get_tool_manager

async def test_mcp_execution():
    manager = get_tool_manager()
    
    # Test 1: Tool execution via MCP client
    result = await manager.execute_tool("web_search", {"query": "AI trends", "max_results": 2})
    assert isinstance(result, str)  # JSON string from MCP
    assert "query" in result or "results" in result
    
    # Test 2: MCP client is created
    assert manager.client is not None
    
    # Test 3: Tool execution is routed through MCP
    # (Verify it's not just calling the function directly)
```

**Gate**: Tools can be assigned to agents and executed via MCP client, not direct function calls.

---

### **Step 3: Runtime Tool Injection**
**Goal**: Inject tool metadata into agent context

#### **What to Implement**:
- `ToolInjector` class
- Tool context generation
- Agent tool assignment
- Tool metadata injection

#### **Success Criteria - What Must Be Tested**:

✅ **Tool Context Injection Test**:
```python
# test_step3_tool_injection.py
from agentmanager.runtime import get_tool_injector
from agentmanager.core.tools import tool

@tool(name="injection_test_tool", description="Injection test")
def injection_tool(data: str) -> dict:
    return {"injected": True, "data": data}

def test_tool_injection():
    injector = get_tool_injector()
    
    # Test 1: Tool injection creates proper metadata
    metadata = injector.inject_tools_into_agent_context("agent_1", ["injection_test_tool", "web_search"])
    
    assert "available_tools" in metadata
    assert "injection_test_tool" in metadata["available_tools"]
    assert "web_search" in metadata["available_tools"]
    
    # Test 2: Tool descriptions are included
    assert "tool_descriptions" in metadata
    assert "injection_test_tool" in metadata["tool_descriptions"]
    
    # Test 3: Usage examples are provided
    assert "tool_usage_examples" in metadata
    assert "injection_test_tool" in metadata["tool_usage_examples"]
```

✅ **Agent Tool Assignment Test**:
```python
# test_step3_agent_assignment.py
from agentmanager.runtime import get_tool_injector

def test_agent_tool_assignment():
    injector = get_tool_injector()
    
    # Test 1: Agent gets tools assigned in tool manager
    injector.inject_tools_into_agent_context("agent_1", ["web_search", "data_analyzer"])
    
    # Check that agent has tools in the tool manager
    agent_tools = injector.tool_manager.get_agent_tools("agent_1")
    assert "web_search" in agent_tools
    assert "data_analyzer" in agent_tools
    
    # Test 2: Invalid tools are filtered out
    metadata = injector.inject_tools_into_agent_context("agent_2", ["nonexistent_tool"])
    assert "nonexistent_tool" not in metadata["available_tools"]
```

**Gate**: Tool metadata is properly injected into agent context and tools are assigned to agents.

---

### **Step 4: Enhanced Agent with Tool Capabilities**
**Goal**: Create EnhancedAgent class with tool access methods

#### **What to Implement**:
- `EnhancedAgent` class
- Tool discovery methods
- Tool execution methods
- Agent-tool integration

#### **Success Criteria - What Must Be Tested**:

✅ **Agent Tool Discovery Test**:
```python
# test_step4_agent_tool_discovery.py
import asyncio
import agentmanager as amg
from agentmanager.core.tools import tool

@tool(name="discovery_test_tool", description="Discovery test")
def discovery_tool(data: str) -> dict:
    return {"discovered": True, "data": data}

async def test_agent_tool_discovery():
    # Test 1: Load agent with tools
    agent = amg.load_agent(
        base_agent="agentplug/analysis-agent",
        tools=["discovery_test_tool", "web_search"]
    )
    
    # Test 2: Agent can discover tools
    assert agent.has_tool("discovery_test_tool") == True
    assert agent.has_tool("web_search") == True
    assert agent.has_tool("nonexistent_tool") == False
    
    # Test 3: Agent lists available tools
    available_tools = agent.get_available_tools()
    assert "discovery_test_tool" in available_tools
    assert "web_search" in available_tools
```

✅ **Agent Tool Execution Test**:
```python
# test_step4_agent_tool_execution.py
import asyncio
import agentmanager as amg

async def test_agent_tool_execution():
    agent = amg.load_agent(
        base_agent="agentplug/analysis-agent",
        tools=["web_search", "data_analyzer"]
    )
    
    # Test 1: Agent can execute tools
    result = await agent.execute_tool("web_search", {"query": "test query", "max_results": 2})
    assert isinstance(result, str)  # JSON string from MCP
    
    # Test 2: Access control works
    try:
        await agent.execute_tool("unauthorized_tool", {"data": "test"})
        assert False, "Should have raised access denied error"
    except ValueError as e:
        assert "access" in str(e).lower() or "denied" in str(e).lower()
```

**Gate**: Agent can discover and execute assigned tools, with proper access control.

---

### **Step 5: Complete SDK Integration**
**Goal**: Full `amg.load_agent(tools=[...])` functionality

#### **What to Implement**:
- Complete SDK integration
- User-facing API
- End-to-end workflow

#### **Success Criteria - What Must Be Tested**:

✅ **Complete User API Test**:
```python
# test_step5_complete_api.py
import asyncio
import agentmanager as amg
from agentmanager.core.tools import tool

@tool(name="user_custom_tool", description="User custom tool")
def user_custom_tool(data: str) -> dict:
    return {"custom": True, "data": data}

async def test_complete_user_api():
    # Test 1: Complete user API works
    agent = amg.load_agent(
        base_agent="agentplug/analysis-agent",
        tools=["user_custom_tool", "web_search", "data_analyzer"]
    )
    
    # Test 2: All tools are available
    assert agent.has_tool("user_custom_tool")
    assert agent.has_tool("web_search")
    assert agent.has_tool("data_analyzer")
    
    # Test 3: Tools can be executed
    result1 = await agent.execute_tool("user_custom_tool", {"data": "test"})
    result2 = await agent.execute_tool("web_search", {"query": "test", "max_results": 1})
    
    assert isinstance(result1, str)
    assert isinstance(result2, str)
```

✅ **End-to-End Workflow Test**:
```python
# test_step5_end_to_end.py
import asyncio
import agentmanager as amg

async def test_end_to_end_workflow():
    # Test complete workflow: register tools -> load agent -> use tools
    agent = amg.load_agent(
        base_agent="agentplug/analysis-agent",
        tools=["web_search", "data_analyzer"]
    )
    
    # Test that the complete workflow works
    # 1. Tools are registered globally
    # 2. Agent gets assigned tools
    # 3. Agent can use tools
    # 4. Tool execution goes through MCP
    # 5. Results are returned properly
    
    assert len(agent.get_available_tools()) >= 2
    result = await agent.execute_tool("web_search", {"query": "test"})
    assert result is not None
```

**Gate**: Complete user API works end-to-end with tool registration, assignment, and execution.

---

### **Step 6: Error Handling & Validation**
**Goal**: Add comprehensive error handling and validation

#### **What to Implement**:
- Custom exceptions
- Error handling
- Input validation
- Graceful degradation

#### **Success Criteria - What Must Be Tested**:

✅ **Error Handling Test**:
```python
# test_step6_error_handling.py
import asyncio
import agentmanager as amg
from agentmanager.core.tools import tool
from agentmanager.core.tools.exceptions import ToolNameConflictError, ToolAccessDeniedError

# Test 1: Duplicate tool registration error
try:
    @tool(name="duplicate_tool", description="First")
    def tool1(data: str) -> dict:
        return {"result": data}
    
    @tool(name="duplicate_tool", description="Second")
    def tool2(data: str) -> dict:
        return {"result": data}
    
    assert False, "Should have raised ToolNameConflictError"
except ToolNameConflictError:
    pass  # Expected

# Test 2: Tool access denied error
async def test_access_denied():
    agent = amg.load_agent("test_agent", tools=["web_search"])
    
    try:
        await agent.execute_tool("unauthorized_tool", {"data": "test"})
        assert False, "Should have raised access denied error"
    except (ValueError, ToolAccessDeniedError) as e:
        assert "access" in str(e).lower() or "denied" in str(e).lower()
```

**Gate**: All error scenarios are properly handled with appropriate exceptions.

---

### **Step 7: Performance & Concurrency**
**Goal**: Add performance optimizations and concurrency support

#### **What to Implement**:
- Concurrent tool execution
- Performance optimizations
- Thread safety
- Scalability improvements

#### **Success Criteria - What Must Be Tested**:

✅ **Concurrency Test**:
```python
# test_step7_concurrency.py
import asyncio
import time
import agentmanager as amg

async def test_concurrent_tool_execution():
    agent = amg.load_agent("test_agent", tools=["web_search", "data_analyzer"])
    
    # Test 1: Concurrent tool execution
    start_time = time.time()
    
    tasks = [
        agent.execute_tool("web_search", {"query": f"query_{i}", "max_results": 1})
        for i in range(5)
    ]
    
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    # Test 2: All executions completed
    assert len(results) == 5
    assert all(isinstance(result, str) for result in results)
    
    # Test 3: Concurrent execution is faster than sequential
    # (This is a basic test - in practice, network calls might not show much difference)
    execution_time = end_time - start_time
    assert execution_time < 10.0  # Should complete within 10 seconds
```

**Gate**: System handles concurrent tool execution efficiently and safely.

---

## 🎯 **Final Gate - Complete User Experience**

### **End-to-End Integration Test**:
```python
# final_integration_test.py
import asyncio
import agentmanager as amg
from agentmanager.core.tools import tool

# User defines custom tools
@tool(name="market_analysis", description="Analyze market trends")
def market_analysis(topic: str) -> dict:
    return {"trends": f"Market analysis for {topic}", "growth": "5.2%"}

@tool(name="sentiment_analyzer", description="Advanced sentiment analysis")
def sentiment_analyzer(text: str) -> dict:
    return {"sentiment": "positive", "confidence": 0.95}

async def test_complete_user_experience():
    # Test the complete user experience
    agent = amg.load_agent(
        base_agent="agentplug/analysis-agent",
        tools=["market_analysis", "sentiment_analyzer", "web_search", "data_analyzer"]
    )
    
    # Test 1: All tools are available
    available_tools = agent.get_available_tools()
    expected_tools = ["market_analysis", "sentiment_analyzer", "web_search", "data_analyzer"]
    for tool_name in expected_tools:
        assert tool_name in available_tools
    
    # Test 2: Tools can be executed
    results = []
    for tool_name in expected_tools:
        if tool_name == "web_search":
            result = await agent.execute_tool(tool_name, {"query": "test", "max_results": 1})
        elif tool_name == "data_analyzer":
            result = await agent.execute_tool(tool_name, {"data": "test data"})
        else:
            result = await agent.execute_tool(tool_name, {"text": "test"})
        
        results.append(result)
        assert isinstance(result, str)  # JSON string from MCP
    
    # Test 3: All executions succeeded
    assert len(results) == len(expected_tools)
    assert all(result is not None for result in results)

asyncio.run(test_complete_user_experience())
```

## 📊 **Testing Metrics & Success Criteria**

### **Per-Step Success Criteria**:
- ✅ **Step 1**: Tool registration and MCP server integration works
- ✅ **Step 2**: Tool assignment and MCP execution works
- ✅ **Step 3**: Tool injection and context management works
- ✅ **Step 4**: Agent tool discovery and execution works
- ✅ **Step 5**: Complete SDK integration works
- ✅ **Step 6**: Error handling and validation works
- ✅ **Step 7**: Concurrency and performance works

### **Overall Success Criteria**:
- ✅ All tests pass for each step
- ✅ No regressions in existing functionality
- ✅ Performance meets baseline requirements
- ✅ Error handling is comprehensive
- ✅ User experience is smooth and intuitive
- ✅ Documentation is complete and accurate

## 🚀 **Test Execution Strategy**

### **Step-by-Step Testing**:
1. **Implement Step 1** → Run Step 1 tests → Verify success criteria
2. **Implement Step 2** → Run Step 1 + Step 2 tests → Verify success criteria
3. **Continue for each step** → Ensure no regressions
4. **Final integration test** → Verify complete user experience

### **Continuous Testing**:
- Run tests after each implementation step
- Fix any failing tests before proceeding
- Maintain test coverage above 90%
- Ensure all tests pass in CI/CD pipeline

This step-by-step testing plan ensures that each implementation step is thoroughly validated before proceeding to the next, maintaining code quality and system reliability throughout the development process.
