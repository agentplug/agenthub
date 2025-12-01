# Phase 3.4: Real-time Communication - Simplified Summary

**TL;DR**: Enable real-time communication between users and agents, plus A2A-compatible agent-to-agent messaging, with automatic WebSocket integration and graceful fallback.

## 🎯 What We're Building

### Primary Goal: User ↔ Agent Interaction
```python
# Agent can request user input during execution
result = agent.standard_research("Your query")
# Agent: "Please specify date range:"
# User: "2020-2024"
# Agent continues with user input...
```

### Secondary Goal: Agent ↔ Agent Communication
```python
# Agents can communicate using A2A-compatible messages
research_agent.send_message(analysis_agent, "analyze_content", data)
```

## 🏗️ What Changes

### New: Core Communication Module
```
agenthub/core/communication/
├── server.py          # Single WebSocket server
├── router.py          # Message routing
├── session.py         # Session management
└── protocol.py        # A2A-compatible format
```

### Enhanced: ProcessManager
- Automatically starts WebSocket server
- Manages communication lifecycle
- Graceful fallback if WebSocket fails

### Enhanced: DynamicAgent Template
- `has_websocket_support()` - Check if WebSocket available
- `request_user_input()` - Request input from user
- `send_agent_message()` - Send message to another agent

### What Doesn't Change
- **Existing agents work unchanged**
- **No breaking changes**
- **All current features preserved**

## 🔧 How It Works

### Architecture
```
┌──────────────────────────────────────────────────┐
│    Single WebSocket Server (port 38765)          │
│    [IANA unassigned range - no conflicts]        │
│                                                   │
│  ┌───────────────────────────────────────────┐   │
│  │         Message Router                     │   │
│  │  • User ↔ Agent                           │   │
│  │  • Agent ↔ Agent (A2A-compatible)         │   │
│  └───────────────────────────────────────────┘   │
└───────────────────────────────────────────────────┘
          ↓              ↓              ↓
    Agent 1         Agent 2        Agent 3
```

### Graceful Fallback
```python
# If WebSocket available:
user_input = self.request_user_input("Prompt")  # Via WebSocket

# If WebSocket unavailable:
user_input = input("Prompt: ")  # Falls back to stdin
```

## 📊 Key Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Port Management | **Single shared port (38765)** | Simpler, agents can discover each other |
| Priority | **User-Agent first, Agent-Agent second** | User interaction is primary use case |
| Agent Changes | **Optional helpers, backward compatible** | No breaking changes |
| Monitoring | **Separate from existing monitoring** | Foundation for future Phase 4.x |
| A2A Protocol | **Compatible structure, not full SDK** | KISS principle, extensible later |
| Auto-Enable | **Yes, with graceful fallback** | Best UX, reliable |

## 🚀 Implementation Phases

### Phase 1: Core Infrastructure (Week 1-2)
- WebSocket server
- Message routing
- Session management
- ProcessManager integration

### Phase 2: Agent Enhancement (Week 3-4)
- Agent template helpers
- User-agent interaction
- Agent-agent messaging
- Fallback mechanisms

### Phase 3: Testing & Documentation (Week 5-6)
- Unit tests
- Integration tests
- Documentation
- Examples

## ✅ Success Criteria (Simple)

- ✅ Agent can request user input → User provides → Agent continues
- ✅ Agent can send message to another agent
- ✅ WebSocket starts automatically
- ✅ Falls back to stdin/stdout if WebSocket fails
- ✅ Existing agents work without changes
- ✅ Performance overhead <10%

## 🎯 What Users See

### Before Phase 3.4
```python
agent = ah.load_agent("agentplug/research-agent")
result = agent.standard_research("query")
# No real-time interaction possible
```

### After Phase 3.4
```python
agent = ah.load_agent("agentplug/research-agent")
result = agent.standard_research("query")
# Agent can request input: "Please confirm (y/n)?"
# User responds: "y"
# Agent continues with confirmation
```

### Agent Implementation (Optional)
```python
class MyAgent:
    def my_method(self, query):
        # Optional: Use new helpers
        if self.has_websocket_support():
            user_input = self.request_user_input("Need clarification:")
        else:
            user_input = input("Need clarification: ")

        return f"Processed with: {user_input}"
```

## 🔒 What We're NOT Building

- ❌ Web dashboard (future)
- ❌ CLI changes (not needed)
- ❌ Cross-machine communication (future)
- ❌ Real-time chat (future)
- ❌ Full A2A protocol (future)
- ❌ Authentication (localhost only)

## 🚀 Future Extensibility

Phase 3.4 provides foundation for:
- **Phase 4.x**: Full A2A protocol with official SDK
- **Phase 4.x**: Cross-machine agent communication
- **Phase 4.x**: Real-time chat interface
- **Phase 4.x**: WebSocket-based monitoring system (replacing current)

## 📝 Bottom Line

**For Users**: Agents can now interact with you in real-time
**For Developers**: Simple APIs, backward compatible, graceful fallback
**For System**: Minimal overhead, auto-enabled, reliable
**For Future**: Foundation for advanced features

**KISS**: Single WebSocket server, simple message format
**YAGNI**: Only what's needed now, extensible for future
**Backward Compatible**: Existing code works unchanged
