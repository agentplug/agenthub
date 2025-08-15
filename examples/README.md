# AgentHub Examples

This directory contains comprehensive examples demonstrating the AgentHub Phase 1 Foundation functionality. All examples are designed to run from the `examples/` directory and automatically handle Python path configuration.

## 🚀 Available Examples

### 1. **Runtime Module Example** (`runtime_example.py`)
**Complete agent execution system demonstration**

Shows how to use the Runtime Module to execute AI agents with proper storage integration, process isolation, and error handling.

**Key Features Demonstrated:**
- Agent discovery via Storage Module
- Process isolation and virtual environment management
- Real AI agent execution with actual results
- Comprehensive error handling
- Agent metadata and interface inspection

**Run:** `python runtime_example.py`

### 2. **Storage Module Example** (`storage_example.py`)
**Agent discovery and storage management**

Demonstrates how to use the Storage Module to discover agents, manage the AgentHub directory structure, and inspect agent metadata.

**Key Features Demonstrated:**
- AgentHub directory structure management
- Agent discovery with metadata extraction
- Agent existence checking
- Path resolution and validation
- Directory content inspection
- Storage statistics and monitoring

**Run:** `python storage_example.py`

### 3. **Integration Example** (`integration_example.py`)
**Complete Storage + Runtime integration**

Shows how the Storage and Runtime modules work together to provide a complete agent management and execution system.

**Key Features Demonstrated:**
- Seamless Storage + Runtime coordination
- Agent discovery and validation pipeline
- Multi-agent execution with proper isolation
- Cross-agent workflow capabilities
- Error handling across both modules
- Performance monitoring and statistics

**Run:** `python integration_example.py`

### 4. **Error Handling Example** (`error_handling_example.py`)
**Comprehensive error scenarios and handling**

Demonstrates how the AgentHub system handles various error conditions gracefully with helpful error messages and recovery suggestions.

**Key Features Demonstrated:**
- Comprehensive input validation
- Graceful error recovery
- Helpful error messages and suggestions
- Proper exception handling and logging
- Process isolation prevents system corruption
- Timeout protection against hanging processes

**Run:** `python error_handling_example.py`

## 📋 Prerequisites

Before running the examples, ensure you have:

1. **Completed setup:** Run `./setup.sh` from the project root
2. **Created seed agents:** The agents in `~/.agenthub/agents/agentplug/` (coding-agent, analysis-agent)
3. **API keys configured:** Set `OPENAI_API_KEY` environment variable or in `.env` files

## 🎯 What You'll See

### Real AI Execution
The examples execute actual AI agents that generate real results:
- **Coding Agent:** Generates actual Python code based on prompts
- **Analysis Agent:** Provides real sentiment analysis and text summarization

### Process Isolation
Each agent runs in its own:
- Virtual environment (`.venv`)
- Subprocess with timeout protection
- Isolated dependency management

### Comprehensive Error Handling
Examples demonstrate robust error handling for:
- Nonexistent agents and methods
- Invalid parameters and malformed files
- Process timeouts and system errors
- Missing dependencies and path issues

## 🏗️ Architecture Demonstrated

```
Storage Module ←→ Runtime Module
     ↓                ↓
   Discovery      Execution
   Validation     Isolation
   Metadata       Error Handling
```

## 🔧 Technical Implementation

**Python Path Handling:**
```python
# Each example includes this pattern for clean imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
```

**Module Integration:**
```python
from agentmanager.storage.local_storage import LocalStorage
from agentmanager.runtime.agent_runtime import AgentRuntime

storage = LocalStorage()
runtime = AgentRuntime(storage=storage)
```

## 📊 Performance Expectations

- **Storage operations:** Instant (local filesystem)
- **Agent discovery:** < 100ms
- **Agent execution:** 2-3 seconds (includes AI API calls)
- **Error handling:** < 50ms

## 🎉 Success Indicators

When running examples, look for:
- ✅ Successful agent discovery
- ✅ Real AI-generated results
- ✅ Clear error messages with suggestions
- ✅ Proper execution times and statistics
- ✅ Cross-agent workflow completion

## 🚨 Troubleshooting

**If examples fail:**

1. **Import errors:** Ensure you're running from the `examples/` directory
2. **No agents found:** Create seed agents first using setup instructions
3. **API errors:** Check `OPENAI_API_KEY` environment variable
4. **Permission errors:** Check write permissions to `~/.agenthub/`

**Common solutions:**
```bash
# From project root
cd examples
python runtime_example.py

# If still failing, check setup
cd ..
./setup.sh
```

## 🔗 Next Steps

After running the examples:
1. **Explore the code** - Each example is heavily commented
2. **Try modifications** - Change prompts and parameters
3. **Create your own agents** - Follow the seed agent pattern
4. **Build workflows** - Combine multiple agents for complex tasks

These examples provide the foundation for understanding how to build and deploy your own AI agent ecosystem using AgentHub!
