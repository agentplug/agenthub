# Creating an AgentHub-Compatible Agent

An AgentHub-compatible agent is a GitHub repository with three required files: `agent.yaml`, `agent.py`, and `pyproject.toml`. See [agentplug/coding-agent](https://github.com/agentplug/coding-agent) as a real example.

## Required File Structure

```
my-agent/
├── agent.yaml        # Agent manifest (required)
├── agent.py          # Agent implementation (required)
├── pyproject.toml    # Python package + dependencies (required)
└── llm_service.py    # LLM helper (optional, copy from coding-agent)
```

## 1. `agent.yaml` — The Manifest

Defines metadata, installation commands, and the public interface:

```yaml
name: "my-agent"
version: "1.0.0"
description: "What your agent does"
author: "your-username"
license: "MIT"
python_version: "3.11+"

installation:
  commands:
    - "python -m ensurepip --upgrade"
    - "python -m pip install --upgrade pip"
    - "pip install uv"
    - "uv venv .venv"
    - "uv pip install -e ."
    - "uv sync"
  description: "Install dependencies using uv"

interface:
  methods:
    do_something:
      description: "What this method does"
      parameters:
        input:
          type: "string"
          description: "The input text"
          required: true
      returns:
        type: "string"
        description: "The result"

tags: ["your-tag"]
```

## 2. `agent.py` — The Implementation

The class methods must match the `interface.methods` defined in `agent.yaml`. AgentHub calls the agent via a `main()` function that reads JSON from `sys.argv[1]` and writes JSON to stdout:

```python
import json
import sys

class MyAgent:
    def __init__(self):
        pass  # initialize any services here

    def do_something(self, input: str) -> str:
        """What this method does."""
        return f"Result for: {input}"


def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Invalid arguments"}))
        sys.exit(1)

    try:
        input_data = json.loads(sys.argv[1])
        method = input_data.get("method")
        parameters = input_data.get("parameters", {})

        agent = MyAgent()

        if method == "do_something":
            result = agent.do_something(parameters.get("input", ""))
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

**Key rules:**
- Method names and parameter names must exactly match `agent.yaml`
- Return a plain string or JSON-serializable value
- The `main()` input format is `{"method": "method_name", "parameters": {...}}`
- Always output `{"result": ...}` on success or `{"error": ...}` on failure

## 3. `pyproject.toml` — Dependencies

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-agent"
version = "1.0.0"
description = "What your agent does"
authors = [{ name = "your-username" }]
requires-python = ">=3.11"
dependencies = [
    "aisuite[openai]>=0.1.7",
    # add your dependencies here
]

[project.scripts]
my-agent = "agent:main"

[tool.setuptools.package-data]
"*" = ["*.yaml", "*.yml", "*.json"]
```

## 4. Publish and Use

```bash
# Push to GitHub
git init && git add . && git commit -m "Initial release"
git remote add origin https://github.com/your-username/my-agent.git
git push -u origin main
```

```python
# Anyone can now load your agent
import agenthub as ah
agent = ah.load_agent("your-username/my-agent")
result = agent.do_something("hello")
print(result["result"])
```
