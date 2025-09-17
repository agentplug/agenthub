# Phase 1: Runtime Module Testing Plan

**Document Type**: Runtime Module Testing Plan
**Phase**: 1 - Foundation
**Author**: William
**Date Created**: 2025-06-28
**Last Updated**: 2025-06-28
**Status**: Active
**Purpose**: Comprehensive testing for Runtime Module functionality

## 🎯 **Runtime Module Testing Overview**

### **Module Purpose**
The Runtime Module is the **core execution engine** that manages agent subprocess execution, environment management, and agent coordination.

### **Testing Focus**
- **"Can Run" Philosophy**: Test that agents execute successfully
- **Process Isolation**: Ensure agents run in isolated environments
- **Error Handling**: Validate graceful failure modes
- **Integration**: Test coordination with other modules

---

## 🧪 **Unit Testing**

### **Process Manager Unit Tests**

#### **Basic Functionality**
- [ ] **Test subprocess creation**: Can create subprocess with correct command
- [ ] **Test parameter passing**: JSON parameters correctly passed to agent
- [ ] **Test output capture**: Can capture stdout and stderr from subprocess
- [ ] **Test return code handling**: Correctly interprets subprocess exit codes

#### **Error Handling**
- [ ] **Test subprocess timeout**: Handles execution timeouts gracefully
- [ ] **Test subprocess failure**: Handles subprocess crashes gracefully
- [ ] **Test invalid commands**: Handles invalid Python paths gracefully
- [ ] **Test permission errors**: Handles file permission issues gracefully

#### **Resource Management**
- [ ] **Test process cleanup**: Orphaned processes are properly cleaned up
- [ ] **Test memory limits**: Respects memory usage limits
- [ ] **Test file descriptor limits**: Doesn't leak file descriptors
- [ ] **Test concurrent execution**: Can handle multiple simultaneous executions

### **Environment Manager Unit Tests**

#### **Virtual Environment Management**
- [ ] **Test venv creation**: Can create virtual environments using UV
- [ ] **Test venv detection**: Correctly identifies existing virtual environments
- [ ] **Test Python path resolution**: Returns correct Python executable path
- [ ] **Test fallback handling**: Falls back to pip if UV unavailable

#### **Dependency Management**
- [ ] **Test dependency installation**: Can install packages in isolated environments
- [ ] **Test requirement parsing**: Correctly parses requirements.txt files
- [ ] **Test conflict resolution**: Handles dependency conflicts gracefully
- [ ] **Test installation failures**: Reports installation errors clearly

#### **Environment Isolation**
- [ ] **Test environment variables**: Provides isolated environment variables
- [ ] **Test PATH isolation**: Doesn't inherit system Python paths
- [ ] **Test package isolation**: Agents can't access system packages
- [ ] **Test cross-platform compatibility**: Works on different operating systems

### **Agent Runtime Unit Tests**

#### **Agent Execution Coordination**
- [ ] **Test method validation**: Correctly validates agent methods before execution
- [ ] **Test parameter validation**: Validates method parameters
- [ ] **Test execution flow**: Coordinates between components correctly
- [ ] **Test result handling**: Correctly processes and returns execution results

#### **Error Coordination**
- [ ] **Test validation errors**: Reports method validation failures
- [ ] **Test execution errors**: Reports execution failures clearly
- **Test timeout coordination**: Handles timeouts across components
- [ ] **Test error propagation**: Errors flow correctly through the system

---

## 🔗 **Integration Testing**

### **Runtime + Storage Integration**

#### **Agent File Access**
- [ ] **Test agent path resolution**: Correctly resolves agent paths from storage
- [ ] **Test manifest loading**: Can load agent manifests from storage
- [ ] **Test file permissions**: Handles file permission issues gracefully
- [ ] **Test missing files**: Reports missing agent files clearly

#### **Agent Metadata Integration**
- [ ] **Test agent discovery**: Can discover agents through storage module
- [ ] **Test agent validation**: Validates agents using storage information
- [ ] **Test agent status**: Tracks agent execution status correctly
- [ ] **Test agent cleanup**: Cleans up agent resources after execution

### **Runtime + Core Integration**

#### **Agent Interface Validation**
- [ ] **Test method discovery**: Correctly discovers available methods from core
- [ ] **Test parameter validation**: Uses core module for parameter validation
- [ ] **Test interface consistency**: Maintains interface consistency with core
- [ ] **Test error reporting**: Reports validation errors from core module

#### **Agent Loading Coordination**
- [ ] **Test agent initialization**: Coordinates agent loading with core module
- [ ] **Test manifest parsing**: Uses core module for manifest processing
- [ ] **Test validation flow**: Validation flows correctly between modules
- [ ] **Test error handling**: Handles core module errors gracefully

### **Runtime + CLI Integration**

#### **Command Execution**
- [ ] **Test CLI execution**: CLI commands can trigger agent execution
- [ ] **Test parameter passing**: CLI parameters correctly passed to runtime
- [ ] **Test result display**: Execution results correctly displayed in CLI
- [ ] **Test error display**: Execution errors correctly displayed in CLI

#### **User Feedback**
- [ ] **Test progress indication**: CLI shows execution progress
- [ ] **Test timeout feedback**: CLI reports timeouts clearly
- [ ] **Test error details**: CLI provides helpful error information
- [ ] **Test success confirmation**: CLI confirms successful execution

---

## 🎯 **End-to-End Testing**

### **Complete Agent Execution Workflow**

#### **Agent Loading to Execution**
- [ ] **Test complete workflow**: User can load agent and execute methods
- [ ] **Test method discovery**: System discovers available methods automatically
- [ ] **Test parameter handling**: User parameters correctly processed
- [ ] **Test result delivery**: User receives execution results correctly

#### **Error Recovery Workflows**
- [ ] **Test agent not found**: System handles missing agents gracefully
- [ ] **Test method not found**: System reports missing methods clearly
- [ ] **Test execution failure**: System handles execution failures gracefully
- [ ] **Test timeout recovery**: System recovers from timeouts gracefully

### **Multi-Agent Scenarios**

#### **Concurrent Execution**
- [ ] **Test multiple agents**: Can execute multiple agents simultaneously
- [ ] **Test resource isolation**: Agents don't interfere with each other
- [ ] **Test error isolation**: One agent's failure doesn't affect others
- [ ] **Test cleanup coordination**: All agents cleaned up properly

#### **Agent Dependencies**
- [ ] **Test agent chaining**: Can chain agent method calls
- [ ] **Test result passing**: Results from one agent can be passed to another
- [ ] **Test error propagation**: Errors propagate correctly through chains
- [ ] **Test dependency management**: Handles agent dependencies correctly

---

## 🧪 **Test Implementation Examples**

### **Process Manager Test Example**
```python
# tests/phase1_foundation/runtime/test_process_manager.py
import pytest
from unittest.mock import Mock, patch
from agenthub.runtime.process_manager import ProcessManager

class TestProcessManager:
    def test_execute_agent_success(self, tmp_path):
        """Test successful agent execution."""
        pm = ProcessManager()

        # Create test agent
        agent_dir = tmp_path / "test-agent"
        agent_dir.mkdir()
        agent_script = agent_dir / "agent.py"
        agent_script.write_text("""
import json
import sys

if __name__ == "__main__":
    data = json.loads(sys.argv[1])
    print(json.dumps({"result": "success"}))
        """)

        # Mock subprocess.run
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = '{"result": "success"}'
            mock_run.return_value.stderr = ''

            result = pm.execute_agent(
                agent_path=str(agent_dir),
                method="test_method",
                parameters={"test": "value"},
                python_path="python"
            )

            assert result["result"] == "success"
            mock_run.assert_called_once()

    def test_execute_agent_timeout(self, tmp_path):
        """Test agent execution timeout."""
        pm = ProcessManager()

        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("test", 30)

            result = pm.execute_agent(
                agent_path=str(tmp_path),
                method="test_method",
                parameters={},
                python_path="python"
            )

            assert "timeout" in result["error"].lower()
```

### **Environment Manager Test Example**
```python
# tests/phase1_foundation/runtime/test_environment_manager.py
import pytest
from pathlib import Path
from agenthub.runtime.environment_manager import EnvironmentManager

class TestEnvironmentManager:
    def test_create_environment(self, tmp_path):
        """Test virtual environment creation."""
        em = EnvironmentManager()

        # Mock UV installation
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0

            venv_path = em.create_environment(str(tmp_path))
            assert venv_path.exists()
            assert (venv_path / "bin" / "python").exists()

    def test_get_python_executable(self, tmp_path):
        """Test Python executable path resolution."""
        em = EnvironmentManager()

        # Create mock venv structure
        venv_dir = tmp_path / "venv"
        venv_dir.mkdir()
        (venv_dir / "bin").mkdir()
        (venv_dir / "bin" / "python").touch()

        python_path = em.get_python_executable(str(tmp_path))
        assert python_path == str(venv_dir / "bin" / "python")
```

### **Agent Runtime Test Example**
```python
# tests/phase1_foundation/runtime/test_agent_runtime.py
import pytest
from agenthub.runtime.agent_runtime import AgentRuntime

class TestAgentRuntime:
    def test_execute_agent_workflow(self, tmp_path):
        """Test complete agent execution workflow."""
        runtime = AgentRuntime()

        # Mock dependencies
        with patch.object(runtime, 'validate_method') as mock_validate:
            with patch.object(runtime, 'environment_manager') as mock_env:
                with patch.object(runtime, 'process_manager') as mock_process:

                    mock_validate.return_value = True
                    mock_env.get_python_executable.return_value = "python"
                    mock_process.execute_agent.return_value = {"result": "success"}

                    result = runtime.execute_agent(
                        agent_path="test-agent",
                        method="test_method",
                        parameters={"test": "value"}
                    )

                    assert result["result"] == "success"
                    mock_validate.assert_called_once_with("test-agent", "test_method")
                    mock_process.execute_agent.assert_called_once()
```

---

## 📊 **Test Coverage Requirements**

### **Line Coverage Targets**
- **Process Manager**: 90%+ line coverage
- **Environment Manager**: 85%+ line coverage
- **Agent Runtime**: 90%+ line coverage
- **Overall Runtime Module**: 88%+ line coverage

### **Branch Coverage Targets**
- **Success Paths**: 100% coverage
- **Error Paths**: 80%+ coverage
- **Edge Cases**: 75%+ coverage

---

## 🚨 **Test Failure Scenarios**

### **Common Failure Modes**
- [ ] **Subprocess creation fails**: File not found, permission denied
- [ ] **Virtual environment issues**: UV not available, venv creation fails
- [ ] **Agent script errors**: Syntax errors, import failures
- [ ] **Resource exhaustion**: Memory limits, file descriptor limits
- [ ] **Timeout scenarios**: Long-running agents, hanging processes

### **Error Recovery Testing**
- [ ] **Test graceful degradation**: System continues working after failures
- [ ] **Test error reporting**: Clear error messages for users
- [ ] **Test recovery mechanisms**: System can recover from failures
- [ ] **Test resource cleanup**: Resources properly cleaned up after failures

---

## 🎯 **Runtime Module Success Criteria**

### **Functional Success**
- [ ] **Can execute agentplug agents**: Real agents run successfully
- [ ] **Process isolation works**: Agents don't interfere with each other
- [ ] **Environment management works**: Virtual environments created and managed
- [ ] **Error handling works**: Failures handled gracefully

### **Performance Success**
- [ ] **Subprocess overhead < 100ms**: Fast subprocess creation
- [ ] **Execution time < 30 seconds**: Reasonable timeout limits
- [ ] **Memory usage < 100MB**: Acceptable memory footprint
- [ ] **Concurrent execution**: Can handle multiple agents simultaneously

### **Integration Success**
- [ ] **Works with Storage Module**: Can access agent files
- [ ] **Works with Core Module**: Can validate agent interfaces
- [ ] **Works with CLI Module**: Can execute from command line
- [ ] **Works with real agents**: Can execute actual agentplug agents

---

## 📋 **Testing Checklist**

### **Pre-Testing Setup**
- [ ] Test environment configured
- [ ] Test dependencies installed
- [ ] Test data prepared
- [ ] Mock services configured

### **Unit Testing**
- [ ] Process Manager tests pass
- [ ] Environment Manager tests pass
- [ ] Agent Runtime tests pass
- [ ] Coverage targets met

### **Integration Testing**
- [ ] Runtime + Storage integration tests pass
- [ ] Runtime + Core integration tests pass
- [ ] Runtime + CLI integration tests pass
- [ ] Cross-module coordination works

### **End-to-End Testing**
- [ ] Complete agent execution workflows work
- [ ] Error scenarios handled gracefully
- [ ] Multi-agent scenarios work correctly
- [ ] Real agentplug agents execute successfully

### **Final Validation**
- [ ] All tests pass consistently
- [ ] Performance requirements met
- [ ] Integration points validated
- [ ] Ready for Phase 2 development

---

## 🚀 **Next Steps After Testing Success**

1. **Document test results** and coverage metrics
2. **Identify any edge cases** that need additional testing
3. **Plan Phase 2 testing** based on Runtime Module learnings
4. **Prepare for integration testing** with other modules

The Runtime Module testing ensures that the **core execution engine** works reliably and can handle real agentplug agents, providing a solid foundation for the entire system.
