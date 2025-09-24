# MCP Tool Execution Call Chain in AgentHub

## **Overview**

This document captures the complete function call chain for how an agent uses an MCP tool in agentHub, based on analysis of the actual codebase.

## **Complete Function Call Flow**

### **1. User Code (Entry Point)**
```python
# User loads agent with tools
agent = load_agent("analysis-agent", external_tools=["document_retrieval"])
result = agent.analyze_text("Find documents about AI trends")
```

### **2. AgentHub SDK Level**
```python
# agenthub/sdk/load_agent.py
def load_agent(base_agent: str, external_tools: list = None):
    # Creates AgentWrapper with tool context
    agent = AgentWrapper(agent_info, tool_registry=get_tool_registry())
    
    # Assigns external tools to agent
    if external_tools:
        agent.add_external_tools(external_tools)
```

### **3. AgentWrapper Level**
```python
# agenthub/core/agents/wrapper.py
def add_external_tools(self, tool_names: list):
    # Adds tools to agent's available tools
    # Creates tool context with descriptions and examples
    tool_context = {
        "available_tools": tool_names,
        "tool_descriptions": {...},
        "tool_usage_examples": {...}
    }
```

### **4. Agent Execution (agent.py main function)**
```python
# C:\Users\Andrea Vu\.agenthub\agents\agentplug\analysis-agent\agent.py
def main():
    # Parse input from command line
    input_data = json.loads(sys.argv[1])
    method = input_data.get("method")
    parameters = input_data.get("parameters", {})
    tool_context = input_data.get("tool_context", {})  # ← Tool context passed here
    
    # Create agent instance with tool context
    agent = ModularAnalysisAgent(tool_context=tool_context)
    
    # Execute method (e.g., analyze_text)
    if method == "analyze_text":
        result = agent.analyze_text(parameters.get("text", ""))
```

### **5. Agent Method Execution**
```python
# agent.py - analyze_text method
def analyze_text(self, text: str, analysis_type: str = "general"):
    # Build system prompt with tool context
    system_prompt = self._build_system_prompt(analysis_type)
    
    # Send to AI with tool context
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Analyze this text:\n{text}"}
    ]
    
    # AI generates response (may include tool calls)
    response_text = self.ai_client.generate_response_with_messages(messages)
    
    # Process AI response for tool calls
    result = self._process_ai_response(response_text, analysis_type)
```

### **6. Tool Call Detection & Processing**
```python
# agent.py - _process_ai_response method
def _process_ai_response(self, response: str, analysis_type: str):
    # Extract tool calls from AI response
    tool_calls = self.response_parser.extract_tool_calls(response)
    
    if tool_calls:
        # Validate tool calls
        validator = ToolValidator(self.available_tools)
        validation_result = validator.validate_tool_calls_batch(tool_calls)
        
        if validation_result["all_valid"]:
            # Execute tools
            return self.tool_executor.execute_tools_workflow(
                validation_result["valid_calls"], text, analysis_type, 
                self.ai_client.get_raw_client(), messages
            )
```

### **7. Tool Execution (ToolExecutor)**
```python
# agent_modules/execution/tool_executor.py
def execute_tools_workflow(self, tool_calls: List[Dict], text: str, analysis_type: str, client, messages):
    # Multi-step tool execution
    for tool_call in tool_calls:
        tool_result = self.execute_single_tool(tool_call)
        
def execute_single_tool(self, tool_call: Dict[str, Any]):
    tool_name = tool_call["tool_name"]
    arguments = tool_call.get("arguments", {})
    
    # CRITICAL: Validate tool is authorized
    if not self.validator.validate_tool_call(tool_call):
        return {"success": False, "error": "UNAUTHORIZED"}
    
    # Execute via MCP client
    result = self.mcp_client.call_tool(tool_name, arguments)
```

### **8. MCP Client Execution**
```python
# agent_modules/execution/mcp_client.py
def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
    # Handle async execution
    try:
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, self._execute_tool_via_sse(tool_name, arguments))
            return future.result(timeout=30)
    except RuntimeError:
        return asyncio.run(self._execute_tool_via_sse(tool_name, arguments))

async def _execute_tool_via_sse(self, tool_name: str, arguments: Dict[str, Any]):
    # Connect to MCP server
    async with sse_client(url=self.server_url) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            
            # Call the actual tool
            result = await session.call_tool(tool_name, arguments=arguments)
            
            # Extract result content
            if hasattr(result, 'content') and result.content:
                return result.content[0].text
            return str(result)
```

### **9. MCP Server Execution**
```python
# examples/tools/mcp_tool_server.py
@tool(name="document_retrieval", description="...")
def document_retrieval(query: str, operation: str = "search", **kwargs):
    # Actual tool implementation
    return {"results": [...], "status": "success"}
```

### **10. Result Flow Back**
```
MCP Server → MCP Client → ToolExecutor → Agent Method → AgentWrapper → User
```

## **Key Components**

### **Tool Context Structure**
```python
tool_context = {
    "available_tools": ["document_retrieval", "web_search", "add"],
    "tool_descriptions": {
        "document_retrieval": "Search and retrieve documents from local collection",
        "web_search": "Search the web for information",
        "add": "Add two numbers together"
    },
    "tool_usage_examples": {
        "document_retrieval": [
            '{"tool_call": {"tool_name": "document_retrieval", "arguments": {"query": "AI trends"}}}'
        ]
    }
}
```

### **Tool Call Format**
```python
# AI generates tool calls in this JSON format:
{
    "tool_call": {
        "tool_name": "document_retrieval",
        "arguments": {
            "query": "AI trends",
            "operation": "search",
            "limit": 5
        }
    },
    "analysis": "I will search for documents about AI trends"
}
```

### **Tool Validation**
```python
# Each tool call is validated against:
# 1. Tool name is in available_tools list
# 2. Arguments match expected format
# 3. Tool is authorized for this agent
```

## **Key Points**

1. **Tool Context Injection**: Tools are passed as `tool_context` to the agent's `main()` function
2. **AI Integration**: The AI model receives tool descriptions in the system prompt
3. **Tool Call Parsing**: AI responses are parsed to extract tool calls in JSON format
4. **Authorization**: Each tool call is validated against the agent's assigned tools
5. **MCP Protocol**: Tools are executed via MCP server using SSE (Server-Sent Events)
6. **Multi-step Execution**: The system supports multi-step tool workflows
7. **Result Integration**: Tool results are fed back to the AI for final analysis

## **File Locations**

- **Agent Entry Point**: `C:\Users\Andrea Vu\.agenthub\agents\agentplug\analysis-agent\agent.py`
- **Tool Executor**: `C:\Users\Andrea Vu\.agenthub\agents\agentplug\analysis-agent\agent_modules\execution\tool_executor.py`
- **MCP Client**: `C:\Users\Andrea Vu\.agenthub\agents\agentplug\analysis-agent\agent_modules\execution\mcp_client.py`
- **Base Agent**: `C:\Users\Andrea Vu\.agenthub\agents\agentplug\analysis-agent\agent_modules\core\base_agent.py`
- **MCP Tool Server**: `examples/tools/mcp_tool_server.py`

## **Error Handling**

- **Tool Authorization**: Unauthorized tools are rejected with clear error messages
- **MCP Server Unavailable**: Falls back to local execution if configured
- **Tool Execution Failures**: Errors are captured and returned in consistent format
- **Multi-step Failures**: System continues with remaining steps even if some fail

## **Security Considerations**

- **Tool Assignment Limits**: Agents can only use tools explicitly assigned to them
- **Input Validation**: All tool arguments are validated before execution
- **Error Isolation**: Tool execution failures don't crash the entire agent
- **Timeout Protection**: Tool execution has timeout limits to prevent hanging

This call chain represents the **complete, actual** implementation used in agentHub for MCP tool execution.
