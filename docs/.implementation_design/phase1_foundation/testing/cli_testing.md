# Phase 1: CLI Module Testing Plan

**Document Type**: CLI Module Testing Plan
**Phase**: 1 - Foundation
**Author**: William
**Date Created**: 2025-06-28
**Last Updated**: 2025-06-28
**Status**: Active
**Purpose**: Comprehensive testing for CLI Module functionality

## 🎯 **CLI Module Testing Overview**

### **Module Purpose**
The CLI Module is the **user interface layer** that provides command-line tools for agent management, testing, and system interaction using Click and Rich for a modern, user-friendly experience.

### **Testing Focus**
- **"Can Run" Philosophy**: Test that CLI commands work reliably
- **User Experience**: Ensure clear, helpful user interactions
- **Command Validation**: Test input validation and error handling
- **Integration**: Test coordination with other modules

---

## 🧪 **Unit Testing**

### **Main CLI Entry Unit Tests**

#### **Command Registration**
- [ ] **Test command discovery**: All commands are properly registered
- [ ] **Test command grouping**: Commands are organized in logical groups
- [ ] **Test command aliases**: Command aliases work correctly
- [ ] **Test command help**: Help text is displayed correctly

#### **CLI Framework Integration**
- [ ] **Test Click integration**: Click framework works correctly
- [ ] **Test Rich integration**: Rich formatting works correctly
- [ ] **Test version display**: Version information is displayed correctly
- [ ] **Test error handling**: CLI framework errors are handled gracefully

### **Command Handlers Unit Tests**

#### **List Command Handler**
- [ ] **Test agent listing**: Can list all available agents
- [ ] **Test agent filtering**: Can filter agents by developer or name
- [ ] **Test agent search**: Can search agents by metadata
- [ ] **Test empty results**: Handles no agents gracefully

#### **Info Command Handler**
- [ ] **Test agent information**: Can display detailed agent information
- [ ] **Test manifest display**: Can display agent manifest details
- [ ] **Test interface display**: Can display agent interface details
- [ ] **Test missing agent**: Handles non-existent agents gracefully

#### **Test Command Handler**
- [ ] **Test agent testing**: Can test agent methods
- [ ] **Test parameter passing**: Can pass parameters to agent methods
- [ ] **Test result display**: Can display test results clearly
- [ ] **Test error handling**: Can handle test errors gracefully

#### **Install Command Handler**
- [ ] **Test agent installation**: Can install agents from sources
- [ ] **Test source validation**: Can validate installation sources
- [ ] **Test dependency handling**: Can handle agent dependencies
- [ ] **Test installation verification**: Can verify successful installation

#### **Remove Command Handler**
- [ ] **Test agent removal**: Can remove agents completely
- [ ] **Test dependency cleanup**: Can clean up agent dependencies
- [ ] **Test confirmation**: Can confirm removal actions
- [ ] **Test safe removal**: Prevents accidental removal

### **Output Formatter Unit Tests**

#### **Text Formatting**
- [ ] **Test table formatting**: Can format data in tables
- [ ] **Test list formatting**: Can format data in lists
- [ ] **Test detail formatting**: Can format detailed information
- [ ] **Test error formatting**: Can format error messages clearly

#### **Rich Integration**
- [ ] **Test color output**: Colors are applied correctly
- [ ] **Test style output**: Styles are applied correctly
- **Test progress bars**: Progress bars work correctly
- [ ] **Test status indicators**: Status indicators work correctly

### **Error Handler Unit Tests**

#### **Error Classification**
- [ ] **Test user errors**: User input errors are handled gracefully
- [ ] **Test system errors**: System errors are handled gracefully
- [ ] **Test validation errors**: Validation errors are handled gracefully
- [ ] **Test integration errors**: Integration errors are handled gracefully

#### **Error Reporting**
- [ ] **Test error messages**: Error messages are clear and helpful
- [ ] **Test error suggestions**: Error suggestions are provided when possible
- [ ] **Test error logging**: Errors are logged appropriately
- [ ] **Test error recovery**: System can recover from errors gracefully

---

## 🔗 **Integration Testing**

### **CLI + Storage Integration**

#### **Agent Management Commands**
- [ ] **Test list command**: CLI can list agents through Storage
- [ ] **Test info command**: CLI can get agent info through Storage
- [ ] **Test install command**: CLI can install agents through Storage
- [ ] **Test remove command**: CLI can remove agents through Storage

#### **File Operations**
- [ ] **Test file access**: CLI can access agent files through Storage
- [ ] **Test file validation**: CLI can validate agent files through Storage
- [ ] **Test file operations**: CLI can perform file operations through Storage
- [ ] **Test error handling**: CLI handles Storage errors gracefully

### **CLI + Core Integration**

#### **Agent Loading Commands**
- [ ] **Test agent loading**: CLI can load agents through Core
- [ ] **Test interface validation**: CLI can validate agent interfaces through Core
- [ ] **Test method discovery**: CLI can discover agent methods through Core
- [ ] **Test agent validation**: CLI can validate agents through Core

#### **Agent Coordination**
- [ ] **Test agent registration**: CLI can register agents through Core
- [ ] **Test agent updates**: CLI can update agents through Core
- [ ] **Test agent cleanup**: CLI can clean up agents through Core
- [ ] **Test error handling**: CLI handles Core errors gracefully

### **CLI + Runtime Integration**

#### **Agent Execution Commands**
- [ ] **Test agent execution**: CLI can execute agents through Runtime
- [ ] **Test method execution**: CLI can execute agent methods through Runtime
- [ ] **Test result handling**: CLI can handle execution results through Runtime
- [ ] **Test error handling**: CLI handles Runtime errors gracefully

#### **Execution Coordination**
- [ ] **Test execution flow**: CLI coordinates execution flow through Runtime
- [ ] **Test progress tracking**: CLI tracks execution progress through Runtime
- [ ] **Test timeout handling**: CLI handles timeouts through Runtime
- [ ] **Test resource management**: CLI manages resources through Runtime

---

## 🎯 **End-to-End Testing**

### **Complete User Workflows**

#### **Agent Discovery Workflow**
- [ ] **Test complete discovery**: User can discover agents from start to finish
- [ ] **Test agent listing**: User can see all available agents
- [ ] **Test agent filtering**: User can filter agents by criteria
- [ ] **Test agent search**: User can search for specific agents

#### **Agent Installation Workflow**
- [ ] **Test complete installation**: User can install agents from start to finish
- [ ] **Test source validation**: User gets feedback on installation sources
- [ ] **Test progress indication**: User sees installation progress
- [ ] **Test success confirmation**: User gets confirmation of successful installation

#### **Agent Testing Workflow**
- [ ] **Test complete testing**: User can test agents from start to finish
- [ ] **Test method selection**: User can select methods to test
- [ ] **Test parameter input**: User can input method parameters
- [ ] **Test result display**: User can see test results clearly

#### **Agent Management Workflow**
- [ ] **Test complete management**: User can manage agents from start to finish
- [ ] **Test agent information**: User can get detailed agent information
- [ ] **Test agent updates**: User can update agent information
- [ ] **Test agent removal**: User can remove agents safely

### **Multi-Command Scenarios**

#### **Sequential Commands**
- [ ] **Test command chaining**: User can run multiple commands in sequence
- [ ] **Test state persistence**: Command state persists between commands
- [ ] **Test error recovery**: User can recover from command errors
- [ ] **Test workflow completion**: User can complete multi-step workflows

#### **Interactive Commands**
- [ ] **Test user input**: Commands can accept user input interactively
- [ ] **Test confirmation prompts**: Commands can prompt for confirmation
- [ ] **Test input validation**: User input is validated appropriately
- [ ] **Test input help**: User gets help with input requirements

---

## 🧪 **Test Implementation Examples**

### **Main CLI Test Example**
```python
# tests/phase1_foundation/cli/test_main.py
import pytest
from click.testing import CliRunner
from agenthub.cli.main import cli

class TestMainCLI:
    def test_cli_help(self):
        """Test CLI help display."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])

        assert result.exit_code == 0
        assert "Agent Hub CLI" in result.output
        assert "list" in result.output
        assert "info" in result.output
        assert "test" in result.output
        assert "install" in result.output
        assert "remove" in result.output

    def test_cli_version(self):
        """Test CLI version display."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])

        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_cli_no_args(self):
        """Test CLI with no arguments."""
        runner = CliRunner()
        result = runner.invoke(cli, [])

        assert result.exit_code == 0
        assert "Agent Hub CLI" in result.output
```

### **List Command Test Example**
```python
# tests/phase1_foundation/cli/test_list_command.py
import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
from agenthub.cli.main import cli

class TestListCommand:
    def test_list_agents_success(self):
        """Test successful agent listing."""
        runner = CliRunner()

        # Mock storage manager
        with patch('agenthub.storage.LocalStorageManager') as mock_storage:
            mock_storage.return_value.list_agents.return_value = [
                {
                    "developer": "test-dev",
                    "name": "test-agent",
                    "version": "1.0.0",
                    "description": "A test agent"
                },
                {
                    "developer": "another-dev",
                    "name": "another-agent",
                    "version": "2.0.0",
                    "description": "Another test agent"
                }
            ]

            result = runner.invoke(cli, ['list'])

            assert result.exit_code == 0
            assert "test-dev/test-agent" in result.output
            assert "another-dev/another-agent" in result.output
            assert "1.0.0" in result.output
            assert "2.0.0" in result.output

    def test_list_agents_empty(self):
        """Test agent listing with no agents."""
        runner = CliRunner()

        with patch('agenthub.storage.LocalStorageManager') as mock_storage:
            mock_storage.return_value.list_agents.return_value = []

            result = runner.invoke(cli, ['list'])

            assert result.exit_code == 0
            assert "No agents found" in result.output

    def test_list_agents_filtered(self):
        """Test filtered agent listing."""
        runner = CliRunner()

        with patch('agenthub.storage.LocalStorageManager') as mock_storage:
            mock_storage.return_value.list_agents.return_value = [
                {
                    "developer": "test-dev",
                    "name": "test-agent",
                    "version": "1.0.0"
                }
            ]

            result = runner.invoke(cli, ['list', '--developer', 'test-dev'])

            assert result.exit_code == 0
            assert "test-dev/test-agent" in result.output

    def test_list_agents_error(self):
        """Test agent listing with error."""
        runner = CliRunner()

        with patch('agenthub.storage.LocalStorageManager') as mock_storage:
            mock_storage.return_value.list_agents.side_effect = Exception("Storage error")

            result = runner.invoke(cli, ['list'])

            assert result.exit_code == 1
            assert "Error listing agents" in result.output
            assert "Storage error" in result.output
```

### **Info Command Test Example**
```python
# tests/phase1_foundation/cli/test_info_command.py
import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
from agenthub.cli.main import cli

class TestInfoCommand:
    def test_info_agent_success(self):
        """Test successful agent info display."""
        runner = CliRunner()

        # Mock storage and core managers
        with patch('agenthub.storage.LocalStorageManager') as mock_storage:
            with patch('agenthub.core.agent_loader.AgentLoader') as mock_loader:

                mock_storage.return_value.get_agent_path.return_value = "/path/to/agent"

                mock_agent = Mock()
                mock_agent.name = "test-agent"
                mock_agent.version = "1.0.0"
                mock_agent.description = "A test agent"
                mock_agent.available_methods = {
                    "test_method": {
                        "description": "Test method",
                        "parameters": {
                            "prompt": {"type": "string", "required": True}
                        }
                    }
                }

                mock_loader.return_value.load_agent.return_value = mock_agent

                result = runner.invoke(cli, ['info', 'test-dev/test-agent'])

                assert result.exit_code == 0
                assert "test-agent" in result.output
                assert "1.0.0" in result.output
                assert "A test agent" in result.output
                assert "test_method" in result.output

    def test_info_agent_not_found(self):
        """Test agent info with non-existent agent."""
        runner = CliRunner()

        with patch('agenthub.storage.LocalStorageManager') as mock_storage:
            mock_storage.return_value.get_agent_path.return_value = None

            result = runner.invoke(cli, ['info', 'non-existent/agent'])

            assert result.exit_code == 1
            assert "Agent not found" in result.output

    def test_info_agent_invalid_format(self):
        """Test agent info with invalid agent format."""
        runner = CliRunner()

        result = runner.invoke(cli, ['info', 'invalid-format'])

        assert result.exit_code == 1
        assert "Invalid agent format" in result.output
        assert "Expected: developer/agent" in result.output
```

### **Test Command Test Example**
```python
# tests/phase1_foundation/cli/test_test_command.py
import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
from agenthub.cli.main import cli

class TestTestCommand:
    def test_test_agent_success(self):
        """Test successful agent testing."""
        runner = CliRunner()

        # Mock dependencies
        with patch('agenthub.core.agent_loader.AgentLoader') as mock_loader:
            with patch('agenthub.runtime.agent_runtime.AgentRuntime') as mock_runtime:

                mock_agent = Mock()
                mock_agent.name = "test-agent"
                mock_agent.available_methods = {
                    "test_method": {
                        "description": "Test method",
                        "parameters": {
                            "prompt": {"type": "string", "required": True}
                        }
                    }
                }

                mock_loader.return_value.load_agent.return_value = mock_agent
                mock_runtime.return_value.execute_agent.return_value = {
                    "result": "Test output"
                }

                result = runner.invoke(cli, [
                    'test', 'test-dev/test-agent', 'test_method',
                    '--params', '{"prompt": "Hello World"}'
                ])

                assert result.exit_code == 0
                assert "Test output" in result.output
                assert "Success" in result.output

    def test_test_agent_method_not_found(self):
        """Test agent testing with non-existent method."""
        runner = CliRunner()

        with patch('agenthub.core.agent_loader.AgentLoader') as mock_loader:
            mock_agent = Mock()
            mock_agent.name = "test-agent"
            mock_agent.available_methods = {}

            mock_loader.return_value.load_agent.return_value = mock_agent

            result = runner.invoke(cli, [
                'test', 'test-dev/test-agent', 'non_existent_method'
            ])

            assert result.exit_code == 1
            assert "Method not found" in result.output

    def test_test_agent_invalid_params(self):
        """Test agent testing with invalid parameters."""
        runner = CliRunner()

        with patch('agenthub.core.agent_loader.AgentLoader') as mock_loader:
            mock_agent = Mock()
            mock_agent.name = "test-agent"
            mock_agent.available_methods = {
                "test_method": {
                    "description": "Test method",
                    "parameters": {
                        "prompt": {"type": "string", "required": True}
                    }
                }
            }

            mock_loader.return_value.load_agent.return_value = mock_agent

            result = runner.invoke(cli, [
                'test', 'test-dev/test-agent', 'test_method',
                '--params', 'invalid-json'
            ])

            assert result.exit_code == 1
            assert "Invalid JSON parameters" in result.output

    def test_test_agent_execution_error(self):
        """Test agent testing with execution error."""
        runner = CliRunner()

        with patch('agenthub.core.agent_loader.AgentLoader') as mock_loader:
            with patch('agenthub.runtime.agent_runtime.AgentRuntime') as mock_runtime:

                mock_agent = Mock()
                mock_agent.name = "test-agent"
                mock_agent.available_methods = {
                    "test_method": {
                        "description": "Test method",
                        "parameters": {}
                    }
                }

                mock_loader.return_value.load_agent.return_value = mock_agent
                mock_runtime.return_value.execute_agent.side_effect = Exception("Execution error")

                result = runner.invoke(cli, [
                    'test', 'test-dev/test-agent', 'test_method'
                ])

                assert result.exit_code == 1
                assert "Execution error" in result.output
```

### **Install Command Test Example**
```python
# tests/phase1_foundation/cli/test_install_command.py
import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
from agenthub.cli.main import cli

class TestInstallCommand:
    def test_install_agent_success(self):
        """Test successful agent installation."""
        runner = CliRunner()

        with patch('agenthub.storage.agent_manager.AgentManager') as mock_manager:
            mock_manager.return_value.install_agent.return_value = {
                "success": True,
                "message": "Agent installed successfully"
            }

            result = runner.invoke(cli, [
                'install', 'test-dev/test-agent', '/path/to/source'
            ])

            assert result.exit_code == 0
            assert "Agent installed successfully" in result.output
            assert "Success" in result.output

    def test_install_agent_source_not_found(self):
        """Test agent installation with non-existent source."""
        runner = CliRunner()

        result = runner.invoke(cli, [
            'install', 'test-dev/test-agent', '/non/existent/path'
        ])

        assert result.exit_code == 1
        assert "Source path not found" in result.output

    def test_install_agent_invalid_format(self):
        """Test agent installation with invalid agent format."""
        runner = CliRunner()

        result = runner.invoke(cli, ['install', 'invalid-format', '/path/to/source'])

        assert result.exit_code == 1
        assert "Invalid agent format" in result.output

    def test_install_agent_installation_error(self):
        """Test agent installation with installation error."""
        runner = CliRunner()

        with patch('agenthub.storage.agent_manager.AgentManager') as mock_manager:
            mock_manager.return_value.install_agent.return_value = {
                "success": False,
                "error": "Installation failed"
            }

            result = runner.invoke(cli, [
                'install', 'test-dev/test-agent', '/path/to/source'
            ])

            assert result.exit_code == 1
            assert "Installation failed" in result.output
```

---

## 📊 **Test Coverage Requirements**

### **Line Coverage Targets**
- **Main CLI Entry**: 90%+ line coverage
- **Command Handlers**: 85%+ line coverage
- **Output Formatter**: 90%+ line coverage
- **Error Handler**: 85%+ line coverage
- **Overall CLI Module**: 87%+ line coverage

### **Branch Coverage Targets**
- **Success Paths**: 100% coverage
- **Error Paths**: 80%+ coverage
- **Edge Cases**: 75%+ coverage

---

## 🚨 **Test Failure Scenarios**

### **Common Failure Modes**
- [ ] **User input errors**: Invalid commands, malformed parameters
- [ ] **System errors**: File system errors, permission issues
- [ ] **Integration errors**: Module coordination failures
- [ ] **Display errors**: Output formatting issues, color problems
- [ ] **Framework errors**: Click or Rich framework issues

### **Error Recovery Testing**
- [ ] **Test graceful degradation**: CLI continues working after failures
- [ ] **Test error reporting**: Clear error messages for users
- [ ] **Test recovery mechanisms**: CLI can recover from failures
- [ ] **Test user guidance**: CLI provides helpful guidance after errors

---

## 🎯 **CLI Module Success Criteria**

### **Functional Success**
- [ ] **Can list agents**: User can see all available agents
- [ ] **Can get agent info**: User can get detailed agent information
- [ ] **Can test agents**: User can test agent methods
- [ ] **Can install agents**: User can install new agents
- [ ] **Can remove agents**: User can remove existing agents

### **User Experience Success**
- [ ] **Clear commands**: Commands are intuitive and easy to use
- [ ] **Helpful output**: Output is clear and informative
- [ ] **Error guidance**: Errors provide helpful guidance
- [ ] **Progress indication**: Long operations show progress

### **Integration Success**
- [ ] **Works with Storage Module**: Can manage agents through Storage
- [ ] **Works with Core Module**: Can load and validate agents through Core
- [ ] **Works with Runtime Module**: Can execute agents through Runtime
- [ ] **Works with real agents**: Can handle actual agentplug agents

---

## 📋 **Testing Checklist**

### **Pre-Testing Setup**
- [ ] Test environment configured
- [ ] Test agents prepared
- [ ] Mock dependencies configured
- [ ] CLI framework configured

### **Unit Testing**
- [ ] Main CLI Entry tests pass
- [ ] Command Handler tests pass
- [ ] Output Formatter tests pass
- [ ] Error Handler tests pass
- [ ] Coverage targets met

### **Integration Testing**
- [ ] CLI + Storage integration tests pass
- [ ] CLI + Core integration tests pass
- [ ] CLI + Runtime integration tests pass
- [ ] Cross-module coordination works

### **End-to-End Testing**
- [ ] Complete user workflows work
- [ ] Commands work correctly
- [ ] Error handling works correctly
- [ ] Real agentplug agents can be managed

### **Final Validation**
- [ ] All tests pass consistently
- [ ] User experience requirements met
- [ ] Integration points validated
- [ ] Ready for Phase 2 development

---

## 🚀 **Next Steps After Testing Success**

1. **Document test results** and coverage metrics
2. **Identify any edge cases** that need additional testing
3. **Plan Phase 2 testing** based on CLI Module learnings
4. **Prepare for integration testing** with other modules

The CLI Module testing ensures that the **user interface layer** works reliably and provides a great user experience, making the system accessible and easy to use.
