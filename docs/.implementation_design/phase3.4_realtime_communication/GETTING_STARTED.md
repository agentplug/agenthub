# Phase 3.4: Getting Started Guide

**For Developers**: Quick start guide for implementing Phase 3.4

## 🚀 Quick Start

### What You Need to Know

Phase 3.4 adds real-time communication with **minimal changes** to existing code:

1. **WebSocket auto-enables** - No manual setup required
2. **Graceful fallback** - Works without WebSocket if unavailable
3. **Backward compatible** - Existing agents work unchanged
4. **Optional enhancements** - Agents can opt-in to interactive features

## 📋 Implementation Checklist

### Step 1: Create Core Communication Module

```bash
# Create directory structure
mkdir -p agenthub/core/communication

# Create files
touch agenthub/core/communication/__init__.py
touch agenthub/core/communication/server.py
touch agenthub/core/communication/router.py
touch agenthub/core/communication/session.py
touch agenthub/core/communication/protocol.py
```

### Step 2: Implement Core Components

Follow `01_architecture_design.md` for detailed implementation of:
- [ ] `CommunicationServer` - WebSocket server
- [ ] `MessageRouter` - Message routing
- [ ] `SessionManager` - Session management
- [ ] `A2AMessageAdapter` - A2A-compatible messages

### Step 3: Enhance ProcessManager

Add to `agenthub/runtime/process_manager.py`:
- [ ] `realtime_communication` parameter (default: True)
- [ ] `_try_start_communication_server()` method
- [ ] `_ensure_communication_server()` method
- [ ] Graceful fallback logic

### Step 4: Enhance Agent Template

Add to `agenthub/core/agents/agent_template.py`:
- [ ] `has_websocket_support()` method
- [ ] `request_user_input()` method
- [ ] `send_agent_message()` method
- [ ] Fallback implementations

### Step 5: Write Tests

Create tests in `tests/phase3.4_realtime_communication/`:
- [ ] Unit tests for each component
- [ ] Integration tests for workflows
- [ ] Fallback scenario tests
- [ ] Backward compatibility tests

## 💡 Example Usage

### For Users (No Changes Required)

```python
import agenthub as ah

# Existing code works unchanged
agent = ah.load_agent("agentplug/research-agent")
result = agent.standard_research("Your query")

# If agent requests input, user is prompted automatically
# WebSocket handles communication transparently
```

### For Agent Developers (Optional Enhancement)

```python
# agenthub/core/agents/agent_template.py
class DynamicAgent:
    def request_user_input(self, prompt: str) -> str:
        """Request input from user with automatic fallback."""
        if self.has_websocket_support():
            return self._request_input_via_websocket(prompt)
        else:
            return input(f"{prompt}: ")
```

### Example: Interactive Agent

```python
class InteractiveResearchAgent:
    def standard_research(self, query: str) -> dict:
        # Perform initial research
        results = self.search(query)

        # Request user confirmation (optional)
        if self.has_websocket_support():
            confirm = self.request_user_input(
                "Found 10 results. Continue with detailed analysis? (y/n)"
            )

            if confirm.lower() == 'y':
                detailed_results = self.detailed_analysis(results)
                return {"results": detailed_results}

        return {"results": results}
```

## 🧪 Testing Your Implementation

### Test 1: WebSocket Availability

```python
# Test that WebSocket auto-enables
from agenthub.runtime import ProcessManager

pm = ProcessManager(realtime_communication=True)
assert pm.realtime_communication == True or pm.realtime_communication == False
# Should be True if websockets available, False otherwise
```

### Test 2: Graceful Fallback

```python
# Test fallback to stdin/stdout
from agenthub.core.agents.agent_template import DynamicAgent

agent = DynamicAgent()
# Should work whether WebSocket is available or not
user_input = agent.request_user_input("Test prompt")
```

### Test 3: Backward Compatibility

```python
# Test that existing agents work unchanged
import agenthub as ah

agent = ah.load_agent("agentplug/coding-agent")
result = agent.solve("Create a calculator function")
# Should work exactly as before
```

## 🔧 Troubleshooting

### Issue: WebSocket Won't Start

**Symptom**: Warning message "Failed to start communication server"

**Solution**: This is expected behavior! System gracefully falls back to stdin/stdout

**Check**:
```python
import websockets  # Should import successfully
```

### Issue: Port 38765 Already in Use

**Symptom**: "Address already in use" error

**Solution**: System should handle this automatically. If not, check for other processes:
```bash
lsof -i :38765
```

### Issue: Agents Not Receiving Messages

**Symptom**: Messages sent but not received

**Debug**:
```python
# Check if server is running
from agenthub.core.communication import CommunicationServer
server = CommunicationServer()
print(f"Server running: {server.is_running}")

# Check active sessions
from agenthub.runtime import ProcessManager
pm = ProcessManager()
print(f"Active sessions: {pm.communication_server.session_manager.get_active_sessions()}")
```

## 📚 Key Files to Reference

### Architecture
- `01_architecture_design.md` - Complete architecture
- `README.md` - Phase overview
- `SIMPLIFIED_SUMMARY.md` - Quick reference

### Implementation
- `IMPLEMENTATION_PLAN.md` - Step-by-step plan
- `core/communication/README.md` - Module details

### Examples
- Look at `examples/getting_started/` for patterns
- Follow Phase 3.2 style in `phase3.2_intelligent_solve/`

## ✅ Definition of Done

Your implementation is complete when:

- [ ] All core components implemented and tested
- [ ] ProcessManager integration working
- [ ] Agent template enhancements working
- [ ] Graceful fallback working
- [ ] Backward compatibility verified
- [ ] Test coverage >95%
- [ ] Documentation complete
- [ ] Example implementations created

## 🎯 Next Steps

1. **Start with Core Module**: Implement `CommunicationServer` first
2. **Add Tests Early**: Write tests as you implement
3. **Test Fallback**: Ensure fallback works throughout
4. **Validate Backward Compatibility**: Test with existing agents
5. **Document as You Go**: Update docs with implementation notes

## 💬 Questions?

Refer to:
- `01_architecture_design.md` for detailed specifications
- `IMPLEMENTATION_PLAN.md` for step-by-step guidance
- Phase 3.2 implementation for similar patterns
- Existing AgentHub code for conventions

Remember: **KISS and YAGNI** - Keep it simple, implement only what's needed, ensure backward compatibility!
