# Phase 3: Installation Commands with UV

**Document Type**: Implementation Example  
**Author**: AgentHub Team  
**Date Created**: 2025-01-27  
**Last Updated**: 2025-01-27  
**Status**: Ready for Implementation  
**Purpose**: Show how Phase 3 uses installation commands instead of dependencies list

## 🎯 **Key Change: Commands Instead of Dependencies**

Instead of listing dependencies in `agent.yaml`, Phase 3 uses **installation commands** that work with the current UV system. Dependencies are managed in standard Python files (`pyproject.toml` or `requirements.txt`).

## 📁 **Agent Repository Structure**

```
agentplug/analysis-agent/
├── agent.yaml              # Agent configuration + installation commands
├── pyproject.toml          # Main dependencies (UV standard)
├── requirements.txt        # Additional dependencies (optional)
├── agent.py               # Agent implementation
└── README.md              # Agent documentation
```

## 🔧 **agent.yaml with Installation Commands**

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

## 📦 **pyproject.toml (Main Dependencies)**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "analysis-agent"
version = "1.0.0"
description = "Analyze text content and provide insights"
authors = [
    {name = "agentplug", email = "contact@agentplug.com"}
]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "aisuite[openai]>=0.1.7",
    "python-dotenv>=1.0.0",
    "nltk>=3.7",
    "spacy>=3.4.0",
    "textblob>=0.17.1",
    "vaderSentiment>=3.3.2",
    "yake>=0.4.8"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=22.0.0",
    "ruff>=0.1.0"
]

[tool.hatch.build.targets.wheel]
packages = ["src"]
```

## 📋 **requirements.txt (Additional Dependencies)**

```txt
# Additional dependencies not in pyproject.toml
# This file is optional - only needed for extra packages
requests>=2.28.0
beautifulsoup4>=4.11.0
```

## 🚀 **How Current UV System Uses This**

### **1. Environment Creation**
```bash
# Current system runs from agent.yaml installation.commands:
uv venv .venv
```

### **2. Dependency Installation**
```bash
# Current system runs from agent.yaml installation.commands:
uv pip install -e .                    # Install from pyproject.toml
uv pip install -r requirements.txt     # Install additional dependencies
```

### **3. Validation**
```bash
# Current system runs from agent.yaml installation.validation:
python -c 'import nltk; import spacy'
python -c 'import textblob; import vaderSentiment'
python -c 'import yake'
```

## 🔄 **Current System Integration**

The current UV system already supports this approach:

```python
# From environment_setup.py - current system already does this
def setup_environment(self, agent_path: str) -> EnvironmentSetupResult:
    # Step 1: Create virtual environment using UV
    create_result = subprocess.run(
        ["uv", "venv", ".venv"],  # From installation.commands[0]
        cwd=agent_path,
        capture_output=True,
        text=True,
        timeout=60
    )
    
    # Step 2: Install dependencies
    if dependencies:
        result = subprocess.run(
            ["uv", "pip", "install", "--python", str(venv_python)] + dependencies,
            cwd=agent_path,
            capture_output=True,
            text=True,
            timeout=300
        )
    else:
        # Fallback to requirements.txt
        result = subprocess.run(
            ["uv", "pip", "install", "--python", str(venv_python), "-r", "requirements.txt"],
            cwd=agent_path,
            capture_output=True,
            text=True,
            timeout=300
        )
```

## ✅ **Benefits of This Approach**

### **1. Standard Python Packaging**
- **pyproject.toml**: Industry standard for Python projects
- **requirements.txt**: Familiar format for additional dependencies
- **UV Compatibility**: Works perfectly with current UV system

### **2. Clear Separation of Concerns**
- **agent.yaml**: Agent configuration and installation commands
- **pyproject.toml**: Main project dependencies
- **requirements.txt**: Additional dependencies

### **3. Flexible Installation**
- **Multiple Sources**: Can install from both pyproject.toml and requirements.txt
- **Custom Commands**: Can add any installation commands needed
- **Validation**: Can verify installation with custom validation commands

### **4. Backward Compatibility**
- **Current System**: Already uses UV and supports this approach
- **No Changes**: Current installation flow continues to work
- **Enhanced**: New installation commands provide more flexibility

## 🎯 **Migration from Current System**

### **Current agent.yaml (Phase 2.5)**
```yaml
dependencies: 
  - "aisuite[openai]>=0.1.7"
  - "python-dotenv>=1.0.0"
```

### **New agent.yaml (Phase 3)**
```yaml
installation:
  commands:
    - "uv venv .venv"
    - "uv pip install -e ."  # Dependencies now in pyproject.toml
    - "uv pip install -r requirements.txt"
  validation:
    - "python -c 'import aisuite'"
    - "python -c 'import dotenv'"
```

## 🚀 **Implementation Strategy**

### **Phase 1: Add Installation Commands**
1. **Extend agent.yaml schema** to include `installation` section
2. **Update current system** to use installation commands
3. **Maintain backward compatibility** with existing dependencies list

### **Phase 2: Migrate to pyproject.toml**
1. **Create pyproject.toml** for each agent
2. **Move dependencies** from agent.yaml to pyproject.toml
3. **Update installation commands** to use UV standard approach

### **Phase 3: Enhanced Features**
1. **Tool dependencies** management
2. **Custom validation** commands
3. **Advanced installation** options

## 📊 **Comparison: Old vs New**

| Aspect | Old (Phase 2.5) | New (Phase 3) |
|--------|-----------------|---------------|
| **Dependencies** | Listed in agent.yaml | In pyproject.toml/requirements.txt |
| **Installation** | Single UV command | Multiple installation commands |
| **Validation** | Basic import check | Custom validation commands |
| **Flexibility** | Limited | High - any installation commands |
| **Standards** | Custom format | Python packaging standards |
| **UV Integration** | Basic | Full UV workflow support |

---

**This approach makes Phase 3 more flexible and standards-compliant while maintaining full compatibility with the current UV-based system.**
