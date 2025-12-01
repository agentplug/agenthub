# Phase 3.4: Real-time Communication Implementation Design

**Document Type**: Phase Implementation Design
**Author**: AI Assistant
**Date Created**: 2025-01-02
**Last Updated**: 2025-01-02
**Status**: Design Phase
**Purpose**: Implementation design for real-time communication between users and agents, with A2A-compatible agent-to-agent messaging

## 🎯 **Phase 3.4 Overview**

Phase 3.4 introduces **real-time communication capabilities** that allow users to interact with agents in real-time and enable agents to communicate with each other using an A2A-compatible message structure.

### **Key Features**
- **User-Agent Interactive Communication**: Users can provide input when agents request it
- **Agent-Agent Message Passing**: Agents can communicate using A2A-compatible message format
- **WebSocket Core Infrastructure**: Single shared WebSocket server for all communication
- **Auto-Enable with Graceful Fallback**: Automatically enabled, falls back to stdin/stdout if unavailable
- **Backward Compatible**: Existing agents work unchanged
- **Future-Ready**: Designed to be foundation for future monitoring system

### **User Experience**
```python
import agenthub as ah

# Load agent - WebSocket enabled by default
agent = ah.load_agent("agentplug/research-agent")

# Agent can request user input during execution
result = agent.standard_research("Your query")
# If agent needs clarification, user is prompted automatically:
# "Agent: Please specify the date range (y/n)?"
# User: "2020-2024"
# Execution continues with user input...

# Agents can communicate with each other (A2A-compatible)
research_agent = ah.load_agent("agentplug/research-agent")
analysis_agent = ah.load_agent("agentplug/analysis-agent")
# Research agent can request analysis from analysis agent automatically
```

## 📁 **Module Structure**

### **core/communication/**
- **Purpose**: Core WebSocket communication infrastructure
- **Key Features**: WebSocket server, message routing, A2A-compatible protocol
- **Files**: README.md, 01_architecture_design.md, 02_implementation_details.md, 03_testing_strategy.md

### **core/agents/**
- **Purpose**: Enhanced agent template with interactive capabilities
- **Key Features**: User input helpers, agent-to-agent messaging, graceful fallback
- **Files**: README.md, 01_interface_design.md, 02_implementation_details.md

### **runtime/**
- **Purpose**: ProcessManager integration with WebSocket
- **Key Features**: Automatic WebSocket management, session handling
- **Files**: README.md, 01_implementation_details.md, 02_testing_strategy.md

### **testing/**
- **Purpose**: Comprehensive testing for Phase 3.4
- **Key Features**: Unit tests, integration tests, fallback tests
- **Files**: README.md, communication_testing.md, integration_testing.md

## 🔄 **Communication Flow**

### **User-Agent Interaction**
1. **Agent Request**: Agent needs user input during execution
2. **WebSocket Broadcast**: Request sent via WebSocket to connected clients
3. **User Response**: User provides input through CLI/interface
4. **Input Forwarded**: Response sent back to agent via WebSocket
5. **Execution Continues**: Agent continues with user input

### **Agent-Agent Communication**
1. **Message Creation**: Agent creates A2A-compatible message
2. **Server Routing**: WebSocket server routes message to target agent
3. **Message Delivery**: Target agent receives message
4. **Response (Optional)**: Target agent can respond if needed

## 🎯 **Success Criteria**

- ✅ User-agent interaction works seamlessly
- ✅ Agent-agent message passing works
- ✅ WebSocket auto-enables without user intervention
- ✅ Graceful fallback to stdin/stdout works
- ✅ Backward compatibility maintained (existing agents unchanged)
- ✅ A2A-compatible message structure
- ✅ Performance overhead <10% per execution
- ✅ Single shared WebSocket server (port 38765 - IANA unassigned range)

## 🏗️ **Architecture Overview**

### **Core Components**
- **CommunicationServer**: Single shared WebSocket server for all agents
- **MessageRouter**: Routes messages between users, agents, and services
- **SessionManager**: Manages active agent sessions and connections
- **A2AMessageAdapter**: Converts between AgentHub and A2A message formats

### **Integration Points**
- **ProcessManager**: Uses CommunicationServer for real-time communication
- **DynamicAgent**: Optional helper methods for interactive capabilities
- **AgentRuntime**: Automatic WebSocket lifecycle management

## 🔗 **Dependencies**

- **Phase 1**: Foundation (runtime, storage, core, CLI)
- **Phase 2**: Auto-install (registry, cache, installer)
- **Phase 2.5**: Tool injection (MCP, tool management)
- **Phase 3**: SDK integration (enhanced load_agent)
- **Phase 3.2**: Intelligent solve() (optional integration)
- **websockets**: WebSocket library for Python
- **A2A Protocol**: Compatible message structure (not full SDK dependency)

## 📊 **Progress Tracking**

- [ ] core/communication module complete
- [ ] core/agents enhancements complete
- [ ] runtime integration complete
- [ ] testing module complete
- [ ] Phase 3.4 testing complete
- [ ] Documentation complete

## 🚀 **Future Extensibility**

Phase 3.4 is designed to be extensible for future enhancements:

- **Phase 4.x**: Full A2A protocol implementation with official SDK
- **Phase 4.x**: Cross-machine agent communication
- **Phase 4.x**: Real-time chat interface between users and agents
- **Phase 4.x**: WebSocket-based monitoring system (replacing current monitoring)
- **Phase 4.x**: Web dashboard for real-time visualization

This phase enables real-time communication while maintaining simplicity and backward compatibility.
