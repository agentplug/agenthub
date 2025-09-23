# Core Module - Phase 3.2

**Purpose**: Core functionality for intelligent solve() method with LLM-powered decision making

## 📁 **Submodules**

### **agents/**
- Enhanced AgentWrapper with solve() method
- LLMDecisionEngine for method selection
- Agent custom solve() interface and support
- Method selection and parameter extraction

### **llm/**
- SolveLLMService for LLM integration
- Method selection prompts and templates
- Parameter extraction prompts
- LLM error handling and fallbacks

## 🔄 **Module Dependencies**

- **llm** → **agents** (LLM service must be available before agents can use it)
- **agents** → **runtime** (solve() method must be implemented before runtime can use it)
- **runtime** → **sdk** (solve() execution must work before SDK can expose it)

## 🎯 **Key Features**

- **solve() Method**: Intelligent problem-solving interface
- **LLM Integration**: aisuite integration for decision making
- **Agent Customization**: Support for agent-specific solve() methods
- **Method Selection**: LLM-powered method selection from agent metadata
- **Parameter Extraction**: Intelligent parameter extraction from natural language
- **Error Handling**: Robust error handling and fallback mechanisms
