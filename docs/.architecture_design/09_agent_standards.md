# Agent Standards and GitHub Registry Specification

**Document Type**: Technical Specification  
**Author**: William  
**Date Created**: 2025-06-28  
**Last Updated**: 2025-06-28  
**Status**: Draft  
**Focus**: Agent interface standards and simplified GitHub-based registry  

## Agent Interface Standards

### Standard Agent Structure

```
my-agent/
├── agent.yaml                 # Agent manifest (required)
├── agent.py                   # Main agent entry point (required)
├── requirements.txt           # Dependencies (required)
├── README.md                  # Documentation (required)
├── src/                       # Agent implementation
│   ├── __init__.py
│   ├── core.py
│   └── utils.py
├── tests/                     # Unit tests
│   ├── test_agent.py
│   └── test_core.py
└── examples/                  # Usage examples
    └── basic_usage.py
```

### Standard Agent Manifest (agent.yaml)

```yaml
# agent.yaml - Standard agent manifest
name: "coding-agent"
version: "1.0.0"
description: "AI coding assistant for Python development"
author: "meta"
license: "MIT"
homepage: "https://github.com/meta/coding-agent"
repository: "https://github.com/meta/coding-agent"

# Agent interface definition
interface:
  methods:
    generate_code:
      description: "Generate Python code from natural language description"
      parameters:
        prompt:
          type: "string"
          required: true
          description: "Natural language description of the code to generate"
        style:
          type: "string" 
          required: false
          default: "clean"
          options: ["clean", "verbose", "minimal"]
      returns:
        type: "string"
        description: "Generated Python code"
      
    debug_code:
      description: "Debug and fix Python code"
      parameters:
        code:
          type: "string"
          required: true
          description: "Python code to debug"
        explain:
          type: "boolean"
          required: false
          default: true
      returns:
        type: "object"
        description: "Fixed code and explanation"
        properties:
          fixed_code: {type: "string"}
          explanation: {type: "string"}
          issues_found: {type: "array"}

# Dependencies
dependencies:
  python: ">=3.8"
  runtime:
    - "openai>=1.0.0"
    - "tiktoken>=0.5.0"
    - "ast-tools>=0.2.0"

# Metadata
tags: ["coding", "python", "ai", "development", "debugging"]
category: "development"
keywords: ["code generation", "debugging", "python", "AI assistant"]

# Publishing info
published_at: "2025-06-28T10:00:00Z"
download_url: "https://github.com/meta/coding-agent/archive/v1.0.0.tar.gz"
size_mb: 2.5
```

### Standard Agent Implementation

```python
# agent.py - Standard agent entry point
import sys
import json
import yaml
from typing import Dict, Any
from src.core import CodingAssistant

class CodingAgent:
    def __init__(self):
        """Initialize agent with manifest"""
        self.manifest = self.load_manifest()
        self.assistant = CodingAssistant()
    
    def load_manifest(self) -> Dict[str, Any]:
        """Load agent manifest"""
        with open("agent.yaml", 'r') as f:
            return yaml.safe_load(f)
    
    def generate_code(self, prompt: str, style: str = "clean") -> str:
        """Generate Python code from description"""
        return self.assistant.generate_code(prompt, style)
    
    def debug_code(self, code: str, explain: bool = True) -> Dict[str, Any]:
        """Debug and fix Python code"""
        return self.assistant.debug_code(code, explain)
    
    def get_interface(self) -> Dict[str, Any]:
        """Return agent interface definition"""
        return self.manifest.get("interface", {})

def main():
    """Main entry point for subprocess execution"""
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python agent.py '<json_input>'"}))
        sys.exit(1)
    
    try:
        # Parse input
        input_data = json.loads(sys.argv[1])
        method_name = input_data["method"]
        parameters = input_data.get("parameters", {})
        
        # Create agent instance
        agent = CodingAgent()
        
        # Execute method
        if hasattr(agent, method_name):
            method = getattr(agent, method_name)
            result = method(**parameters)
            
            # Return success result
            print(json.dumps({
                "success": True,
                "result": result,
                "agent": agent.manifest["name"],
                "version": agent.manifest["version"]
            }))
        else:
            # Method not found
            available_methods = list(agent.get_interface().get("methods", {}).keys())
            print(json.dumps({
                "success": False,
                "error": f"Method '{method_name}' not found",
                "available_methods": available_methods
            }))
            
    except Exception as e:
        # Error handling
        print(json.dumps({
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## GitHub-Based Registry System

### Registry Repository Structure

```
agentplug/agent-registry/
├── registry.json              # Main registry index
├── agents/                    # Agent metadata files
│   ├── meta/
│   │   └── coding-agent.json
│   ├── openai/
│   │   └── data-analyzer.json
│   └── user/
│       └── custom-agent.json
├── categories/                # Category indexes
│   ├── development.json
│   ├── data-science.json
│   └── automation.json
└── README.md                  # Registry documentation
```

### Registry Index Format (registry.json)

```json
{
  "version": "1.0.0",
  "updated_at": "2025-06-28T10:00:00Z",
  "total_agents": 156,
  "categories": [
    "development", "data-science", "automation", 
    "content", "analysis", "utilities"
  ],
  "featured_agents": [
    "meta/coding-agent",
    "openai/data-analyzer", 
    "anthropic/writing-assistant"
  ],
  "trending_agents": [
    "user/automation-helper",
    "meta/code-reviewer",
    "openai/text-summarizer"
  ],
  "agents": {
    "meta/coding-agent": {
      "name": "coding-agent",
      "version": "1.0.0",
      "author": "meta",
      "description": "AI coding assistant for Python development",
      "category": "development",
      "tags": ["coding", "python", "ai", "development"],
      "download_url": "https://github.com/meta/coding-agent/archive/v1.0.0.tar.gz",
      "homepage": "https://github.com/meta/coding-agent",
      "published_at": "2025-06-28T10:00:00Z",
      "downloads": 1250,
      "rating": 4.8,
      "size_mb": 2.5,
      "python_version": ">=3.8",
      "verified": true
    },
    "openai/data-analyzer": {
      "name": "data-analyzer",
      "version": "2.1.0",
      "author": "openai",
      "description": "Advanced data analysis and visualization agent",
      "category": "data-science",
      "tags": ["data", "analysis", "visualization", "pandas"],
      "download_url": "https://github.com/openai/data-analyzer/archive/v2.1.0.tar.gz",
      "homepage": "https://github.com/openai/data-analyzer",
      "published_at": "2025-06-25T14:30:00Z",
      "downloads": 890,
      "rating": 4.6,
      "size_mb": 8.2,
      "python_version": ">=3.9",
      "verified": true
    }
  }
}
```

### Publishing Workflow

#### 1. Developer Creates Agent Package
```bash
# Initialize agent template
agenthub init my-awesome-agent

# Develop agent
cd my-awesome-agent
# ... implement agent logic ...

# Validate agent
agenthub validate .

# Package agent
agenthub package .
```

#### 2. Automated Publishing Process
```bash
# Create GitHub release
git tag v1.0.0
git push origin v1.0.0

# Agent Hub automatically:
# 1. Detects new release
# 2. Downloads and validates agent
# 3. Updates registry.json
# 4. Creates pull request to registry repo
```

#### 3. Manual Publishing (MVP)
```bash
# Developer submits PR to registry
# 1. Fork agentplug/agent-registry
# 2. Add agent metadata to registry.json
# 3. Submit pull request
# 4. Maintainers review and merge
```

## Improved Error Handling

### User-Friendly Error Messages

```python
class AgentHubError(Exception):
    def __init__(self, message: str, solution: str = None, docs_link: str = None):
        self.message = message
        self.solution = solution  
        self.docs_link = docs_link
        super().__init__(message)
    
    def display(self):
        """Display formatted error message"""
        print(f"❌ Error: {self.message}")
        if self.solution:
            print(f"💡 Solution: {self.solution}")
        if self.docs_link:
            print(f"📖 Help: {self.docs_link}")

# Specific error types
class AgentNotFoundError(AgentHubError):
    def __init__(self, agent_path: str, suggestions: List[str] = None):
        message = f"Agent '{agent_path}' not found"
        solution = None
        if suggestions:
            suggestion_list = "\n   - ".join(suggestions[:3])
            solution = f"Did you mean:\n   - {suggestion_list}\n\n🔍 Try: agenthub search {agent_path.split('/')[-1]}"
        else:
            solution = f"Try: agenthub search {agent_path.split('/')[-1]}"
        
        super().__init__(
            message=message,
            solution=solution,
            docs_link="https://docs.agenthub.ai/troubleshooting#agent-not-found"
        )

class DependencyInstallError(AgentHubError):
    def __init__(self, package: str, error_details: str):
        message = f"Failed to install dependency '{package}'"
        solution = f"Try:\n  1. Check internet connection\n  2. uv pip install {package}\n  3. Contact agent author if issue persists"
        
        super().__init__(
            message=message,
            solution=solution,
            docs_link="https://docs.agenthub.ai/troubleshooting#dependency-errors"
        )
```

### CLI Error Display

```bash
# Example error output
$ agenthub install meta/coding-agnt
❌ Error: Agent 'meta/coding-agnt' not found
💡 Solution: Did you mean:
   - meta/coding-agent
   - meta/coding-assistant  
   - openai/coding-helper

🔍 Try: agenthub search coding
📖 Help: https://docs.agenthub.ai/troubleshooting#agent-not-found

# Recovery suggestions
$ agenthub install meta/coding-agent --fix-name
✅ Found similar agent: meta/coding-agent
🔄 Installing meta/coding-agent instead...
```

## Agent Template System

### Template Generator

```python
class AgentTemplate:
    def __init__(self, agent_name: str, category: str = "general"):
        self.agent_name = agent_name
        self.category = category
    
    def generate_template(self, output_dir: str):
        """Generate complete agent template"""
        templates = {
            "agent.yaml": self.generate_manifest(),
            "agent.py": self.generate_main_script(),
            "requirements.txt": self.generate_requirements(),
            "README.md": self.generate_readme(),
            "src/__init__.py": "",
            "src/core.py": self.generate_core_logic(),
            "tests/test_agent.py": self.generate_tests(),
            "examples/basic_usage.py": self.generate_examples()
        }
        
        for file_path, content in templates.items():
            full_path = os.path.join(output_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
```

### Category-Specific Templates

```python
AGENT_TEMPLATES = {
    "development": {
        "methods": ["generate_code", "review_code", "debug_code"],
        "dependencies": ["openai", "ast-tools", "black"],
        "description": "Development and coding assistance agent"
    },
    "data-science": {
        "methods": ["analyze_data", "visualize_data", "generate_insights"],
        "dependencies": ["pandas", "matplotlib", "seaborn", "scipy"],
        "description": "Data analysis and visualization agent"
    },
    "content": {
        "methods": ["generate_text", "edit_content", "summarize_text"],
        "dependencies": ["openai", "nltk", "transformers"],
        "description": "Content generation and editing agent"
    }
}
```

## Analytics and Discovery

### Simple Usage Analytics

```python
class SimpleAnalytics:
    def __init__(self):
        self.analytics_file = "~/.agenthub/analytics.json"
    
    def track_agent_usage(self, agent_path: str, method: str):
        """Track agent usage for discovery"""
        data = self.load_analytics()
        
        # Update usage stats
        if agent_path not in data["usage"]:
            data["usage"][agent_path] = {"total_calls": 0, "methods": {}}
        
        data["usage"][agent_path]["total_calls"] += 1
        data["usage"][agent_path]["methods"][method] = \
            data["usage"][agent_path]["methods"].get(method, 0) + 1
        data["usage"][agent_path]["last_used"] = time.time()
        
        self.save_analytics(data)
    
    def get_recommendations(self) -> List[str]:
        """Get agent recommendations based on usage patterns"""
        data = self.load_analytics()
        
        # Simple recommendation based on popularity
        popular_agents = sorted(
            data["usage"].items(),
            key=lambda x: x[1]["total_calls"],
            reverse=True
        )
        
        return [agent for agent, _ in popular_agents[:5]]
```

### Enhanced Discovery Commands

```bash
# Enhanced discovery
agenthub trending                    # Show trending agents
agenthub search coding --category development
agenthub recommend                   # Personal recommendations
agenthub agents --by-downloads       # Most downloaded
agenthub agents --by-rating          # Highest rated
```

This improved specification provides:
1. **Clear agent standards** for consistent development
2. **Simple GitHub-based registry** for zero-maintenance hosting
3. **Better error handling** with actionable solutions
4. **Template system** for faster agent development
5. **Enhanced discovery** for better user experience

The approach is much more practical for an MVP while maintaining extensibility for future enhancements.
