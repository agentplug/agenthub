# Process Manager Refactoring Design

**Phase**: 3.4 - Real-time Communication
**Date**: October 16, 2025
**Status**: Design Proposal
**Author**: Architecture Review

---

## Executive Summary

The current `ProcessManager` class has grown to 960 lines (38KB) and handles too many responsibilities. This document outlines a refactoring plan to convert it into a modular architecture with clear separation of concerns, improved testability, and better maintainability.

**Key Goals:**
- Split monolithic `process_manager.py` into focused modules
- Maintain backward compatibility with existing API
- Improve testability and code organization
- Establish clear boundaries for WebSocket communication
- Preserve optional monitoring as a plugin system

---

## Current State Analysis

### File Structure
```
agenthub/runtime/
├── __init__.py
├── agent_runtime.py           (8.2K)
├── environment_manager.py     (4.3K)
└── process_manager.py         (38K - TOO LARGE!)

agenthub/monitoring/          (Separate, optional)
├── llm_analyzer.py           (4.9K)
├── log_streamer.py           (5.9K)
├── terminal_display.py       (6.6K)
└── metrics.py                (8.4K - UNUSED!)
```

### Problems Identified

**1. Single Responsibility Principle Violation**

`ProcessManager` currently handles:
- ✗ Process execution (subprocess management)
- ✗ WebSocket communication (server lifecycle, session management)
- ✗ Monitoring coordination (LLM analysis, log streaming, terminal display)
- ✗ Log streaming & filtering
- ✗ Session lifecycle management
- ✗ Dynamic execution delegation
- ✗ Environment management delegation

**2. Code Organization Issues**
- 960 lines in single file makes navigation difficult
- Mixed abstraction levels (high-level orchestration + low-level subprocess details)
- Hard to test components in isolation
- Difficult to reuse communication layer elsewhere

**3. Tight Coupling**
- WebSocket communication tightly coupled to process execution
- Monitoring components imported conditionally but still coupled
- Log filtering logic embedded in streaming code

**4. Unused Code**
- `agenthub/monitoring/metrics.py` - No references found
- Should be removed to reduce maintenance burden

---

## Proposed Solution

### Architecture Overview

Convert to modular architecture with clear component boundaries:

```
agenthub/runtime/process_manager/
├── __init__.py                    # Public API (backward compatibility)
├── manager.py                     # Core orchestration (150 lines)
├── executor.py                    # Process execution logic (300 lines)
├── communication.py               # WebSocket management (200 lines)
├── log_streaming.py               # Log capture & filtering (150 lines)
├── monitoring_adapter.py          # Monitoring integration (100 lines)
└── session.py                     # Session lifecycle (60 lines)

agenthub/monitoring/               # Keep as optional plugin
├── __init__.py
├── llm_analyzer.py               # ✅ Keep
├── log_streamer.py               # ✅ Keep
├── terminal_display.py           # ✅ Keep
└── metrics.py                    # ❌ Remove (unused)
```

### Design Principles

1. **Separation of Concerns**: Each module has one clear responsibility
2. **Backward Compatibility**: Existing API unchanged via `__init__.py`
3. **Testability**: Components can be tested independently
4. **Extensibility**: Easy to add new execution strategies or communication methods
5. **Optional Features**: Monitoring and WebSocket are opt-in plugins

---

## Detailed Module Design

### 1. `__init__.py` - Public API

**Purpose**: Maintain backward compatibility, expose ProcessManager class

**Responsibilities:**
- Export `ProcessManager` class
- Maintain existing public API
- Version info

**Example:**
```python
"""Process manager for executing agents in isolated subprocesses."""

from .manager import ProcessManager

__all__ = ["ProcessManager"]
```

---

### 2. `manager.py` - Core Orchestration

**Size**: ~150 lines
**Purpose**: High-level orchestration and delegation

**Responsibilities:**
- Initialize subsystems (executor, communication, monitoring)
- Orchestrate execution flow
- Delegate to specialized components
- Manage component lifecycle

**Key Methods:**
```python
class ProcessManager:
    def __init__(self, timeout, use_dynamic_execution, monitoring, realtime_communication):
        """Initialize all subsystems."""

    def execute_agent(self, agent_path, method, parameters, manifest, tool_context):
        """Main entry point - orchestrates execution flow."""

    def set_monitoring(self, enabled):
        """Enable/disable monitoring dynamically."""

    def set_realtime_communication(self, enabled):
        """Enable/disable WebSocket communication."""

    def get_communication_status(self):
        """Get current communication status."""

    def validate_agent_structure(self, agent_path, require_venv):
        """Validate agent directory structure."""
```

**Dependencies:**
- `executor.Executor`
- `communication.CommunicationManager`
- `monitoring_adapter.MonitoringAdapter`
- `session.SessionManager`

---

### 3. `executor.py` - Process Execution

**Size**: ~300 lines
**Purpose**: Handle subprocess execution and result parsing

**Responsibilities:**
- Execute agents via subprocess or dynamic execution
- Parse execution results (JSON parsing)
- Handle timeouts and errors
- Determine agent script type (Python vs Dana)

**Key Methods:**
```python
class Executor:
    def __init__(self, timeout, use_dynamic_execution, environment_manager):
        """Initialize executor with configuration."""

    def execute(self, agent_path, method, parameters, tool_context, manifest):
        """Execute agent and return result."""

    def execute_subprocess(self, agent_path, method, parameters, tool_context):
        """Execute via subprocess with streaming."""

    def execute_dynamic(self, agent_path, method, parameters, manifest):
        """Execute via dynamic execution (in-process)."""

    def parse_result(self, result, execution_time):
        """Parse and validate execution result."""

    def _get_agent_script(self, agent_path):
        """Determine agent script path (agent.py vs agent.na)."""

    def _handle_timeout(self, process):
        """Handle subprocess timeout."""
```

**Design Notes:**
- Separates execution strategy (subprocess vs dynamic) cleanly
- Encapsulates result parsing logic
- No knowledge of monitoring or WebSocket - just executes

---

### 4. `communication.py` - WebSocket Management

**Size**: ~200 lines
**Purpose**: Manage WebSocket server lifecycle and agent sessions

**Responsibilities:**
- Initialize WebSocket server (with graceful fallback)
- Register/unregister agent sessions
- Check server status and health
- Coordinate message sending

**Key Methods:**
```python
class CommunicationManager:
    def __init__(self, enabled=True):
        """Initialize communication manager."""

    async def ensure_server_running(self):
        """Ensure WebSocket server is started."""

    def register_session(self, agent_path, session_data):
        """Register agent session for communication."""

    def unregister_session(self, agent_path):
        """Clean up agent session."""

    def send_message(self, agent_path, message):
        """Send message to specific agent session."""

    def get_status(self):
        """Get communication server status."""

    def log_status(self):
        """Log current communication status."""

    def start_server_if_needed(self):
        """Start server in background thread if not running."""

    def is_available(self):
        """Check if WebSocket communication is available."""
```

**Design Notes:**
- Encapsulates all WebSocket server interaction
- Handles graceful fallback to stdin/stdout
- No subprocess knowledge - pure communication layer
- Could be reused by CLI or API in future

---

### 5. `log_streaming.py` - Log Capture & Filtering

**Size**: ~150 lines
**Purpose**: Real-time log streaming with filtering

**Responsibilities:**
- Stream stdout/stderr from subprocess
- Filter noise and internal logs
- Send logs via WebSocket communication
- Collect logs for final result

**Key Methods:**
```python
class LogStreamer:
    def __init__(self, communication_manager, agent_path, method):
        """Initialize log streamer."""

    def stream_logs(self, process):
        """Start streaming logs from subprocess."""

    def _stream_stdout(self, process):
        """Stream stdout in separate thread."""

    def _stream_stderr(self, process):
        """Stream stderr in separate thread."""

    def _is_noise_log(self, log_line):
        """Determine if log should be filtered."""

    def _send_log_message(self, stream, message):
        """Send log via WebSocket."""

    def get_collected_logs(self):
        """Get all collected logs."""
```

**Log Filtering Rules:**
```python
# Filter by logger name
internals = [
    "research_agent.core.research",
    "research_agent.core.tools.agenthub_mcp_client",
]

# Filter by content patterns
noise = [
    'File "/',
    "Traceback",
    "DEBUG:",
    "ERROR:",
    "HTTP Request:",
    "httpx:",
    "pydantic",
]
```

**Design Notes:**
- Standalone component - can be tested independently
- Uses communication manager for sending (dependency injection)
- Clean separation between filtering logic and streaming logic

---

### 6. `monitoring_adapter.py` - Monitoring Integration

**Size**: ~100 lines
**Purpose**: Integrate optional monitoring features

**Responsibilities:**
- Load monitoring components dynamically (lazy import)
- Coordinate monitoring lifecycle
- Execute agent with monitoring enabled
- Handle monitoring errors gracefully

**Key Methods:**
```python
class MonitoringAdapter:
    def __init__(self, enabled=False):
        """Initialize monitoring adapter."""

    def enable(self):
        """Enable monitoring (lazy load components)."""

    def disable(self):
        """Disable monitoring and cleanup."""

    def execute_with_monitoring(self, command, agent_dir, timeout):
        """Execute subprocess with monitoring enabled."""

    def _load_monitoring_components(self):
        """Lazy load monitoring dependencies."""

    def _start_monitoring_session(self, command, agent_dir):
        """Start log streaming and display."""

    def _monitor_execution(self, start_time):
        """Monitor execution with periodic analysis."""

    def _finalize_monitoring(self, execution_time, return_code):
        """Cleanup and show final summary."""
```

**Design Notes:**
- Lazy loads monitoring components (only when enabled)
- Handles ImportError gracefully
- Keeps monitoring logic isolated from core execution
- Acts as facade to `agenthub.monitoring` module

---

### 7. `session.py` - Session Lifecycle

**Size**: ~60 lines
**Purpose**: Manage agent session state and lifecycle

**Responsibilities:**
- Track session state (registered, executing, completed)
- Coordinate session registration/cleanup
- Provide session status information

**Key Methods:**
```python
class SessionManager:
    def __init__(self, communication_manager):
        """Initialize session manager."""

    def start_session(self, agent_path, method, parameters):
        """Start agent session and register."""

    def end_session(self, agent_path, success=True):
        """End session and cleanup."""

    def is_session_active(self, agent_path):
        """Check if session is active."""

    def get_session_info(self, agent_path):
        """Get session information."""
```

**Design Notes:**
- Simple coordinator between execution and communication
- Ensures proper cleanup even on errors
- Could be extended for session persistence in future

---

## Migration Plan

### Phase 1: Preparation (Week 1)

**Goals**: Set up new structure without breaking existing code

**Tasks:**
1. Create `agenthub/runtime/process_manager/` directory
2. Create `__init__.py` with import from old file
3. Set up test structure
4. Document public API contract

**Success Criteria:**
- New directory exists
- Tests still pass
- No functionality changes

---

### Phase 2: Extract Components (Week 2)

**Goals**: Move code into new modules while maintaining compatibility

**Day 1-2: Extract Executor**
- Move subprocess execution logic to `executor.py`
- Move result parsing to `executor.py`
- Update imports in `manager.py`
- Write unit tests for `Executor`

**Day 3-4: Extract Communication**
- Move WebSocket logic to `communication.py`
- Move session registration to `communication.py`
- Update imports
- Write unit tests for `CommunicationManager`

**Day 5: Extract Log Streaming**
- Move log streaming to `log_streaming.py`
- Move filtering logic
- Update imports
- Write unit tests for `LogStreamer`

**Day 6-7: Extract Monitoring Adapter**
- Move monitoring coordination to `monitoring_adapter.py`
- Implement lazy loading
- Write unit tests

**Success Criteria:**
- All modules extracted
- Tests pass for each module
- Code coverage >80%

---

### Phase 3: Integration (Week 3)

**Goals**: Integrate all components and ensure backward compatibility

**Tasks:**
1. Update `manager.py` to orchestrate new components
2. Ensure backward compatibility via `__init__.py`
3. Run full integration tests
4. Update documentation
5. Performance testing

**Success Criteria:**
- All existing tests pass
- No API changes
- Performance unchanged or improved
- Documentation updated

---

### Phase 4: Cleanup (Week 4)

**Goals**: Remove old code and improve quality

**Tasks:**
1. Remove old `process_manager.py` (move to `_deprecated/`)
2. Remove `agenthub/monitoring/metrics.py`
3. Add tests for monitoring components
4. Code review and refinement
5. Update architecture documentation

**Success Criteria:**
- Old code removed
- Test coverage >85%
- Code review approved
- Architecture docs updated

---

## Testing Strategy

### Unit Tests

Each module gets comprehensive unit tests:

**`test_executor.py`:**
```python
def test_execute_subprocess_success()
def test_execute_subprocess_timeout()
def test_execute_dynamic_execution()
def test_parse_result_valid_json()
def test_parse_result_invalid_json()
def test_get_agent_script_python()
def test_get_agent_script_dana()
```

**`test_communication.py`:**
```python
def test_initialize_server_success()
def test_initialize_server_fallback()
def test_register_session()
def test_unregister_session()
def test_send_message_connected()
def test_send_message_disconnected()
def test_get_status()
```

**`test_log_streaming.py`:**
```python
def test_stream_stdout()
def test_stream_stderr()
def test_filter_noise_logs()
def test_collect_logs()
def test_send_via_websocket()
```

**`test_monitoring_adapter.py`:**
```python
def test_enable_monitoring()
def test_disable_monitoring()
def test_lazy_loading()
def test_handle_import_error()
```

### Integration Tests

Test component interactions:

```python
def test_full_execution_with_websocket()
def test_full_execution_with_monitoring()
def test_execution_with_fallback()
def test_session_lifecycle()
```

### Performance Tests

Ensure no regression:

```python
def test_execution_performance()
def test_websocket_latency()
def test_log_streaming_overhead()
```

---

## Backward Compatibility

### Public API Contract

The following API must remain unchanged:

```python
# Initialization
manager = ProcessManager(
    timeout=300,
    use_dynamic_execution=True,
    monitoring=False,
    realtime_communication=True
)

# Execution
result = manager.execute_agent(
    agent_path="path/to/agent",
    method="run",
    parameters={"query": "test"},
    manifest=None,
    tool_context=None
)

# Configuration
manager.set_monitoring(True)
manager.set_realtime_communication(False)
manager.validate_agent_structure("path/to/agent")
manager.get_communication_status()
manager.log_communication_status()
```

### Implementation Strategy

`__init__.py` maintains compatibility:

```python
"""
Process manager for executing agents in isolated subprocesses.

Backward compatible API maintained through this module.
"""

from .manager import ProcessManager

# Re-export for backward compatibility
__all__ = ["ProcessManager"]

# Version info
__version__ = "2.0.0"  # Major version for internal refactoring
```

---

## Monitoring Module Decision

### Keep `agenthub/monitoring/` as Optional Plugin

**Rationale:**
1. **Separation of Concerns**: Monitoring is optional, not core functionality
2. **Reusability**: Could be used by CLI, API, or other components in future
3. **Plugin Architecture**: Clean opt-in design
4. **Independent Evolution**: Can evolve monitoring without affecting core execution

### Actions:

**Keep:**
- ✅ `llm_analyzer.py` - LLM-based log analysis
- ✅ `log_streamer.py` - Real-time log capture
- ✅ `terminal_display.py` - Visual progress display

**Remove:**
- ❌ `metrics.py` - Unused, no references found

**Add:**
- ✅ Unit tests for each monitoring component
- ✅ Integration tests with process_manager
- ✅ Documentation for enabling/using monitoring

---

## Benefits of Refactoring

### Code Quality
- ✅ **Smaller files** - Easier to understand and maintain
- ✅ **Clear responsibilities** - Each module has one job
- ✅ **Better organization** - Logical grouping of related code
- ✅ **Reduced complexity** - Simpler mental model

### Testing
- ✅ **Unit testable** - Test components in isolation
- ✅ **Easier mocking** - Clear dependency boundaries
- ✅ **Better coverage** - Focused test suites
- ✅ **Faster tests** - Can skip integration tests for unit changes

### Maintainability
- ✅ **Easier debugging** - Smaller scope to search
- ✅ **Safer changes** - Isolated impact
- ✅ **Better docs** - Each module can have focused documentation
- ✅ **Team scaling** - Different people can work on different modules

### Extensibility
- ✅ **New execution strategies** - Add new executors easily
- ✅ **Alternative communication** - Could add gRPC, HTTP, etc.
- ✅ **Monitoring plugins** - Easy to add new monitoring features
- ✅ **Future features** - Clear place for new functionality

---

## Risk Assessment

### Low Risk
- ✅ Unit tests in place before refactoring
- ✅ Backward compatibility maintained
- ✅ Incremental migration (can pause at any phase)
- ✅ Old code kept as reference during transition

### Medium Risk
- ⚠️ Integration complexity - Components must work together
- ⚠️ Performance impact - Need to measure and optimize
- ⚠️ Testing coverage - Must achieve >85% coverage

### Mitigation Strategies
1. **Comprehensive Testing**: Write tests before refactoring
2. **Incremental Rollout**: Deploy phase by phase
3. **Performance Monitoring**: Benchmark before and after
4. **Rollback Plan**: Keep old code until confident in new version
5. **Code Review**: Peer review for each phase

---

## Success Metrics

### Code Metrics
- File size: All files <400 lines ✅
- Cyclomatic complexity: <10 per method ✅
- Test coverage: >85% ✅
- Code duplication: <3% ✅

### Quality Metrics
- All existing tests pass ✅
- New unit tests for all modules ✅
- Integration tests for component interactions ✅
- Documentation updated ✅

### Performance Metrics
- Execution time unchanged or improved ✅
- WebSocket latency <10ms ✅
- Memory usage unchanged or reduced ✅
- No regression in subprocess handling ✅

---

## Timeline

**Total Duration**: 4 weeks

| Week | Phase | Deliverables |
|------|-------|--------------|
| 1 | Preparation | New structure, tests setup, API documentation |
| 2 | Extraction | All modules extracted with unit tests |
| 3 | Integration | Components integrated, all tests pass |
| 4 | Cleanup | Old code removed, documentation complete |

**Checkpoints:**
- End of Week 1: Structure approved, ready to extract
- End of Week 2: All modules extracted, unit tested
- End of Week 3: Integration complete, all tests green
- End of Week 4: Cleanup done, ready for production

---

## Conclusion

This refactoring transforms `ProcessManager` from a monolithic 960-line file into a clean, modular architecture with clear separation of concerns. The new structure:

1. **Improves Maintainability**: Smaller, focused modules
2. **Enhances Testability**: Independent unit testing
3. **Enables Extensibility**: Easy to add new features
4. **Maintains Compatibility**: No breaking changes to public API
5. **Preserves Quality**: Comprehensive testing throughout

The migration plan is low-risk, incremental, and can be paused at any phase if issues arise. The monitoring module remains as an optional plugin, demonstrating good architectural separation.

**Recommendation**: Proceed with refactoring following the outlined plan.

---

## Appendix A: File Size Breakdown

**Before Refactoring:**
```
process_manager.py: 960 lines (38KB)
```

**After Refactoring:**
```
manager.py:            150 lines (~6KB)
executor.py:           300 lines (~12KB)
communication.py:      200 lines (~8KB)
log_streaming.py:      150 lines (~6KB)
monitoring_adapter.py: 100 lines (~4KB)
session.py:             60 lines (~2KB)
__init__.py:            20 lines (~1KB)
--------------------------------
Total:                 980 lines (~39KB)
```

**Net Change**: +20 lines, +1KB (minor increase for better organization)

---

## Appendix B: Import Graph

```
manager.py
  ├── executor.py
  │     └── environment_manager
  ├── communication.py
  │     └── agenthub.core.communication.server
  ├── log_streaming.py
  │     └── communication.py
  ├── monitoring_adapter.py
  │     └── agenthub.monitoring.*  (lazy import)
  └── session.py
        └── communication.py

agenthub.monitoring/  (optional)
  ├── llm_analyzer.py
  ├── log_streamer.py
  └── terminal_display.py
```

**Dependency Rules:**
- No circular dependencies
- Communication layer standalone
- Monitoring optional and lazy-loaded
- Executor independent of communication

---

## Appendix C: Configuration Examples

### Minimal Configuration (No Monitoring, No WebSocket)
```python
manager = ProcessManager(
    timeout=300,
    use_dynamic_execution=True,
    monitoring=False,
    realtime_communication=False
)
```

### Full Features (Monitoring + WebSocket)
```python
manager = ProcessManager(
    timeout=600,
    use_dynamic_execution=True,
    monitoring=True,
    realtime_communication=True
)
```

### Dynamic Configuration
```python
manager = ProcessManager(timeout=300)

# Enable monitoring later
manager.set_monitoring(True)

# Enable WebSocket
manager.set_realtime_communication(True)

# Check status
status = manager.get_communication_status()
print(f"WebSocket: {status['enabled']}")
```

---

**Document Version**: 1.0
**Last Updated**: October 16, 2025
**Next Review**: After Phase 1 completion
