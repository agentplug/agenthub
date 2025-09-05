# Phase 2.5 Real MCP Tool Integration - Implementation Plan

## Overview
This document provides the detailed step-by-step implementation plan for Phase 2.5: **Real MCP Tool Integration** using the **official MCP Python SDK** from [https://github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk). The plan is divided into 4 sequential steps, each designed to be testable end-to-end before proceeding to the next.

## Core Principle: End-to-End Validation After Each Phase
**Critical**: After each implementation phase, a comprehensive end-to-end test must be completed to validate the work and prevent redundant effort. This ensures that:
- Each phase delivers working functionality
- Integration issues are caught early
- No time is wasted on building upon broken foundations
- Progress is measurable and validated

## Architecture: Real MCP Tool Registry with Official SDK Integration
**Design Decision**: The tool registry will use **real MCP protocol** via the **official MCP Python SDK** while supporting automatic tool registration through decorators. This provides:

### Benefits:
- **Production Ready**: Persistent **real MCP service** independent of agent sessions using official SDK
- **Developer Friendly**: Tools auto-register with `@tool` decorator and become **real MCP tools**
- **Built-in + External Tools**: Supports **both built-in tools AND external tools** (populated through `amg.load_agent(tools=[])`)
- **Operations Control**: CLI management for production environments with **real MCP protocol**
- **Fault Tolerant**: Auto-recovery when **real MCP service** restarts
- **Scalable**: Multiple agents can use the same **real MCP tool service** via official SDK

### Architecture Flow:
```
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐
│    CLI      │───▶│ Real MCP Server  │◀───│   Agents    │
│ (Management)│    │ (Official SDK)   │    │ (MCP Clients)│
└─────────────┘    └──────────────────┘    └─────────────┘
       │                   │                   │
       │                   │                   │
   Start/Stop          Auto-Recovery        HTTP API
   List/Status         @tool decorators     Tool Calls
   Unregister          Manual registration
```

### CLI Commands:
- `agenthub tools start` - Start persistent tool registry service
- `agenthub tools stop` - Stop tool registry service  
- `agenthub tools status` - Check service status
- `agenthub tools list` - List registered tools
- `agenthub tools unregister <name>` - Remove specific tool
- `agenthub tools restart` - Reload auto-registered tools

## Implementation Timeline: 5 Weeks

### Step 1: Modular Core Architecture and Tool System (Week 1-2)
**Goal**: Refactor core into modular architecture and build the foundational decorator-based tool system with CLI management and auto-recovery

#### Deliverables
- **Modular Core Architecture** (`agentmanager/core/`)
  - `agents/` package: Agent lifecycle management components
  - `tools/` package: Tool registration, validation, security, and execution
  - `runtime/` package: Runtime management and component coordination
  - `common/` package: Shared utilities, types, and exceptions
  
- **Tool Decorator System** (`agentmanager/core/tools/decorators.py`)
  - `@tool` decorator for automatic tool registration
  - `@register_tool` decorator for manual registration
  - Tool metadata extraction and validation
  
- **Tool Registration System** (`agentmanager/core/tools/registry.py`)
  - Handles explicit tool registration by users
  - Manages tool metadata and validation
  - Coordinates tool registration with framework
  - Auto-recovery mechanism for service restarts

- **Agent-Tools Tracker** (`agentmanager/core/tools/agent_tools_tracker.py`)
  - Tracks which tools are assigned to which agents
  - Provides bidirectional lookup (agent → tools, tool → agents)
  - Manages usage statistics and monitoring
  - Integrates with CLI and runtime systems

- **Tool Service Hosting** (`agentmanager/core/tools/service.py`)
  - Hosts registered tools as HTTP/GRPC services
  - Creates API endpoints for each registered function
  - Manages tool service lifecycle
  - Persistent service mode with CLI management

- **CLI Tool Management** (`agentmanager/cli/commands/tools.py`)
  - `agenthub tools start` - Start persistent tool registry service
  - `agenthub tools stop` - Stop tool registry service
  - `agenthub tools status` - Check service status
  - `agenthub tools list` - List registered tools
  - `agenthub tools unregister <name>` - Remove specific tool
  - `agenthub tools restart` - Reload auto-registered tools
  - `agenthub tools tracker` - Show agent-tools tracker status
  - `agenthub tools assign <agent> <tools>` - Assign tools to agent
  - `agenthub tools agent <agent>` - Show agent's assigned tools
  - `agenthub tools stats` - Show tool usage statistics

#### Implementation Order
1. **Modular Architecture Setup**
   - Create modular directory structure (`agents/`, `tools/`, `runtime/`, `common/`)
   - Move existing files to appropriate packages
   - Update package `__init__.py` files
   - Create new common components (exceptions, types, utils)

2. **Tool System Implementation**
   - Create tool decorator system with metadata extraction
   - Implement explicit tool registration system with auto-recovery
   - Build persistent tool service hosting with CLI management
   - Add tool validation and security checks
   - **Implement Agent-Tools Tracker** with full functionality

3. **CLI Integration**
   - Add CLI commands for tool registry management
   - Create integration with user code execution
   - Implement auto-recovery mechanisms

4. **Migration and Testing**
   - Update all import statements throughout codebase
   - Update tests to work with new modular structure
   - Validate backward compatibility

#### Success Criteria
- **Modular Architecture**: Core components are properly organized into logical packages
- **Backward Compatibility**: All existing functionality preserved with new modular structure
- **Tool System**: Decorators can register tools when user code runs
- **CLI Management**: CLI can manage tool registry service lifecycle
- **Persistence**: Tool services persist independently of agent sessions
- **Auto-Recovery**: Auto-recovery works when service restarts
- **Testing**: All tests pass with new modular structure

#### End-to-End Test After Step 1
**Test Name**: `test_cli_managed_tool_registry_e2e`
**Purpose**: Validate CLI-managed tool registry with auto-recovery
**Test Steps**:
1. Start tool registry service via CLI (`agenthub tools start`)
2. Create a test tool with `@tool` decorator
3. Register the tool using `register_tools([test_tool])`
4. Verify tool is accessible via CLI (`agenthub tools list`)
5. Verify tool is hosted as HTTP service
6. Make API call to tool endpoint
7. Test CLI management (`agenthub tools status`, `agenthub tools unregister`)
8. Simulate service restart and verify auto-recovery
9. Verify tool executes correctly and returns expected result
10. Stop service via CLI (`agenthub tools stop`)

**Validation Criteria**:
- ✅ CLI can start/stop tool registry service
- ✅ Tool registration completes without errors
- ✅ CLI management commands work correctly
- ✅ Tool service starts and responds to health checks
- ✅ Tool API endpoint returns correct response
- ✅ Auto-recovery restores tools after service restart
- ✅ Tool metadata is accessible via API
- ✅ Service persists independently of agent sessions
- ✅ No memory leaks or resource issues

**Blocking Criteria**: If CLI management or auto-recovery fails, Step 2 cannot begin until issues are resolved.

---

### Step 2: Tool API Generation and Management (Week 2-3)
**Goal**: Generate API endpoints for registered functions, manage tool communication, and implement agent-tools tracking

#### Deliverables
- **Auto-API Generator** (`agentmanager/core/auto_api_generator.py`)
  - RESTful API endpoint generation
  - Parameter validation and error handling
  - Automatic API documentation

- **Tool Communication Layer** (`agentmanager/core/tool_communication.py`)
  - HTTP/GRPC server implementation
  - Tool execution coordination
  - Response formatting and error handling

- **Tool Manager** (`agentmanager/core/tool_manager.py`)
  - Tool registration and assignment
  - Agent-tool coordination
  - Tool availability management

- **Agent-Tools Tracker** (`agentmanager/core/tools/agent_tools_tracker.py`)
  - Centralized tracking of tool assignments to agents
  - Bidirectional lookup (agent → tools, tool → agents)
  - Usage statistics and monitoring
  - CLI management integration
  - **Module Placement**: New module within existing `tools` package
  - **Design Documents**: [Core Module Design](core/05_agent_tools_tracker_module_design.md) | [Component Design](core/06_agent_tools_tracker_design.md)

#### Implementation Order
1. Design API generation framework
2. Implement endpoint creation for registered functions
3. Add parameter validation and error handling
4. Build tool communication layer
5. Create tool manager for coordination
6. Implement agent-tools tracker for assignment management
7. Add CLI commands for tool assignment management
8. Integrate tracker with agent loading and execution

#### Success Criteria
- Generates working API endpoints for all registered functions
- Handles parameter validation correctly
- Provides comprehensive error handling
- API endpoints are secure and performant
- **Agent-Tools Tracker** manages tool assignments correctly
- **Bidirectional lookup** works (agent → tools, tool → agents)
- **O(1) lookup performance** for all operations
- **CLI commands** work for tool assignment management
- **Usage statistics** are accurate and up-to-date
- **Tool assignments** are properly tracked during agent execution
- **Error handling** prevents invalid assignments
- **Module placement** is correct (`agentmanager/core/tools/agent_tools_tracker.py`)

#### End-to-End Test After Step 2
**Test Name**: `test_tool_api_generation_and_management_e2e`
**Purpose**: Validate complete API generation, tool management workflow, and agent-tools tracking
**Test Steps**:
1. Register multiple tools with different parameter types
2. Verify API endpoints are auto-generated for all tools
3. Test parameter validation with valid and invalid inputs
4. Test error handling with malformed requests
5. Test tool manager coordination between multiple tools
6. Verify API documentation is generated correctly
7. Test concurrent tool execution
8. **Test Agent-Tools Tracker assignment management**
9. **Test bidirectional lookup (agent → tools, tool → agents)**
10. **Test O(1) lookup performance for all operations**
11. **Verify CLI commands for tool assignment work correctly**
12. **Test tool assignment tracking during agent execution**
13. **Verify usage statistics are accurate and up-to-date**
14. **Test error handling prevents invalid assignments**
15. **Verify module placement is correct**

**Validation Criteria**:
- ✅ All registered tools have working API endpoints
- ✅ Parameter validation works for all tool types
- ✅ Error handling returns appropriate HTTP status codes
- ✅ Tool manager coordinates multiple tools correctly
- ✅ API documentation is complete and accurate
- ✅ Concurrent execution doesn't cause conflicts
- ✅ Performance meets requirements (<100ms response time)
- ✅ **Agent-Tools Tracker manages assignments correctly**
- ✅ **Bidirectional lookup works (agent → tools, tool → agents)**
- ✅ **O(1) lookup performance for all operations**
- ✅ **CLI commands for tool assignment work properly**
- ✅ **Tool assignments are tracked during agent execution**
- ✅ **Usage statistics are accurate and up-to-date**
- ✅ **Error handling prevents invalid assignments**
- ✅ **Module placement is correct**

**Blocking Criteria**: If this test fails, Step 3 cannot begin until issues are resolved.

---

### Step 3: Agent Integration and Progress Tracking (Week 3-4)
**Goal**: Integrate agents with assigned tools and implement semantic progress tracking

#### Deliverables
- **Enhanced Agent Wrapper** (`agentmanager/core/enhanced_agent_wrapper.py`)
  - Tool access integration
  - Tool usage coordination
  - Progress tracking integration

- **Semantic Progress Tracker** (`agentmanager/utils/semantic_progress.py`)
  - Human-readable progress messages
  - Task phase management
  - Real-time status updates

- **Tool Context Injection** (`agentmanager/runtime/tool_context.py`)
  - Provides available tools to agents
  - Injects tool context during agent execution
  - **Note**: Tool selection logic is handled by individual agents, not AgentHub

#### Implementation Order
1. Enhance agent wrapper with tool access
2. Implement semantic progress tracking
3. Add tool assignment and access
4. Create progress reporting system
5. **Implement tool context injection** (agents handle tool selection)
6. Integrate all components

#### Success Criteria
- Agents can access and use assigned tools
- **Tool context is properly injected** to agents
- **Agents handle their own tool selection logic**
- Progress tracking provides meaningful updates
- Tool assignment and access works correctly
- All components integrate seamlessly

#### End-to-End Test After Step 3
**Test Name**: `test_agent_tool_integration_and_progress_tracking_e2e`
**Purpose**: Validate complete agent-tool integration and progress tracking workflow
**Test Steps**:
1. Load an agent with assigned tools
2. Execute agent task that requires tool usage
3. Verify agent can access and use assigned tools
4. Verify progress tracking provides meaningful updates
5. Test tool assignment and access control
6. Verify semantic progress messages are human-readable
7. Test multiple agents with different tool assignments
8. Verify no cross-contamination between agent tool access

**Validation Criteria**:
- ✅ Agent successfully uses assigned tools
- ✅ Progress tracking provides meaningful, real-time updates
- ✅ Tool assignment works correctly (agents only access assigned tools)
- ✅ Semantic progress messages are clear and informative
- ✅ Multiple agents can run concurrently with different tool sets
- ✅ No unauthorized tool access occurs
- ✅ Progress tracking doesn't impact performance significantly

**Blocking Criteria**: If this test fails, Step 4 cannot begin until issues are resolved.

---

### Step 4: Advanced Features and Testing (Week 4-5)
**Goal**: Add advanced features and comprehensive testing

#### Deliverables
- **Authentication and Authorization** (`agentmanager/core/auth_manager.py`)
  - User authentication system
  - Tool access control
  - Security validation

- **Tool Composition and Workflows** (`agentmanager/core/tool_workflows.py`)
  - Tool workflow creation
  - Multi-tool orchestration
  - Workflow management

- **Performance Monitoring** (`agentmanager/utils/performance_monitor.py`)
  - Tool execution metrics
  - Performance optimization
  - Resource monitoring

- **Testing Suite** (`tests/phase2_5_complete_system/`)
  - Unit tests for all components
  - Integration tests for workflows
  - Performance benchmarks

#### Implementation Order
1. Implement authentication and authorization
2. Add tool composition capabilities
3. Create performance monitoring system
4. Build comprehensive testing suite
5. Final integration and validation

#### Success Criteria
- Authentication system works correctly
- Tool workflows can be created and executed
- Performance monitoring provides useful insights
- Test coverage above 90%
- System is production-ready

#### End-to-End Test After Step 4
**Test Name**: `test_complete_system_production_readiness_e2e`
**Purpose**: Validate complete system is production-ready with all advanced features
**Test Steps**:
1. Test authentication and authorization with multiple users
2. Create and execute complex tool workflows
3. Verify performance monitoring captures all metrics
4. Test system under load (100+ concurrent agents)
5. Verify security measures prevent unauthorized access
6. Test system recovery from failures
7. Validate all documentation and examples work
8. Run comprehensive test suite (unit, integration, e2e)

**Validation Criteria**:
- ✅ Authentication and authorization work correctly
- ✅ Tool workflows execute successfully
- ✅ Performance monitoring provides actionable insights
- ✅ System handles load without degradation
- ✅ Security measures prevent unauthorized access
- ✅ System recovers gracefully from failures
- ✅ All documentation is accurate and examples work
- ✅ Test coverage is above 90%
- ✅ System meets all production requirements

**Blocking Criteria**: If this test fails, the system is not ready for production deployment.

---

## Testing Strategy

### Core Testing Principle: End-to-End Validation After Each Phase
**Critical**: Each phase must pass a comprehensive end-to-end test before proceeding to the next phase. This prevents redundant effort and ensures solid foundations.

### Per-Step Testing
Each step includes these test types:
- **Unit Tests**: Individual component testing (run continuously)
- **Integration Tests**: Component interaction testing (run after each component)
- **End-to-End Tests**: Complete workflow testing (run after each phase - BLOCKING)
- **Performance Tests**: Performance and scalability testing (run after each phase)

### End-to-End Test Requirements
Each end-to-end test must:
1. **Validate Complete Workflow**: Test the entire user journey for that phase
2. **Include Error Scenarios**: Test both success and failure cases
3. **Verify Integration**: Ensure all components work together
4. **Check Performance**: Meet performance requirements
5. **Be Blocking**: Next phase cannot start until test passes

### Test Locations
```
tests/phase2.5_semantic_tools/
├── step1_tool_registration/       # Tool registration and hosting tests
│   ├── unit/                      # Unit tests for components
│   ├── integration/               # Integration tests
│   └── e2e/                       # End-to-end test (BLOCKING)
├── step2_api_generation/          # API generation and management tests
│   ├── unit/                      # Unit tests for components
│   ├── integration/               # Integration tests
│   └── e2e/                       # End-to-end test (BLOCKING)
├── step3_agent_integration/       # Agent integration and progress tests
│   ├── unit/                      # Unit tests for components
│   ├── integration/               # Integration tests
│   └── e2e/                       # End-to-end test (BLOCKING)
└── step4_production_ready/        # Production readiness tests
    ├── unit/                      # Unit tests for components
    ├── integration/               # Integration tests
    └── e2e/                       # Final end-to-end test (BLOCKING)
```

---

## Validation Milestones

### Phase Gate Requirements
Each phase has a **mandatory gate** that must be passed before proceeding:

#### Gate 1: Tool Registration Foundation (After Step 1)
- **E2E Test**: `test_tool_registration_and_hosting_e2e` must pass
- **Performance**: Tool registration < 1 second, API response < 100ms
- **Coverage**: 90%+ unit test coverage for tool registration components
- **Documentation**: Complete API documentation for tool registration

#### Gate 2: API Generation Complete (After Step 2)
- **E2E Test**: `test_tool_api_generation_and_management_e2e` must pass
- **Performance**: API generation < 2 seconds, concurrent execution stable
- **Coverage**: 90%+ unit test coverage for API generation components
- **Documentation**: Complete API documentation for all generated endpoints

#### Gate 3: Agent Integration Working (After Step 3)
- **E2E Test**: `test_agent_tool_integration_and_progress_tracking_e2e` must pass
- **Performance**: Agent startup < 3 seconds, progress updates < 50ms
- **Coverage**: 90%+ unit test coverage for agent integration components
- **Documentation**: Complete user guide for agent-tool integration

#### Gate 4: Production Ready (After Step 4)
- **E2E Test**: `test_complete_system_production_readiness_e2e` must pass
- **Performance**: System handles 100+ concurrent agents without degradation
- **Coverage**: 95%+ overall test coverage
- **Documentation**: Complete production deployment guide

### Gate Failure Protocol
If any gate fails:
1. **Stop**: Do not proceed to next phase
2. **Analyze**: Identify root cause of failure
3. **Fix**: Address all issues found
4. **Re-test**: Run full test suite again
5. **Validate**: Ensure gate passes completely
6. **Document**: Record lessons learned

---

## Risk Mitigation

### Function Discovery Risks
- **Complex Dependencies**: Functions with complex imports might not be discovered correctly
  - **Mitigation**: Comprehensive dependency analysis, fallback mechanisms

### API Generation Risks
- **Security Vulnerabilities**: Auto-generated APIs could have security issues
  - **Mitigation**: Security validation, input sanitization, rate limiting

### Tool Communication Risks
- **Network Failures**: Tool communication could fail
  - **Mitigation**: Retry mechanisms, fallback tools, graceful degradation

### Backward Compatibility
- All changes additive, no breaking changes
- Existing agents continue working
- Gradual rollout with feature flags

---

## Completion Checklist

### Step 1: Tool Registration Foundation
- [ ] Tool decorator system implemented
- [ ] Tool registration system working
- [ ] Tool service hosting functional
- [ ] Tool validation and security working
- [ ] **GATE 1**: `test_tool_registration_and_hosting_e2e` passes
- [ ] **GATE 1**: Performance requirements met
- [ ] **GATE 1**: 90%+ test coverage achieved
- [ ] **GATE 1**: Documentation complete

### Step 2: API Generation and Management
- [ ] API generation framework complete
- [ ] Endpoints created for all registered functions
- [ ] Parameter validation working
- [ ] Tool communication layer functional
- [ ] Tool manager coordination working
- [ ] **GATE 2**: `test_tool_api_generation_and_management_e2e` passes
- [ ] **GATE 2**: Performance requirements met
- [ ] **GATE 2**: 90%+ test coverage achieved
- [ ] **GATE 2**: Documentation complete

### Step 3: Agent Integration and Progress Tracking
- [ ] Enhanced agent wrapper working
- [ ] Semantic progress tracking implemented
- [ ] Tool assignment and access working
- [ ] Progress reporting system functional
- [ ] All components integrated
- [ ] **GATE 3**: `test_agent_tool_integration_and_progress_tracking_e2e` passes
- [ ] **GATE 3**: Performance requirements met
- [ ] **GATE 3**: 90%+ test coverage achieved
- [ ] **GATE 3**: Documentation complete

### Step 4: Production Ready
- [ ] Authentication system complete
- [ ] Tool workflows working
- [ ] Performance monitoring functional
- [ ] Comprehensive testing complete
- [ ] **GATE 4**: `test_complete_system_production_readiness_e2e` passes
- [ ] **GATE 4**: Performance requirements met
- [ ] **GATE 4**: 95%+ test coverage achieved
- [ ] **GATE 4**: Production deployment guide complete
- [ ] **GATE 4**: System validated and ready for production

---

## Next Steps
1. Review and approve this updated implementation plan
2. Begin Step 1: Function Discovery Foundation
3. Create implementation timeline
4. Set up development branches
5. Begin incremental implementation