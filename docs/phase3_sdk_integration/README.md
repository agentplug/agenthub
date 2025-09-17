# Phase 3: SDK Integration and Production Polish

**Document Type**: Phase Implementation Design  
**Author**: AgentHub Team  
**Date Created**: 2025-01-27  
**Last Updated**: 2025-01-27  
**Status**: Ready for Implementation  
**Purpose**: Production-ready SDK with user-oriented interface and comprehensive tool management

## 🎯 **Phase 3 Overview**

Phase 3 transforms AgentHub into a production-ready platform with a **user-oriented interface** that makes agent configuration simple and intuitive. The focus is on **polishing the existing functionality** rather than rebuilding, with emphasis on better error handling, clean architecture, and enhanced user experience.

### **Key Innovation: Installation Commands Instead of Dependencies**

Phase 3 replaces the dependencies list in `agent.yaml` with **installation commands** that work with the current UV system. Dependencies are managed in standard Python files (`pyproject.toml` or `requirements.txt`), following industry best practices.

### **Key Philosophy: User-Oriented Design**

- **Users never edit YAML files** - they use simple API parameters
- **Agent developers define capabilities** - they write agent.yaml with tool definitions
- **Framework handles complexity** - loads YAML + applies user configuration

### **Benefits of Installation Commands Approach**

- **Standard Python Packaging**: Dependencies in `pyproject.toml` (industry standard)
- **UV Integration**: Works perfectly with current UV system
- **Flexible Installation**: Support any installation commands needed
- **Better Validation**: Custom validation commands for complex setups
- **Cleaner YAML**: Agent configuration separate from dependency management

## 🚀 **Core Features**

### **1. User-Oriented Agent Loading**
```python
# Simple, intuitive interface for users
agent = amg.load_agent(
    "agentplug/analysis-agent",
    external_tools=['web_search', 'rag'],  # Mapped from current 'tools' parameter
    disabled_builtin_tools=['keyword_extraction'],  # New: disable built-in tools
    knowledge="You are a data analysis expert. Always provide detailed insights."
)

# Backward compatibility - existing code still works
agent = amg.load_agent(
    "agentplug/analysis-agent",
    tools=['web_search', 'rag']  # DEPRECATED: use external_tools instead
)
```

### **2. Enhanced Tool Management**
- **Built-in Tools**: Defined by agent developers in agent.yaml `builtin_tools` section
- **External Tools**: Mapped from current `tools` parameter → `external_tools` parameter
- **Disabled Built-in Tools**: New `disabled_builtin_tools` parameter to disable specific built-in tools
- **Agent-Implemented Tool Management**: Agent developers must implement tool disabling logic
- **Framework Communication**: Framework passes disabled tools to agent via command parameters
- **Tool Conflicts**: Resolved through user choice and developer priorities
- **Tool Validation**: Comprehensive parameter validation and error messages

### **3. Simple Knowledge Injection**
- **Text-based Knowledge**: Users inject knowledge as simple text strings
- **Quick Onboarding**: No complex schemas or categories
- **Agent Context**: Knowledge automatically available to agent's AI

### **4. Production-Ready Error Handling**
- **Specific Error Types**: `AgentLoadError`, `AgentExecutionError`, `ValidationError`
- **Helpful Messages**: Clear guidance and suggestions for fixing issues
- **Graceful Recovery**: Robust error handling and recovery strategies

## 🏗️ **Architecture Design**

### **Separation of Concerns**

| Component | Responsibility | Interface |
|-----------|---------------|-----------|
| **Agent Developer** | Define agent capabilities | agent.yaml with builtin_tools |
| **End User** | Configure agent for their needs | Simple API parameters |
| **Framework** | Handle complexity and integration | Load YAML + apply user config |

### **Enhanced agent.yaml Schema (For Developers)**

```yaml
# agent.yaml - Developer defines agent capabilities
name: "analysis-agent"
version: "1.0.0"
description: "Analyze text content and provide insights"
author: "agentplug"
license: "MIT"
python_version: "3.11+"

# Agent interface (what methods the agent provides)
interface:
  methods:
    analyze_data:
      description: "Analyze data and provide insights"
      parameters:
        data: { type: "string", required: true }
        options: { type: "object", required: false, default: {} }
      returns: { type: "object" }

# Built-in tools (what tools this agent provides)
builtin_tools:
  text_analyzer:
    description: "Analyze text content with various analysis types"
    required: true  # Core functionality - cannot be disabled
    parameters:
      text: { type: "string", required: true }
      analysis_type: { type: "string", enum: ["sentiment", "entities", "keywords"] }
      confidence_threshold: { type: "number", default: 0.8, minimum: 0.0, maximum: 1.0 }
  
  keyword_extraction:
    description: "Extract keywords from text content"
    required: false  # Optional feature - can be disabled
    parameters:
      text: { type: "string", required: true }
      max_keywords: { type: "integer", default: 10, minimum: 1, maximum: 50 }
      language: { type: "string", default: "en", enum: ["en", "es", "fr", "de"] }
  
  sentiment_analysis:
    description: "Analyze sentiment of text content"
    required: false  # Optional feature - can be disabled
    parameters:
      text: { type: "string", required: true }
      model: { type: "string", default: "default", enum: ["default", "advanced", "multilingual"] }

# Installation commands (dependencies in pyproject.toml or requirements.txt)
installation:
  commands:
    - "uv venv .venv"
    - "uv pip install -e ."  # Install from pyproject.toml
    - "uv pip install -r requirements.txt"  # Install additional dependencies
  validation:
    - "python -c 'import nltk; import spacy'"
    - "python -c 'import textblob; import vaderSentiment'"
    - "python -c 'import yake'"

```

### **User-Oriented API (For End Users)**

```python
# agentmanager/sdk/load_agent.py
def load_agent(
    agent_name: str,
    tools: Optional[List[str]] = None,  # DEPRECATED: use external_tools instead
    external_tools: Optional[List[str]] = None,  # Mapped from current 'tools' parameter
    disabled_builtin_tools: Optional[List[str]] = None,  # New: disable built-in tools
    knowledge: Optional[str] = None,  # New: inject knowledge
    **kwargs
):
    """
    Load agent with user-friendly configuration.
    
    Args:
        agent_name: Agent name in format "namespace/agent"
        tools: DEPRECATED - use external_tools instead (for backward compatibility)
        external_tools: List of external tool names to add (mapped from current 'tools')
        disabled_builtin_tools: List of built-in tools to disable (all enabled by default)
        knowledge: Text knowledge to inject into agent context
        
    Returns:
        AgentWrapper instance with configured tools and knowledge
    """
    # Handle backward compatibility
    if tools is not None:
        if external_tools is not None:
            raise ValueError("Cannot specify both 'tools' and 'external_tools'. Use 'external_tools' instead.")
        external_tools = tools
        warnings.warn("'tools' parameter is deprecated. Use 'external_tools' instead.", DeprecationWarning)
    
    # Load agent definition from YAML (developer created)
    agent_info = load_agent_from_yaml(agent_name)
    
    # Create agent instance
    agent = create_agent_instance(agent_info)
    
    # Apply user configuration
    if external_tools:
        agent.add_external_tools(external_tools)
    
    if disabled_builtin_tools:
        # Validate disabled tools at framework level
        for tool_name in disabled_builtin_tools:
            if tool_name in agent.builtin_tools:
                tool_info = agent.builtin_tools[tool_name]
                if tool_info.required:
                    raise ValueError(f"Built-in tool '{tool_name}' cannot be disabled (required core functionality)")
        agent.disable_builtin_tools(disabled_builtin_tools)
    
    if knowledge:
        agent.inject_knowledge(knowledge)
    
    return agent
```

### **2. Agent Metadata Access**

After loading an agent, you can access its metadata through the returned `AgentWrapper`:

```python
# Load agent
agent = amg.load_agent("agentplug/analysis-agent")

# Access basic metadata
print(f"Agent Name: {agent.name}")
print(f"Namespace: {agent.namespace}")
print(f"Version: {agent.version}")
print(f"Description: {agent.description}")
print(f"Path: {agent.path}")

# Access interface information
print(f"Available Methods: {agent.methods}")
print(f"Built-in Tools: {agent.get_available_tools()}")

# Get detailed method information
method_info = agent.get_method_info("analyze_data")
print(f"Method Parameters: {method_info.get('parameters', {})}")

# Access full agent information
agent_dict = agent.to_dict()
print(f"Full Agent Info: {agent_dict}")

# Access built-in tool information (Phase 3)
for tool_name, tool_info in agent.builtin_tools.items():
    print(f"Tool: {tool_name}")
    print(f"  Required: {tool_info.required}")
    print(f"  Description: {tool_info.description}")
    print(f"  Parameters: {tool_info.parameters}")
```

### **3. Practical Metadata Usage Examples**

```python
# Example 1: Check agent capabilities before using
agent = amg.load_agent("agentplug/analysis-agent")

# Check if agent has specific method
if agent.has_method("analyze_sentiment"):
    result = agent.analyze_sentiment("This is great!")
else:
    print("Sentiment analysis not available")

# Check if agent has specific built-in tool
if "text_analyzer" in agent.builtin_tools:
    tool_info = agent.builtin_tools["text_analyzer"]
    if not tool_info.required:
        print("Text analyzer can be disabled if needed")

# Example 2: Dynamic method discovery
for method in agent.methods:
    method_info = agent.get_method_info(method)
    print(f"Method: {method}")
    print(f"  Description: {method_info.get('description', 'No description')}")
    print(f"  Parameters: {list(method_info.get('parameters', {}).keys())}")

# Example 3: Tool management
print(f"Total built-in tools: {len(agent.builtin_tools)}")
required_tools = [name for name, info in agent.builtin_tools.items() if info.required]
optional_tools = [name for name, info in agent.builtin_tools.items() if not info.required]

print(f"Required tools: {required_tools}")
print(f"Optional tools: {optional_tools}")

# Example 4: Agent introspection
agent_info = agent.to_dict()
print(f"Agent Summary:")
print(f"  Name: {agent_info['name']}")
print(f"  Version: {agent_info['version']}")
print(f"  Methods: {len(agent_info['methods'])}")
print(f"  Tools: {len(agent_info.get('assigned_tools', []))}")
print(f"  Has Runtime: {agent_info['has_runtime']}")
```

## 🔧 **Implementation Components**

### **1. Enhanced Agent Class (Agent Developer Implementation Required)**

**Important**: Since the framework doesn't have direct access to agent built-in tools, agent developers must implement tool management logic.

```python
class AgentClass:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.builtin_tools: Dict[str, ToolInfo] = {}
        self.external_tools: List[str] = []  # Mapped from current 'tools' parameter
        self.disabled_builtin_tools: Set[str] = set()  # Agent manages disabled tools
        self.knowledge: str = ""
        self._load_builtin_tools_from_yaml()
    
    def _load_builtin_tools_from_yaml(self):
        """Load built-in tools from agent.yaml builtin_tools section"""
        # This would be populated from agent.yaml builtin_tools section
        self.builtin_tools = {
            "text_analyzer": ToolInfo(
                name="text_analyzer",
                description="Analyze text content with various analysis types",
                required=True,  # Core functionality - cannot be disabled
                parameters={
                    "text": {"type": "string", "required": True},
                    "analysis_type": {"type": "string", "enum": ["sentiment", "entities", "keywords"]},
                    "confidence_threshold": {"type": "number", "default": 0.8}
                }
            ),
            "keyword_extraction": ToolInfo(
                name="keyword_extraction",
                description="Extract keywords from text content",
                required=False,  # Optional feature - can be disabled
                parameters={
                    "text": {"type": "string", "required": True},
                    "max_keywords": {"type": "integer", "default": 10}
                }
            ),
            "sentiment_analysis": ToolInfo(
                name="sentiment_analysis",
                description="Analyze sentiment of text content",
                required=False,  # Optional feature - can be disabled
                parameters={
                    "text": {"type": "string", "required": True},
                    "model": {"type": "string", "default": "default"}
                }
            )
        }
    
    def disable_builtin_tools(self, disabled_builtin_tools: Set[str]) -> None:
        """Set which tools are disabled (called by framework)"""
        self.disabled_builtin_tools = disabled_builtin_tools
    
    def add_external_tools(self, tool_names: List[str]) -> None:
        """Add external tools from user (mapped from current 'tools' parameter)"""
        for tool_name in tool_names:
            if tool_name not in self.tool_registry.get_available_tools():
                raise ValueError(f"External tool '{tool_name}' not found in registry")
            self.external_tools.append(tool_name)
    
    def inject_knowledge(self, knowledge_text: str) -> None:
        """Inject knowledge - simple text"""
        self.knowledge = knowledge_text
    
    def get_available_tools(self) -> List[str]:
        """Get all available tools (enabled built-in + external)"""
        available = []
        
        # Add enabled built-in tools
        for name, tool in self.builtin_tools.items():
            if name not in self.disabled_builtin_tools:
                available.append(name)
        
        # Add external tools
        available.extend(self.external_tools)
        
        return available
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute tool with disabled tool checking"""
        # Check if tool is disabled
        if tool_name in self.disabled_builtin_tools:
            raise ValueError(f"Tool '{tool_name}' is disabled by user configuration")
        
        # Validate parameters
        errors = self.validate_tool_parameters(tool_name, parameters)
        if errors:
            raise ValueError(f"Tool parameter validation failed: {'; '.join(errors)}")
        
        # Execute tool
        if tool_name in self.builtin_tools:
            return self._execute_builtin_tool(tool_name, parameters)
        elif tool_name in self.external_tools:
            return self._execute_external_tool(tool_name, parameters)
        else:
            raise ValueError(f"Tool '{tool_name}' not found")
    
    def _execute_builtin_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute built-in tool"""
        if tool_name == "text_analyzer":
            return self._text_analyzer(parameters)
        elif tool_name == "keyword_extraction":
            return self._keyword_extraction(parameters)
        elif tool_name == "core_analyzer":
            return self._core_analyzer(parameters)
        else:
            raise ValueError(f"Built-in tool '{tool_name}' not implemented")
    
    def _execute_external_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute external tool via MCP (existing functionality)"""
        # This uses the existing MCP system from Phase 2.5
        return self.tool_registry.execute_tool(tool_name, parameters)
    
    def main(self):
        """Command handler - agent developer must implement this"""
        import sys
        import json
        
        # Parse execution data from framework
        execution_data = json.loads(sys.argv[1])
        method = execution_data["method"]
        parameters = execution_data["parameters"]
        disabled_builtin_tools = set(execution_data.get("disabled_builtin_tools", []))
        
        # Configure disabled tools (set by framework)
        self.disable_builtin_tools(disabled_builtin_tools)
        
        # Execute method
        if method == "analyze_data":
            result = self.analyze_data(parameters)
        elif method == "execute_tool":
            tool_name = parameters["tool_name"]
            tool_params = parameters["parameters"]
            result = self.execute_tool(tool_name, tool_params)
        else:
            result = {"error": f"Unknown method: {method}"}
        
        # Return result
        print(json.dumps(result))

class ToolInfo:
    """Information about a built-in tool"""
    def __init__(self, name: str, description: str, required: bool, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.required = required  # True = cannot be disabled, False = can be disabled
        self.parameters = parameters
```

### **2. Framework Communication System**

**Important**: The framework doesn't have direct access to agent built-in tools, so it communicates disabled tools via command parameters.

```python
class ProcessManager:
    """Framework side - passes disabled tools to agent"""
    
    def execute_agent(self, agent_path: str, method: str, parameters: dict, 
                     disabled_builtin_tools: Set[str] = None) -> dict:
        """Execute agent with disabled tools information"""
        
        # Add disabled tools to execution data
        execution_data = {
            "method": method,
            "parameters": parameters,
            "disabled_builtin_tools": list(disabled_builtin_tools or []),  # Pass to agent
            "tool_context": self.tool_context
        }
        
        # Execute agent command
        result = subprocess.run(
            [python_executable, str(agent_script), json.dumps(execution_data)],
            cwd=str(agent_dir),
            capture_output=True,
            text=True,
            timeout=self.timeout,
        )
        
        return self._parse_result(result)

class AgentWrapper:
    """Framework side - manages user configuration"""
    
    def __init__(self, agent_name: str, disabled_builtin_tools: Set[str] = None):
        self.agent_name = agent_name
        self.disabled_builtin_tools = disabled_builtin_tools or set()
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute tool through agent command with disabled tools info"""
        # Call agent with disabled tools information
        result = self.process_manager.execute_agent(
            agent_path=self.agent_path,
            method="execute_tool",
            parameters={
                "tool_name": tool_name,
                "parameters": parameters
            },
            disabled_builtin_tools=self.disabled_builtin_tools
        )
        
        return result
    
    def get_available_tools(self) -> List[str]:
        """Get available tools from agent (agent handles filtering)"""
        result = self.process_manager.execute_agent(
            agent_path=self.agent_path,
            method="get_available_tools",
            parameters={},
            disabled_builtin_tools=self.disabled_builtin_tools
        )
        
        return result.get("tools", [])
```

### **3. Knowledge Management System**

```python
class KnowledgeManager:
    def __init__(self):
        self.knowledge: str = ""
        self.knowledge_metadata: Dict[str, Any] = {}
    
    def inject_knowledge(self, knowledge_text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Inject text-based knowledge into agent context"""
        self.knowledge = knowledge_text
        self.knowledge_metadata = metadata or {}
    
    def get_knowledge(self) -> str:
        """Get injected knowledge"""
        return self.knowledge
    
    def is_knowledge_available(self) -> bool:
        """Check if knowledge is available"""
        return bool(self.knowledge.strip())
    
    def clear_knowledge(self) -> None:
        """Clear injected knowledge"""
        self.knowledge = ""
        self.knowledge_metadata = {}
```

### **4. Enhanced Error Handling**

```python
class AgentLoadError(Exception):
    """Raised when agent loading fails"""
    def __init__(self, message: str, suggestions: Optional[List[str]] = None):
        super().__init__(message)
        self.suggestions = suggestions or []
    
    def __str__(self):
        base_msg = super().__str__()
        if self.suggestions:
            suggestions_text = "\n".join(f"  • {suggestion}" for suggestion in self.suggestions)
            return f"{base_msg}\n\nSuggestions:\n{suggestions_text}"
        return base_msg

class AgentExecutionError(Exception):
    """Raised when agent execution fails"""
    def __init__(self, message: str, method_name: str, parameters: Dict[str, Any]):
        super().__init__(message)
        self.method_name = method_name
        self.parameters = parameters
    
    def __str__(self):
        return f"Execution failed for method '{self.method_name}': {super().__str__()}"

class ValidationError(Exception):
    """Raised when parameter validation fails"""
    def __init__(self, message: str, parameter_name: str, expected_type: str, actual_value: Any):
        super().__init__(message)
        self.parameter_name = parameter_name
        self.expected_type = expected_type
        self.actual_value = actual_value
    
    def __str__(self):
        return f"Validation failed for parameter '{self.parameter_name}': expected {self.expected_type}, got {type(self.actual_value).__name__}"
```

## 🎯 **User Experience Examples**

### **Basic Agent Loading**
```python
import agentmanager as amg

# Simple agent loading
agent = amg.load_agent("agentplug/analysis-agent")
result = agent.analyze_data("Customer feedback text")
```

### **Backward Compatibility (Phase 2.5 → Phase 3)**
```python
# Current usage (Phase 2.5) - still works with deprecation warning
agent = amg.load_agent(
    "agentplug/analysis-agent",
    tools=['web_search', 'rag']  # DEPRECATED: use external_tools instead
)
```

### **Agent with Tool Configuration (Phase 3)**
```python
# New usage (Phase 3) - more explicit and powerful
agent = amg.load_agent(
    "agentplug/analysis-agent",
    external_tools=['web_search', 'rag'],  # Mapped from current 'tools' parameter
    disabled_builtin_tools=['keyword_extraction']  # New: disable built-in tools
)

# Check available tools
tools = agent.get_available_tools()
print(f"Available tools: {tools}")
# Output: ['text_analyzer', 'sentiment_analysis', 'web_search', 'rag']
# Note: 'keyword_extraction' is disabled, so it's not in the list

# Use agent with tools
result = agent.analyze_data("Customer feedback text", {"use_tools": True})
```

### **Error Handling for Required Tools**
```python
# This will raise an error - cannot disable required tools
try:
    agent = amg.load_agent(
        "agentplug/analysis-agent",
        disabled_builtin_tools=['text_analyzer']  # ERROR: text_analyzer is required
    )
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: Built-in tool 'text_analyzer' cannot be disabled (required core functionality)

# This works - can disable optional tools
agent = amg.load_agent(
    "agentplug/analysis-agent",
    disabled_builtin_tools=['keyword_extraction', 'sentiment_analysis']  # OK: both are optional
)
```

### **Agent with Knowledge Injection**
```python
# Agent with knowledge for better responses
agent = amg.load_agent(
    "agentplug/analysis-agent",
    knowledge="You are a data analysis expert. Always provide detailed insights and explanations. For sentiment analysis, return confidence scores and reasoning."
)

# Agent now uses knowledge for better responses
result = agent.analyze_data("Customer feedback text")
```

### **Complete Configuration**
```python
# Full configuration example
agent = amg.load_agent(
    "agentplug/analysis-agent",
    external_tools=['web_search', 'rag', 'data_visualizer'],
    disabled_builtin_tools=['keyword_extraction', 'sentiment_analysis'],
    knowledge="You are a data analysis expert specializing in customer feedback analysis. Always provide actionable insights and recommendations."
)

# Agent works with user's complete configuration
result = agent.analyze_data("Customer feedback text", {"analysis_type": "comprehensive"})
```

## 📋 **Implementation Roadmap**

### **Week 1-2: Enhanced agent.yaml Schema**
- [ ] Add builtin_tools section to agent.yaml
- [ ] Update agent validation to handle new schema
- [ ] Create tool configuration parser

### **Week 3-4: User-Oriented API**
- [ ] Implement simplified load_agent function
- [ ] Add external_tools parameter
- [ ] Add disabled_builtin_tools parameter
- [ ] Add knowledge parameter

### **Week 5-6: Tool Management System**
- [ ] Implement ToolManager class
- [ ] Add tool conflict resolution
- [ ] Add tool parameter validation
- [ ] Integrate with existing MCP system

### **Week 7-8: Knowledge Management**
- [ ] Implement KnowledgeManager class
- [ ] Add knowledge injection to agent context
- [ ] Add knowledge query capabilities
- [ ] Integrate with agent execution

### **Week 9-10: Error Handling & Testing**
- [ ] Implement enhanced error types
- [ ] Add comprehensive error messages
- [ ] Add parameter validation
- [ ] Create comprehensive test suite

### **Week 11-12: Integration & Documentation**
- [ ] Integrate all components
- [ ] Update documentation
- [ ] Create migration examples
- [ ] Performance optimization

## 🎯 **Success Metrics**

- **User Experience**: 90%+ users can configure agents without documentation
- **Error Recovery**: 95%+ of errors provide actionable suggestions
- **Tool Management**: 100% of tool conflicts resolved automatically
- **Knowledge Integration**: 90%+ of users successfully inject knowledge
- **Performance**: <2s agent loading time, <500ms tool execution

## 🔄 **Migration Strategy**

### **For Existing Agents (Breaking Change Required)**
1. **Agent Developer Implementation**: Existing agents must implement tool management logic
2. **Required Changes**: Add `disable_builtin_tools()`, `get_available_tools()`, and `main()` methods
3. **Migration Helper**: CLI tool to help migrate agents to new interface
4. **Transition Period**: Framework supports both old and new agent interfaces during transition

### **For Users**
1. **Enhanced Features**: New features available through new parameters
2. **Clear Documentation**: Migration guide and examples for agent developers
3. **Support**: Help with migration process
4. **Breaking Change**: Existing agents need updates to support tool disabling

### **Migration Requirements for Agent Developers**
```python
# Existing agents must add these methods:
class ExistingAgent:
    def disable_builtin_tools(self, disabled_builtin_tools: Set[str]) -> None:
        """Required: Set which tools are disabled"""
        self.disabled_builtin_tools = disabled_builtin_tools
    
    def get_available_tools(self) -> List[str]:
        """Required: Return available tools (filtered by disabled)"""
        return [tool for tool in self.all_tools if tool not in self.disabled_builtin_tools]
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Required: Check if tool is disabled before executing"""
        if tool_name in self.disabled_builtin_tools:
            raise ValueError(f"Tool '{tool_name}' is disabled")
        # ... existing tool execution logic
    
    def main(self):
        """Required: Command handler for framework communication"""
        import sys
        import json
        
        execution_data = json.loads(sys.argv[1])
        disabled_builtin_tools = set(execution_data.get("disabled_builtin_tools", []))
        
        self.disable_builtin_tools(disabled_builtin_tools)
        # ... rest of command handling
```

## 🚀 **Key Benefits**

### **For Users**
- **Simple Interface**: No YAML editing required
- **Intuitive Parameters**: Clear, self-explanatory parameter names
- **Quick Setup**: Configure agents in seconds
- **Powerful Features**: Full tool and knowledge management

### **For Agent Developers**
- **Rich YAML**: Define complex tool schemas and capabilities
- **Clear Documentation**: YAML serves as living documentation
- **Flexible Design**: Support any tool parameters and validation
- **Tool Management Implementation**: Must implement tool disabling logic in agent code
- **Command Interface**: Must implement command handler for framework communication

### **For Framework**
- **Clean Architecture**: Clear separation of concerns
- **Maintainable**: Easy to extend and modify
- **Production Ready**: Robust error handling and validation

---

**Phase 3 transforms AgentHub into a production-ready platform with a user-oriented interface that makes agent configuration simple and intuitive while maintaining the power and flexibility needed for complex use cases.**
