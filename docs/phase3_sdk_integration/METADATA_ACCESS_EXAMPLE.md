# Agent Metadata Access Examples

This document shows how to access agent metadata after loading in Phase 3.

## 🎯 **Basic Metadata Access**

```python
import agentmanager as amg

# Load an agent
agent = amg.load_agent("agentplug/analysis-agent")

# Access basic information
print(f"Agent Name: {agent.name}")
print(f"Namespace: {agent.namespace}")
print(f"Version: {agent.version}")
print(f"Description: {agent.description}")
print(f"Path: {agent.path}")
```

## 🔍 **Method Information**

```python
# List all available methods
print(f"Available Methods: {agent.methods}")

# Check if a specific method exists
if agent.has_method("analyze_data"):
    print("✅ analyze_data method is available")
else:
    print("❌ analyze_data method not found")

# Get detailed method information
try:
    method_info = agent.get_method_info("analyze_data")
    print(f"Method Description: {method_info.get('description', 'No description')}")
    print(f"Method Parameters: {list(method_info.get('parameters', {}).keys())}")
    
    # Show parameter details
    for param_name, param_info in method_info.get('parameters', {}).items():
        param_type = param_info.get('type', 'unknown')
        required = param_info.get('required', False)
        default = param_info.get('default', 'No default')
        print(f"  {param_name}: {param_type} {'(required)' if required else f'(default: {default})'}")
        
except Exception as e:
    print(f"Error getting method info: {e}")
```

## 🛠️ **Built-in Tools Information (Phase 3)**

```python
# Access built-in tools
print(f"Built-in Tools: {list(agent.builtin_tools.keys())}")

# Get detailed tool information
for tool_name, tool_info in agent.builtin_tools.items():
    print(f"\nTool: {tool_name}")
    print(f"  Required: {tool_info.required}")
    print(f"  Description: {tool_info.description}")
    print(f"  Parameters: {tool_info.parameters}")
    
    # Check if tool can be disabled
    if tool_info.required:
        print(f"  ⚠️  This tool cannot be disabled (core functionality)")
    else:
        print(f"  ✅ This tool can be disabled if needed")
```

## 📊 **Agent Capabilities Summary**

```python
# Get comprehensive agent information
agent_info = agent.to_dict()

print("🤖 Agent Capabilities Summary:")
print(f"  Name: {agent_info['name']}")
print(f"  Version: {agent_info['version']}")
print(f"  Description: {agent_info['description']}")
print(f"  Methods: {len(agent_info['methods'])}")
print(f"  Built-in Tools: {len(agent.builtin_tools)}")
print(f"  External Tools: {len(agent_info.get('assigned_tools', []))}")
print(f"  Has Runtime: {agent_info['has_runtime']}")

# Show method list
print(f"\n📋 Available Methods:")
for method in agent_info['methods']:
    print(f"  • {method}")

# Show built-in tools list
print(f"\n🔧 Built-in Tools:")
for tool_name, tool_info in agent.builtin_tools.items():
    status = "🔒 Required" if tool_info.required else "🔓 Optional"
    print(f"  • {tool_name} - {status}")
```

## 🔄 **Dynamic Agent Discovery**

```python
# Example: Build a dynamic agent interface
def build_agent_interface(agent):
    """Build a dynamic interface for an agent based on its metadata."""
    
    interface = {
        "name": agent.name,
        "version": agent.version,
        "description": agent.description,
        "methods": {},
        "tools": {}
    }
    
    # Add method information
    for method_name in agent.methods:
        try:
            method_info = agent.get_method_info(method_name)
            interface["methods"][method_name] = {
                "description": method_info.get("description", ""),
                "parameters": method_info.get("parameters", {}),
                "returns": method_info.get("returns", {})
            }
        except Exception as e:
            interface["methods"][method_name] = {"error": str(e)}
    
    # Add tool information
    for tool_name, tool_info in agent.builtin_tools.items():
        interface["tools"][tool_name] = {
            "description": tool_info.description,
            "required": tool_info.required,
            "parameters": tool_info.parameters
        }
    
    return interface

# Use the dynamic interface
agent = amg.load_agent("agentplug/analysis-agent")
interface = build_agent_interface(agent)

print("🔍 Dynamic Agent Interface:")
print(f"Methods: {list(interface['methods'].keys())}")
print(f"Tools: {list(interface['tools'].keys())}")
```

## 🎯 **Practical Usage Patterns**

```python
# Pattern 1: Capability checking before execution
def safe_execute_method(agent, method_name, *args, **kwargs):
    """Safely execute a method with capability checking."""
    if not agent.has_method(method_name):
        available = ", ".join(agent.methods)
        raise ValueError(f"Method '{method_name}' not available. Available: {available}")
    
    try:
        return agent.execute(method_name, kwargs if kwargs else {})
    except Exception as e:
        raise RuntimeError(f"Failed to execute {method_name}: {e}")

# Pattern 2: Tool availability checking
def check_tool_availability(agent, tool_name):
    """Check if a tool is available and can be disabled."""
    if tool_name not in agent.builtin_tools:
        return False, "Tool not found"
    
    tool_info = agent.builtin_tools[tool_name]
    if tool_info.required:
        return True, "Tool available but required (cannot be disabled)"
    else:
        return True, "Tool available and can be disabled"

# Pattern 3: Agent validation
def validate_agent(agent):
    """Validate that an agent meets minimum requirements."""
    issues = []
    
    if not agent.methods:
        issues.append("No methods available")
    
    if not agent.builtin_tools:
        issues.append("No built-in tools defined")
    
    required_tools = [name for name, info in agent.builtin_tools.items() if info.required]
    if not required_tools:
        issues.append("No required tools defined")
    
    return len(issues) == 0, issues

# Usage examples
agent = amg.load_agent("agentplug/analysis-agent")

# Safe execution
try:
    result = safe_execute_method(agent, "analyze_data", text="Sample text")
    print(f"Analysis result: {result}")
except Exception as e:
    print(f"Error: {e}")

# Tool checking
for tool_name in ["text_analyzer", "keyword_extraction"]:
    available, message = check_tool_availability(agent, tool_name)
    print(f"{tool_name}: {message}")

# Agent validation
is_valid, issues = validate_agent(agent)
if is_valid:
    print("✅ Agent is valid")
else:
    print(f"❌ Agent has issues: {issues}")
```

## 📝 **Summary**

The `AgentWrapper` provides comprehensive metadata access through:

- **Basic Properties**: `name`, `namespace`, `version`, `description`, `path`
- **Method Information**: `methods`, `has_method()`, `get_method_info()`
- **Tool Information**: `builtin_tools`, `get_available_tools()`
- **Full Information**: `to_dict()` for complete agent data
- **Runtime Information**: `has_runtime`, `assigned_tools`

This allows you to build dynamic, robust applications that can adapt to different agent capabilities and configurations.
