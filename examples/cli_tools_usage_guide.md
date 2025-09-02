# AgentHub CLI Tools Management Guide

This guide demonstrates how to use the new CLI tool management commands in AgentHub.

## Overview

The CLI tools management system provides commands to start, stop, and manage the tool registry service. The service runs as a persistent background process that can be accessed by multiple agents.

## Available Commands

### `agenthub tools start`
Start the tool registry service.

```bash
# Start service on default port (8000)
agenthub tools start

# Start service on custom port
agenthub tools start --port 8001

# Start service with custom host
agenthub tools start --host 0.0.0.0 --port 8000

# Start service with debug logging
agenthub tools start --log-level debug
```

### `agenthub tools stop`
Stop the tool registry service.

```bash
# Stop service on default port
agenthub tools stop

# Stop service on custom port
agenthub tools stop --port 8001
```

### `agenthub tools status`
Check the status of the tool registry service.

```bash
# Check status on default port
agenthub tools status

# Check status on custom port
agenthub tools status --port 8001

# Get status in JSON format
agenthub tools status --json
```

### `agenthub tools list`
List all registered tools.

```bash
# List tools on default port
agenthub tools list

# List tools on custom port
agenthub tools list --port 8001

# Get list in JSON format
agenthub tools list --json
```

### `agenthub tools info`
Get detailed information about a specific tool.

```bash
# Get tool info
agenthub tools info my_tool

# Get tool info on custom port
agenthub tools info my_tool --port 8001

# Get info in JSON format
agenthub tools info my_tool --json
```

### `agenthub tools restart`
Restart the tool registry service.

```bash
# Restart service on default port
agenthub tools restart

# Restart service on custom port
agenthub tools restart --port 8001
```

### `agenthub tools unregister`
Unregister a tool from the registry.

```bash
# Unregister a tool
agenthub tools unregister my_tool

# Force unregister without confirmation
agenthub tools unregister my_tool --force
```

## Usage Patterns

### Pattern 1: Development Workflow

1. Start the service in one terminal:
   ```bash
   agenthub tools start --port 8000
   ```

2. In another terminal, register and use tools:
   ```bash
   # Check service status
   agenthub tools status
   
   # List registered tools
   agenthub tools list
   
   # Run your agent code that uses tools
   python my_agent.py
   ```

3. Stop the service when done:
   ```bash
   agenthub tools stop
   ```

### Pattern 2: Production Deployment

1. Start the service as a background process:
   ```bash
   nohup agenthub tools start --port 8000 > tool_service.log 2>&1 &
   ```

2. Monitor the service:
   ```bash
   agenthub tools status
   ```

3. Stop the service:
   ```bash
   agenthub tools stop
   ```

### Pattern 3: Testing and Development

1. Start service for testing:
   ```bash
   agenthub tools start --port 8001 --log-level debug
   ```

2. Run tests that use tools:
   ```bash
   python -m pytest tests/
   ```

3. Check tool status during testing:
   ```bash
   agenthub tools list --port 8001
   ```

## Service Architecture

The tool registry service provides:

- **HTTP REST API** for tool interaction
- **Health monitoring** via `/health` endpoint
- **Tool discovery** via `/tools/` endpoint
- **Tool execution** via `/tools/{name}/execute` endpoint
- **Concurrent execution** support for multiple agents

## Integration with Agents

Agents can connect to the tool service using HTTP requests:

```python
import requests

# Check if service is running
response = requests.get("http://127.0.0.1:8000/health")
if response.status_code == 200:
    print("Tool service is running")

# List available tools
response = requests.get("http://127.0.0.1:8000/tools/")
tools = response.json()["tools"]

# Execute a tool
response = requests.post(
    "http://127.0.0.1:8000/tools/my_tool/execute",
    json={"parameters": {"input": "test"}}
)
result = response.json()
```

## Troubleshooting

### Service Won't Start
- Check if port is already in use: `lsof -i :8000`
- Try a different port: `agenthub tools start --port 8001`
- Check logs for errors

### Service Not Accessible
- Verify service is running: `agenthub tools status`
- Check firewall settings
- Ensure correct host/port configuration

### Tools Not Registered
- Use `@tool` decorator in your code
- Manually register tools using the registration API
- Check tool registration with `agenthub tools list`

## Next Steps

The CLI tools management system is now ready for use. The next phase will add:

- **Persistent storage** for tool metadata
- **Auto-recovery** mechanism for service restarts
- **Advanced monitoring** and logging features
- **Service discovery** and load balancing
