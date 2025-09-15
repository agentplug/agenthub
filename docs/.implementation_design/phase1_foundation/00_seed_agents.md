# Phase 1: Seed Agent Creation

**Document Type**: Seed Agent Creation Guide
**Phase**: 1 - Foundation (Prerequisite)
**Author**: William
**Date Created**: 2025-06-28
**Last Updated**: 2025-06-28
**Status**: Active
**Purpose**: Create working seed agents that Phase 1 will test with

## 🎯 **Seed Agent Creation Overview**

**Seed agents are the foundation of Phase 1 testing.** Without working agents to test with, we cannot validate that our runtime, storage, core, or CLI modules work correctly.

### **Critical Success Factor**
- ✅ **Must be created BEFORE** any other Phase 1 development
- ✅ **Must work independently** before integration testing
- ✅ **Must have proper structure** (agent.yaml, agent.py, etc.)
- ✅ **Must provide real functionality** (not just mock responses)

## 🌱 **Required Seed Agents**

### **Critical: Independent Virtual Environments**
Each agent **MUST** have its own independent virtual environment (`.venv/` directory) to ensure:
- **Dependency Isolation**: No conflicts between agent packages
- **Security**: Agents can't access system packages
- **Reproducibility**: Exact dependency versions for each agent
- **Maintenance**: Easy to update/remove individual agent environments

### **1. agentplug/coding-agent**

#### **Purpose**
Generate Python code based on natural language prompts.

#### **Methods**
```yaml
interface:
  methods:
    generate_code:
      description: "Generate Python code based on a prompt"
      parameters:
        prompt:
          type: "string"
          description: "Natural language description of code to generate"
          required: true
      returns:
        type: "string"
        description: "Generated Python code"

    explain_code:
      description: "Explain what a piece of Python code does"
      parameters:
        code:
          type: "string"
          description: "Python code to explain"
          required: true
      returns:
        type: "string"
        description: "Explanation of what the code does"
```

#### **Functionality Requirements**
- Actually generates working Python code using AI
- Handles common coding requests (functions, classes, loops, etc.)
- Provides helpful error messages for invalid requests
- Returns properly formatted Python code

#### **Dependencies**
- **aisuite**: For unified AI provider interface
- **python-dotenv**: For API key management
- **Minimal external packages**: Only essential AI integration
- **Lightweight implementation**: Efficient AI calls

### **2. agentplug/analysis-agent**

#### **Purpose**
Analyze text content and provide insights.

#### **Methods**
```yaml
interface:
  methods:
    analyze_text:
      description: "Analyze text and provide insights"
      parameters:
        text:
          type: "string"
          description: "Text content to analyze"
          required: true
        analysis_type:
          type: "string"
          description: "Type of analysis (sentiment, key_points, summary)"
          required: false
          default: "general"
      returns:
        type: "object"
        description: "Analysis results with insights"

    summarize_content:
      description: "Create a summary of content"
      parameters:
        content:
          type: "string"
          description: "Content to summarize"
          required: true
        max_length:
          type: "integer"
          description: "Maximum summary length"
          required: false
          default: 200
      returns:
        type: "string"
        description: "Summarized content"
```

#### **Functionality Requirements**
- Actually analyzes text content using AI
- Provides different types of analysis
- Handles various content lengths
- Returns structured, useful insights

#### **Dependencies**
- **aisuite**: For unified AI provider interface
- **python-dotenv**: For API key management
- **Minimal external packages**: Only essential AI integration
- **Lightweight implementation**: Efficient AI calls

## 🏗️ **Agent Directory Structure**

### **Standard Structure**
```
~/.agenthub/agents/agentplug/
├── coding-agent/
│   ├── agent.yaml           # Agent manifest (required)
│   ├── agent.py             # Main agent script (required)
│   ├── requirements.txt     # Dependencies (optional)
│   ├── README.md            # Documentation (optional)
│   ├── .venv/               # Independent virtual environment (required)
│   │   ├── bin/             # Python executable and scripts
│   │   ├── lib/             # Installed packages
│   │   └── pyvenv.cfg       # Virtual environment config
│   └── examples/            # Example usage (optional)
│       ├── basic_usage.py
│       └── advanced_usage.py
└── analysis-agent/
    ├── agent.yaml           # Agent manifest (required)
    ├── agent.py             # Main agent script (required)
    ├── requirements.txt     # Dependencies (optional)
    ├── README.md            # Documentation (optional)
    ├── .venv/               # Independent virtual environment (required)
    │   ├── bin/             # Python executable and scripts
    │   ├── lib/             # Installed packages
    │   └── pyvenv.cfg       # Virtual environment config
    └── examples/            # Example usage (optional)
        ├── basic_usage.py
        └── advanced_usage.py
```

### **File Requirements**

#### **agent.yaml (Required)**
```yaml
name: "coding-agent"
version: "1.0.0"
description: "Generate Python code based on natural language prompts"
author: "agentplug"
license: "MIT"
python_version: "3.12+"

interface:
  methods:
    generate_code:
      description: "Generate Python code based on a prompt"
      parameters:
        prompt:
          type: "string"
          description: "Natural language description of code to generate"
          required: true
      returns:
        type: "string"
        description: "Generated Python code"

    explain_code:
      description: "Explain what a piece of Python code does"
      parameters:
        code:
          type: "string"
          description: "Python code to explain"
          required: true
      returns:
        type: "string"
        description: "Explanation of what the code does"

dependencies:
  - "aisuite[openai]>=0.1.7"
  - "python-dotenv>=1.0.0"
tags: ["code-generation", "python", "ai-assistant"]
```

#### **agent.py (Required)**
```python
#!/usr/bin/env python3
"""
Agent Hub Agent: coding-agent
Generates Python code based on natural language prompts.
"""

import json
import sys
from typing import Dict, Any

class CodingAgent:
    """Python code generation agent."""

    def __init__(self):
        """Initialize the coding agent."""
        pass

    def generate_code(self, prompt: str) -> str:
        """
        Generate Python code based on a prompt using AI.

        Args:
            prompt: Natural language description of code to generate

        Returns:
            Generated Python code as a string
        """
        try:
            import aisuite as ai
            from dotenv import load_dotenv
            load_dotenv()

            client = ai.Client()
            messages = [
                {"role": "system", "content": "You are a Python code generator. Generate only valid, working Python code. Do not include explanations, just the code."},
                {"role": "user", "content": prompt}
            ]

            response = client.chat.completions.create(
                model="openai:gpt-4o",
                messages=messages,
                temperature=0.1
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"# Error generating code: {str(e)}\n# Please check your API key and internet connection."

    def explain_code(self, code: str) -> str:
        """
        Explain what a piece of Python code does using AI.

        Args:
            code: Python code to explain

        Returns:
            Explanation of what the code does
        """
        try:
            import aisuite as ai
            from dotenv import load_dotenv
            load_dotenv()

            client = ai.Client()
            messages = [
                {"role": "system", "content": "You are a Python code explainer. Explain what the code does in simple terms."},
                {"role": "user", "content": f"Explain this Python code:\n{code}"}
            ]

            response = client.chat.completions.create(
                model="openai:gpt-4o",
                messages=messages,
                temperature=0.1
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"Error explaining code: {str(e)}. Please check your API key and internet connection."

def main():
    """Main entry point for agent execution."""
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Invalid arguments"}))
        sys.exit(1)

    try:
        # Parse input from command line
        input_data = json.loads(sys.argv[1])
        method = input_data.get("method")
        parameters = input_data.get("parameters", {})

        # Create agent instance
        agent = CodingAgent()

        # Execute requested method
        if method == "generate_code":
            result = agent.generate_code(parameters.get("prompt", ""))
            print(json.dumps({"result": result}))
        elif method == "explain_code":
            result = agent.explain_code(parameters.get("code", ""))
            print(json.dumps({"result": result}))
        else:
            print(json.dumps({"error": f"Unknown method: {method}"}))
            sys.exit(1)

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## 🧪 **Testing Seed Agents**

### **Independent Testing (Before Integration)**
Each seed agent must work independently before being used in Phase 1 testing.

#### **Test coding-agent**
```bash
# Test generate_code method (must use virtual environment)
cd ~/.agenthub/agents/agentplug/coding-agent
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows

python agent.py '{"method": "generate_code", "parameters": {"prompt": "Create a function that adds two numbers"}}'

# Expected output:
# {"result": "def add_numbers(a, b):\n    return a + b"}

# Test explain_code method
python agent.py '{"method": "explain_code", "parameters": {"code": "def add_numbers(a, b): return a + b"}}'

# Expected output:
# {"result": "This function takes two parameters 'a' and 'b' and returns their sum."}
```

#### **Test analysis-agent**
```bash
# Test analyze_text method
python agent.py '{"method": "analyze_text", "parameters": {"text": "Python is a great programming language for beginners."}}'

# Test summarize_content method
python agent.py '{"method": "summarize_content", "parameters": {"content": "Long text content here..."}}'
```

### **Success Criteria for Seed Agents**
- ✅ **Execute independently**: `python agent.py` works
- ✅ **Handle valid requests**: Methods return expected results
- ✅ **Handle invalid requests**: Graceful error handling
- ✅ **JSON output**: Proper JSON formatting for integration
- ✅ **Real functionality**: Not just mock responses

## 🚀 **Implementation Steps**

### **Step 0: Set Up AI Environment**
```bash
# Install aisuite and dependencies
pip install 'aisuite[openai]' python-dotenv

# Set up API keys in .env file
echo "OPENAI_API_KEY=your-openai-api-key-here" > ~/.agenthub/.env
echo "ANTHROPIC_API_KEY=your-anthropic-api-key-here" >> ~/.agenthub/.env

# Or set environment variables
export OPENAI_API_KEY="your-openai-api-key-here"
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
```

### **Step 0.5: Set Up UV Package Manager**
```bash
# Install UV package manager (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

### **Step 1: Create Agent Directories and Virtual Environments**
```bash
# Create agent directories
mkdir -p ~/.agenthub/agents/agentplug/coding-agent
mkdir -p ~/.agenthub/agents/agentplug/analysis-agent

# Create independent virtual environments for each agent
cd ~/.agenthub/agents/agentplug/coding-agent
uv venv .venv

cd ~/.agenthub/agents/agentplug/analysis-agent
uv venv .venv
```

### **Step 2: Create Agent Manifests**
- Write `agent.yaml` files with proper interface definitions
- Ensure all required fields are present
- Validate YAML syntax

### **Step 3: Install Dependencies in Virtual Environments**
```bash
# Install dependencies in coding-agent environment
cd ~/.agenthub/agents/agentplug/coding-agent
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows
uv pip install 'aisuite[openai]' python-dotenv

# Install dependencies in analysis-agent environment
cd ~/.agenthub/agents/agentplug/analysis-agent
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows
uv pip install 'aisuite[openai]' python-dotenv
```

### **Step 4: Implement Agent Logic**
- Write `agent.py` files with actual functionality
- Implement all defined methods
- Add proper error handling
- Test JSON input/output format

### **Step 4: Test Independently**
- Test each agent in isolation
- Verify methods work as expected
- Ensure proper error handling
- Validate JSON output format

### **Step 5: Document and Examples**
- Add README.md files
- Create example usage files
- Document any dependencies
- Provide usage instructions

## ⚠️ **Common Pitfalls**

### **1. Mock Responses**
- ❌ **Don't**: Return hardcoded mock responses
- ✅ **Do**: Use aisuite to provide real AI functionality

### **2. Missing AI Integration**
- ❌ **Don't**: Try to implement AI without proper libraries
- ✅ **Do**: Use aisuite for unified AI provider interface

### **2. Complex Dependencies**
- ❌ **Don't**: Require heavy external packages
- ✅ **Do**: Use standard library or minimal dependencies

### **3. Poor Error Handling**
- ❌ **Don't**: Let exceptions crash the agent
- ✅ **Do**: Catch exceptions and return JSON error responses

### **4. Invalid JSON**
- ❌ **Don't**: Output malformed JSON
- ✅ **Do**: Always output valid JSON with proper error handling

### **5. Missing Methods**
- ❌ **Don't**: Define methods in YAML that don't exist in code
- ✅ **Do**: Ensure code matches YAML interface exactly

## 🎯 **Success Validation**

### **Before Phase 1 Development**
- ✅ Both seed agents created and working
- ✅ Agents can be executed independently
- ✅ Methods return expected results
- ✅ Error handling works properly
- ✅ JSON output is valid and consistent

### **Integration Readiness**
- ✅ Agents ready for Runtime Module testing
- ✅ Agents ready for Storage Module testing
- ✅ Agents ready for Core Module testing
- ✅ Agents ready for CLI Module testing

## 🔄 **Next Steps After Seed Agent Creation**

1. **Validate seed agents work independently**
2. **Begin Phase 1 module development**
3. **Test modules with working seed agents**
4. **Iterate and improve based on testing**

## 📋 **Checklist**

- [ ] Set up aisuite and API keys
- [ ] Install UV package manager
- [ ] Create `~/.agenthub/agents/agentplug/` directory structure
- [ ] Create independent virtual environments for each agent using UV
- [ ] Install dependencies in each agent's virtual environment
- [ ] Write `agent.yaml` for coding-agent with aisuite dependencies
- [ ] Write `agent.py` for coding-agent with aisuite AI integration
- [ ] Write `agent.yaml` for analysis-agent with aisuite dependencies
- [ ] Write `agent.py` for analysis-agent with aisuite AI integration
- [ ] Test coding-agent independently with AI calls (in virtual environment)
- [ ] Test analysis-agent independently with AI calls (in virtual environment)
- [ ] Validate JSON input/output format
- [ ] Test error handling scenarios (API failures, etc.)
- [ ] Document agent usage and examples
- [ ] Verify agents are ready for Phase 1 integration

**Seed agents are the foundation of Phase 1 success. Without them, we cannot validate that our system works. Create them first, test them thoroughly, then proceed with Phase 1 development.**
