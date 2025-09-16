# Phase 1: Core Module Testing Plan

**Document Type**: Core Module Testing Plan
**Phase**: 1 - Foundation
**Author**: William
**Date Created**: 2025-06-28
**Last Updated**: 2025-06-28
**Status**: Active
**Purpose**: Comprehensive testing for Core Module functionality

## 🎯 **Core Module Testing Overview**

### **Module Purpose**
The Core Module is the **central coordination hub** that handles agent loading, manifest parsing, interface validation, and provides the main `AgentWrapper` class for user interaction.

### **Testing Focus**
- **"Can Run" Philosophy**: Test that agents can be loaded and wrapped successfully
- **Interface Validation**: Ensure agent interfaces are correctly validated
- **Dynamic Method Dispatch**: Test the `__getattr__` magic method functionality
- **Integration Coordination**: Test coordination with other modules

---

## 🧪 **Unit Testing**

### **Agent Loader Unit Tests**

#### **Agent Discovery**
- [ ] **Test agent path resolution**: Correctly resolves agent paths
- [ ] **Test agent existence check**: Can check if agents exist
- [ ] **Test agent validation**: Validates agent directory structure
- [ ] **Test agent loading**: Can load valid agents successfully

#### **Agent Initialization**
- [ ] **Test manifest loading**: Loads agent.yaml files correctly
- [ ] **Test interface parsing**: Parses agent interfaces correctly
- [ ] **Test dependency resolution**: Resolves agent dependencies
- [ ] **Test agent wrapper creation**: Creates AgentWrapper instances

#### **Error Handling**
- [ ] **Test missing agent**: Handles non-existent agents gracefully
- [ ] **Test invalid manifest**: Handles corrupted agent.yaml files
- [ ] **Test missing files**: Handles missing agent.py or requirements.txt
- [ ] **Test permission errors**: Handles file permission issues

### **Manifest Parser Unit Tests**

#### **YAML Parsing**
- [ ] **Test valid YAML**: Correctly parses valid YAML content
- [ ] **Test YAML syntax errors**: Handles malformed YAML gracefully
- [ ] **Test encoding issues**: Handles different text encodings
- [ ] **Test large manifests**: Handles large manifest files

#### **Schema Validation**
- [ ] **Test required fields**: Validates required manifest fields
- [ ] **Test field types**: Validates field data types
- [ ] **Test field constraints**: Validates field constraints (e.g., version format)
- [ ] **Test nested structures**: Validates nested interface definitions

#### **Interface Parsing**
- [ ] **Test method definitions**: Correctly parses method definitions
- [ ] **Test parameter definitions**: Correctly parses parameter definitions
- [ ] **Test return definitions**: Correctly parses return definitions
- [ ] **Test method metadata**: Correctly parses method descriptions and examples

### **Interface Validator Unit Tests**

#### **Method Validation**
- [ ] **Test method existence**: Validates that methods exist in agent.py
- [ ] **Test method signature**: Validates method parameter signatures
- [ ] **Test method accessibility**: Validates method accessibility
- [ ] **Test method documentation**: Validates method documentation

#### **Parameter Validation**
- [ ] **Test parameter types**: Validates parameter type definitions
- [ ] **Test required parameters**: Validates required parameter handling
- [ ] **Test parameter constraints**: Validates parameter constraints
- [ ] **Test parameter defaults**: Validates parameter default values

#### **Return Validation**
- [ ] **Test return type validation**: Validates return type definitions
- [ ] **Test return constraints**: Validates return value constraints
- [ ] **Test return documentation**: Validates return documentation
- [ ] **Test return examples**: Validates return value examples

### **Agent Manager Unit Tests**

#### **Agent Registration**
- [ ] **Test agent registration**: Can register agents in the system
- [ ] **Test agent lookup**: Can find registered agents by name
- [ ] **Test agent listing**: Can list all registered agents
- [ ] **Test agent removal**: Can remove agents from registration

#### **Agent Lifecycle**
- [ ] **Test agent initialization**: Agents are properly initialized
- [ ] **Test agent validation**: Agents are validated during registration
- [ ] **Test agent cleanup**: Agents are properly cleaned up
- [ ] **Test agent updates**: Agents can be updated and re-registered

---

## 🔗 **Integration Testing**

### **Core + Storage Integration**

#### **Agent File Access**
- [ ] **Test manifest loading**: Core can load manifests from Storage
- [ ] **Test agent discovery**: Core can discover agents through Storage
- [ ] **Test file validation**: Core can validate agent files through Storage
- [ ] **Test metadata coordination**: Core and Storage maintain consistent metadata

#### **Agent Installation**
- [ ] **Test agent installation flow**: Core coordinates with Storage for installation
- [ ] **Test agent validation**: Core validates newly installed agents
- [ ] **Test agent registration**: Core registers newly installed agents
- [ ] **Test error handling**: Core handles Storage errors gracefully

### **Core + Runtime Integration**

#### **Agent Execution**
- [ ] **Test method validation**: Core validates methods before Runtime execution
- [ ] **Test parameter validation**: Core validates parameters before Runtime execution
- [ ] **Test interface coordination**: Core and Runtime maintain interface consistency
- [ ] **Test error propagation**: Core handles Runtime errors gracefully

#### **Agent Coordination**
- [ ] **Test agent loading**: Core loads agents for Runtime execution
- [ ] **Test method discovery**: Core discovers methods for Runtime execution
- [ ] **Test result handling**: Core processes Runtime execution results
- [ ] **Test error handling**: Core handles Runtime execution errors

### **Core + CLI Integration**

#### **Command Coordination**
- [ ] **Test agent listing**: CLI can list agents through Core
- [ ] **Test agent info**: CLI can display agent information through Core
- [ ] **Test agent validation**: CLI can validate agents through Core
- [ ] **Test error display**: CLI displays Core errors clearly

#### **User Interface**
- [ ] **Test progress indication**: CLI shows Core operation progress
- [ ] **Test result display**: CLI displays Core operation results
- [ ] **Test error reporting**: CLI reports Core errors clearly
- [ ] **Test user feedback**: CLI provides helpful user feedback

---

## 🎯 **End-to-End Testing**

### **Complete Agent Loading Workflow**

#### **Agent Discovery to Loading**
- [ ] **Test complete workflow**: User can discover and load agents
- [ ] **Test manifest parsing**: Agent manifests are parsed correctly
- [ ] **Test interface validation**: Agent interfaces are validated
- [ ] **Test wrapper creation**: AgentWrapper instances are created

#### **Method Discovery to Execution**
- [ ] **Test method discovery**: Available methods are discovered automatically
- [ ] **Test method validation**: Methods are validated before execution
- [ ] **Test parameter validation**: Parameters are validated before execution
- [ ] **Test execution coordination**: Methods are executed through Runtime

### **Multi-Agent Scenarios**

#### **Agent Coordination**
- [ ] **Test multiple agents**: Can load and manage multiple agents
- [ ] **Test agent isolation**: Agents don't interfere with each other
- [ ] **Test agent dependencies**: Handles agent dependencies correctly
- [ ] **Test agent updates**: Can update and reload agents

#### **Interface Consistency**
- [ ] **Test interface validation**: Maintains interface consistency across agents
- [ ] **Test method conflicts**: Handles method name conflicts gracefully
- [ ] **Test parameter conflicts**: Handles parameter conflicts gracefully
- [ ] **Test return conflicts**: Handles return value conflicts gracefully

---

## 🧪 **Test Implementation Examples**

### **Agent Loader Test Example**
```python
# tests/phase1_foundation/core/test_agent_loader.py
import pytest
from pathlib import Path
from agenthub.core.agent_loader import AgentLoader

class TestAgentLoader:
    def test_load_valid_agent(self, tmp_path):
        """Test loading a valid agent."""
        loader = AgentLoader()

        # Create test agent
        agent_dir = tmp_path / "test-agent"
        agent_dir.mkdir()

        # Create valid manifest
        manifest_file = agent_dir / "agent.yaml"
        manifest_file.write_text("""
name: test-agent
version: 1.0.0
description: A test agent
interface:
  methods:
    test_method:
      description: Test method
      parameters:
        prompt:
          type: string
          required: true
      returns:
        type: string
        description: Test result
        """)

        # Create agent script
        agent_script = agent_dir / "agent.py"
        agent_script.write_text("""
def test_method(prompt):
    return f"Processed: {prompt}"
        """)

        # Load agent
        agent = loader.load_agent(str(agent_dir))

        assert agent is not None
        assert agent.name == "test-agent"
        assert "test_method" in agent.available_methods
        assert agent.available_methods["test_method"]["description"] == "Test method"

    def test_load_invalid_agent(self, tmp_path):
        """Test loading an invalid agent."""
        loader = AgentLoader()

        # Create invalid agent (missing manifest)
        agent_dir = tmp_path / "invalid-agent"
        agent_dir.mkdir()

        # Try to load invalid agent
        with pytest.raises(ValueError, match="Missing agent.yaml"):
            loader.load_agent(str(agent_dir))

    def test_load_corrupted_manifest(self, tmp_path):
        """Test loading agent with corrupted manifest."""
        loader = AgentLoader()

        # Create agent with corrupted manifest
        agent_dir = tmp_path / "corrupted-agent"
        agent_dir.mkdir()

        manifest_file = agent_dir / "agent.yaml"
        manifest_file.write_text("""
name: test-agent
version: 1.0.0
interface:
  methods:
    test_method:
      description: Test method
      parameters:
        prompt:
          type: string
          required: true
      returns:
        type: string
        description: Test result
        # Missing closing brace
        """)

        # Try to load corrupted agent
        with pytest.raises(ValueError, match="Invalid YAML"):
            loader.load_agent(str(agent_dir))
```

### **Manifest Parser Test Example**
```python
# tests/phase1_foundation/core/test_manifest_parser.py
import pytest
from agenthub.core.manifest_parser import ManifestParser

class TestManifestParser:
    def test_parse_valid_manifest(self):
        """Test parsing a valid manifest."""
        parser = ManifestParser()

        manifest_content = """
name: test-agent
version: 1.0.0
description: A test agent
interface:
  methods:
    test_method:
      description: Test method
      parameters:
        prompt:
          type: string
          required: true
          description: Input prompt
        max_length:
          type: integer
          required: false
          default: 100
          description: Maximum output length
      returns:
        type: string
        description: Processed result
        example: "Processed: Hello World"
        """

        manifest = parser.parse_manifest_from_string(manifest_content)

        assert manifest["name"] == "test-agent"
        assert manifest["version"] == "1.0.0"
        assert manifest["description"] == "A test agent"

        # Check method definition
        method = manifest["interface"]["methods"]["test_method"]
        assert method["description"] == "Test method"

        # Check parameters
        prompt_param = method["parameters"]["prompt"]
        assert prompt_param["type"] == "string"
        assert prompt_param["required"] is True

        max_length_param = method["parameters"]["max_length"]
        assert max_length_param["type"] == "integer"
        assert max_length_param["required"] is False
        assert max_length_param["default"] == 100

        # Check returns
        returns = method["returns"]
        assert returns["type"] == "string"
        assert returns["description"] == "Processed result"
        assert returns["example"] == "Processed: Hello World"

    def test_validate_manifest_schema(self):
        """Test manifest schema validation."""
        parser = ManifestParser()

        # Valid manifest
        valid_manifest = {
            "name": "test-agent",
            "version": "1.0.0",
            "interface": {
                "methods": {
                    "test_method": {
                        "description": "Test method",
                        "parameters": {},
                        "returns": {
                            "type": "string",
                            "description": "Test result"
                        }
                    }
                }
            }
        }

        result = parser.validate_manifest(valid_manifest)
        assert result["valid"] is True

        # Invalid manifest (missing required fields)
        invalid_manifest = {
            "name": "test-agent"
            # Missing version and interface
        }

        result = parser.validate_manifest(invalid_manifest)
        assert result["valid"] is False
        assert "version" in result["errors"]
        assert "interface" in result["errors"]
```

### **Interface Validator Test Example**
```python
# tests/phase1_foundation/core/test_interface_validator.py
import pytest
from pathlib import Path
from agenthub.core.interface_validator import InterfaceValidator

class TestInterfaceValidator:
    def test_validate_method_existence(self, tmp_path):
        """Test method existence validation."""
        validator = InterfaceValidator()

        # Create test agent script
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("""
def test_method(prompt):
    return f"Processed: {prompt}"

def another_method():
    return "Hello World"
        """)

        # Define interface
        interface = {
            "methods": {
                "test_method": {
                    "description": "Test method",
                    "parameters": {
                        "prompt": {"type": "string", "required": True}
                    }
                },
                "another_method": {
                    "description": "Another method",
                    "parameters": {}
                }
            }
        }

        # Validate interface
        result = validator.validate_interface(str(agent_script), interface)
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_missing_method(self, tmp_path):
        """Test validation of missing method."""
        validator = InterfaceValidator()

        # Create test agent script (missing method)
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("""
def test_method(prompt):
    return f"Processed: {prompt}"
        """)

        # Define interface with missing method
        interface = {
            "methods": {
                "test_method": {
                    "description": "Test method",
                    "parameters": {
                        "prompt": {"type": "string", "required": True}
                    }
                },
                "missing_method": {
                    "description": "Missing method",
                    "parameters": {}
                }
            }
        }

        # Validate interface
        result = validator.validate_interface(str(agent_script), interface)
        assert result["valid"] is False
        assert "missing_method" in result["errors"]
        assert "not found in agent.py" in result["errors"]["missing_method"]

    def test_validate_parameter_signature(self, tmp_path):
        """Test parameter signature validation."""
        validator = InterfaceValidator()

        # Create test agent script
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("""
def test_method(prompt, max_length=100):
    return f"Processed: {prompt}"[:max_length]
        """)

        # Define interface with parameter mismatch
        interface = {
            "methods": {
                "test_method": {
                    "description": "Test method",
                    "parameters": {
                        "prompt": {"type": "string", "required": True},
                        "max_length": {"type": "integer", "required": False, "default": 50}
                    }
                }
            }
        }

        # Validate interface
        result = validator.validate_interface(str(agent_script), interface)
        assert result["valid"] is True  # Should pass as parameters match
```

### **AgentWrapper Test Example**
```python
# tests/phase1_foundation/core/test_agent_wrapper.py
import pytest
from unittest.mock import Mock, patch
from agenthub.core.agent_wrapper import AgentWrapper

class TestAgentWrapper:
    def test_method_discovery(self):
        """Test method discovery through __getattr__."""
        # Create mock runtime
        mock_runtime = Mock()
        mock_runtime.execute_agent.return_value = {"result": "success"}

        # Create agent wrapper
        agent = AgentWrapper(
            name="test-agent",
            path="/path/to/agent",
            interface={
                "methods": {
                    "test_method": {
                        "description": "Test method",
                        "parameters": {
                            "prompt": {"type": "string", "required": True}
                        }
                    }
                }
            },
            runtime=mock_runtime
        )

        # Test method discovery
        assert "test_method" in agent.available_methods
        assert agent.available_methods["test_method"]["description"] == "Test method"

        # Test method execution
        result = agent.test_method("Hello World")
        assert result["result"] == "success"

        # Verify runtime was called
        mock_runtime.execute_agent.assert_called_once_with(
            agent_path="/path/to/agent",
            method="test_method",
            parameters={"prompt": "Hello World"}
        )

    def test_invalid_method_call(self):
        """Test calling non-existent method."""
        # Create mock runtime
        mock_runtime = Mock()

        # Create agent wrapper
        agent = AgentWrapper(
            name="test-agent",
            path="/path/to/agent",
            interface={"methods": {}},
            runtime=mock_runtime
        )

        # Test calling non-existent method
        with pytest.raises(AttributeError, match="Agent 'test-agent' has no method 'invalid_method'"):
            agent.invalid_method()

        # Verify runtime was not called
        mock_runtime.execute_agent.assert_not_called()

    def test_parameter_validation(self):
        """Test parameter validation before execution."""
        # Create mock runtime
        mock_runtime = Mock()

        # Create agent wrapper with required parameters
        agent = AgentWrapper(
            name="test-agent",
            path="/path/to/agent",
            interface={
                "methods": {
                    "test_method": {
                        "description": "Test method",
                        "parameters": {
                            "prompt": {"type": "string", "required": True},
                            "max_length": {"type": "integer", "required": False, "default": 100}
                        }
                    }
                }
            },
            runtime=mock_runtime
        )

        # Test missing required parameter
        with pytest.raises(ValueError, match="Missing required parameter 'prompt'"):
            agent.test_method()

        # Test with required parameter
        result = agent.test_method("Hello World")
        assert result["result"] == "success"

        # Verify runtime was called with correct parameters
        mock_runtime.execute_agent.assert_called_once_with(
            agent_path="/path/to/agent",
            method="test_method",
            parameters={"prompt": "Hello World", "max_length": 100}
        )
```

---

## 📊 **Test Coverage Requirements**

### **Line Coverage Targets**
- **Agent Loader**: 90%+ line coverage
- **Manifest Parser**: 95%+ line coverage
- **Interface Validator**: 90%+ line coverage
- **Agent Manager**: 85%+ line coverage
- **Agent Wrapper**: 95%+ line coverage
- **Overall Core Module**: 92%+ line coverage

### **Branch Coverage Targets**
- **Success Paths**: 100% coverage
- **Error Paths**: 85%+ coverage
- **Edge Cases**: 80%+ coverage

---

## 🚨 **Test Failure Scenarios**

### **Common Failure Modes**
- [ ] **Manifest parsing errors**: Invalid YAML, missing fields, type mismatches
- [ ] **Interface validation errors**: Missing methods, parameter mismatches
- [ ] **Agent loading errors**: File not found, permission denied, corrupted files
- [ ] **Method execution errors**: Runtime errors, parameter validation failures
- [ ] **Integration errors**: Module coordination failures, data inconsistencies

### **Error Recovery Testing**
- [ ] **Test graceful degradation**: System continues working after failures
- [ ] **Test error reporting**: Clear error messages for users
- [ ] **Test recovery mechanisms**: System can recover from failures
- [ ] **Test data consistency**: Data remains consistent after failures

---

## 🎯 **Core Module Success Criteria**

### **Functional Success**
- [ ] **Can load agentplug agents**: Real agents can be loaded and wrapped
- [ ] **Interface validation works**: Agent interfaces are correctly validated
- [ ] **Method dispatch works**: Dynamic method calls work correctly
- [ ] **Integration works**: Coordinates with other modules correctly

### **Performance Success**
- [ ] **Agent loading < 500ms**: Fast agent loading and validation
- [ ] **Method discovery < 10ms**: Fast method discovery and validation
- [ ] **Interface validation < 100ms**: Fast interface validation
- [ ] **Concurrent loading**: Can handle multiple agents simultaneously

### **Integration Success**
- [ ] **Works with Storage Module**: Can load agents from Storage
- [ ] **Works with Runtime Module**: Can coordinate agent execution
- [ ] **Works with CLI Module**: Can provide agent information
- [ ] **Works with real agents**: Can handle actual agentplug agents

---

## 📋 **Testing Checklist**

### **Pre-Testing Setup**
- [ ] Test environment configured
- [ ] Test agents prepared
- [ ] Test manifests created
- [ ] Mock dependencies configured

### **Unit Testing**
- [ ] Agent Loader tests pass
- [ ] Manifest Parser tests pass
- [ ] Interface Validator tests pass
- [ ] Agent Manager tests pass
- [ ] Agent Wrapper tests pass
- [ ] Coverage targets met

### **Integration Testing**
- [ ] Core + Storage integration tests pass
- [ ] Core + Runtime integration tests pass
- [ ] Core + CLI integration tests pass
- [ ] Cross-module coordination works

### **End-to-End Testing**
- [ ] Complete agent loading workflows work
- [ ] Interface validation works correctly
- [ ] Method dispatch works correctly
- [ ] Real agentplug agents can be loaded

### **Final Validation**
- [ ] All tests pass consistently
- [ ] Performance requirements met
- [ ] Integration points validated
- [ ] Ready for Phase 2 development

---

## 🚀 **Next Steps After Testing Success**

1. **Document test results** and coverage metrics
2. **Identify any edge cases** that need additional testing
3. **Plan Phase 2 testing** based on Core Module learnings
4. **Prepare for integration testing** with other modules

The Core Module testing ensures that the **central coordination hub** works reliably and can handle real agentplug agents, providing a solid foundation for the entire system.
