# Phase 1: Storage Module Testing Plan

**Document Type**: Storage Module Testing Plan
**Phase**: 1 - Foundation
**Author**: William
**Date Created**: 2025-06-28
**Last Updated**: 2025-06-28
**Status**: Active
**Purpose**: Comprehensive testing for Storage Module functionality

## 🎯 **Storage Module Testing Overview**

### **Module Purpose**
The Storage Module is the **data management foundation** that handles file system operations, agent directory management, metadata storage, and file operations for the Agent Hub system.

### **Testing Focus**
- **"Can Run" Philosophy**: Test that file operations work reliably
- **Data Integrity**: Ensure agent data is stored and retrieved correctly
- **File System Operations**: Validate directory and file management
- **Metadata Management**: Test agent manifest and metadata handling

---

## 🧪 **Unit Testing**

### **Local Storage Manager Unit Tests**

#### **Directory Structure Management**
- [ ] **Test base directory creation**: Can create `~/.agenthub/` directory
- [ ] **Test subdirectory creation**: Can create agents, cache, config, logs directories
- [ ] **Test agent directory creation**: Can create developer/agent subdirectories
- [ ] **Test directory permissions**: Sets correct permissions on created directories

#### **File Operations**
- [ ] **Test file creation**: Can create agent.yaml, agent.py, requirements.txt files
- [ ] **Test file reading**: Can read and parse various file types
- [ ] **Test file writing**: Can write data to files correctly
- [ ] **Test file deletion**: Can remove files and directories safely

#### **Path Resolution**
- [ ] **Test absolute path resolution**: Correctly resolves absolute paths
- [ ] **Test relative path resolution**: Handles relative paths correctly
- [ ] **Test home directory expansion**: Expands `~` to user home directory
- [ ] **Test path normalization**: Normalizes paths across platforms

### **Agent Manager Unit Tests**

#### **Agent Discovery**
- [ ] **Test agent listing**: Can list all available agents
- [ ] **Test agent filtering**: Can filter agents by developer or name
- [ ] **Test agent search**: Can search agents by metadata
- [ ] **Test agent validation**: Can validate agent directory structures

#### **Agent Installation**
- [ ] **Test agent directory creation**: Creates proper agent directory structure
- [ ] **Test file copying**: Copies agent files to correct locations
- [ ] **Test dependency handling**: Manages requirements.txt and dependencies
- [ ] **Test installation verification**: Verifies successful installation

#### **Agent Removal**
- [ ] **Test agent uninstallation**: Removes agent directories completely
- [ ] **Test dependency cleanup**: Cleans up virtual environments
- [ ] **Test metadata cleanup**: Removes agent metadata
- [ ] **Test safe removal**: Prevents accidental deletion of system files

### **Metadata Manager Unit Tests**

#### **Manifest Parsing**
- [ ] **Test YAML parsing**: Correctly parses agent.yaml files
- [ ] **Test schema validation**: Validates manifest against schema
- [ ] **Test required fields**: Checks for required manifest fields
- [ ] **Test field types**: Validates field data types

#### **Metadata Storage**
- [ ] **Test metadata creation**: Creates .metadata.json files
- [ ] **Test metadata updates**: Updates existing metadata correctly
- [ ] **Test metadata retrieval**: Retrieves metadata efficiently
- [ ] **Test metadata validation**: Ensures metadata consistency

#### **Cache Management**
- [ ] **Test cache creation**: Creates cache directories and files
- [ ] **Test cache invalidation**: Invalidates stale cache entries
- [ ] **Test cache cleanup**: Removes old cache files
- [ ] **Test cache performance**: Cache operations are fast

### **File Manager Unit Tests**

#### **File Type Handling**
- [ ] **Test Python file handling**: Correctly handles .py files
- [ ] **Test YAML file handling**: Correctly handles .yaml files
- [ ] **Test requirements handling**: Correctly handles requirements.txt
- [ ] **Test binary file handling**: Correctly handles binary files

#### **File Validation**
- [ ] **Test file existence**: Checks if files exist before operations
- [ ] **Test file permissions**: Validates file permissions
- [ ] **Test file integrity**: Checks file integrity and corruption
- [ ] **Test file size limits**: Respects file size limits

---

## 🔗 **Integration Testing**

### **Storage + Runtime Integration**

#### **Agent File Access**
- [ ] **Test agent script access**: Runtime can access agent.py files
- [ ] **Test manifest access**: Runtime can read agent.yaml files
- [ ] **Test dependency access**: Runtime can access requirements.txt
- [ ] **Test environment access**: Runtime can access virtual environments

#### **File Path Coordination**
- [ ] **Test path resolution**: Storage and Runtime use consistent paths
- [ ] **Test file locking**: Prevents concurrent file access conflicts
- [ ] **Test file sharing**: Multiple components can access same files
- [ ] **Test file synchronization**: File changes are visible to all components

### **Storage + Core Integration**

#### **Agent Loading**
- [ ] **Test agent discovery**: Core can discover agents through Storage
- [ ] **Test manifest loading**: Core can load manifests from Storage
- [ ] **Test interface validation**: Core can validate agent interfaces
- [ ] **Test agent registration**: Core can register agents with Storage

#### **Metadata Coordination**
- [ ] **Test metadata consistency**: Storage and Core maintain consistent metadata
- [ ] **Test validation flow**: Validation flows correctly between modules
- [ ] **Test error handling**: Storage errors are handled by Core
- [ ] **Test data integrity**: Data remains consistent across modules

### **Storage + CLI Integration**

#### **Command Execution**
- [ ] **Test list command**: CLI can list agents through Storage
- [ ] **Test install command**: CLI can install agents through Storage
- [ ] **Test remove command**: CLI can remove agents through Storage
- [ ] **Test info command**: CLI can display agent information

#### **User Interface**
- [ ] **Test progress display**: CLI shows file operation progress
- [ ] **Test error display**: CLI shows storage operation errors
- [ ] **Test success confirmation**: CLI confirms successful operations
- [ ] **Test user feedback**: CLI provides helpful user feedback

---

## 🎯 **End-to-End Testing**

### **Complete Agent Lifecycle**

#### **Agent Installation Workflow**
- [ ] **Test complete installation**: User can install agent from start to finish
- [ ] **Test directory creation**: Proper directory structure is created
- [ ] **Test file copying**: All agent files are copied correctly
- [ ] **Test metadata creation**: Agent metadata is created and stored

#### **Agent Execution Workflow**
- [ ] **Test agent loading**: System can load installed agents
- [ ] **Test method execution**: Agent methods can be executed
- [ ] **Test result handling**: Execution results are handled correctly
- [ ] **Test cleanup**: Resources are cleaned up after execution

#### **Agent Removal Workflow**
- [ ] **Test complete removal**: User can remove agent completely
- [ ] **Test file cleanup**: All agent files are removed
- [ ] **Test dependency cleanup**: Virtual environments are cleaned up
- [ ] **Test metadata cleanup**: Agent metadata is removed

### **Multi-Agent Scenarios**

#### **Concurrent Operations**
- [ ] **Test multiple installations**: Can install multiple agents simultaneously
- [ ] **Test multiple executions**: Can execute multiple agents simultaneously
- [ ] **Test mixed operations**: Can perform different operations simultaneously
- [ ] **Test resource sharing**: Agents can share common resources

#### **Agent Dependencies**
- [ ] **Test shared dependencies**: Agents can share common dependencies
- [ ] **Test dependency conflicts**: Handles dependency conflicts gracefully
- [ ] **Test dependency updates**: Updates shared dependencies correctly
- [ ] **Test dependency isolation**: Maintains dependency isolation when needed

---

## 🧪 **Test Implementation Examples**

### **Local Storage Manager Test Example**
```python
# tests/phase1_foundation/storage/test_local_storage.py
import pytest
from pathlib import Path
from agenthub.storage.local_storage import LocalStorageManager

class TestLocalStorage:
    def test_create_base_directory(self, tmp_path):
        """Test base directory creation."""
        storage = LocalStorageManager(base_path=tmp_path)

        # Test base directory creation
        storage.create_base_directory()
        assert (tmp_path / ".agenthub").exists()
        assert (tmp_path / ".agenthub" / "agents").exists()
        assert (tmp_path / ".agenthub" / "cache").exists()
        assert (tmp_path / ".agenthub" / "config").exists()
        assert (tmp_path / ".agenthub" / "logs").exists()

    def test_create_agent_directory(self, tmp_path):
        """Test agent directory creation."""
        storage = LocalStorageManager(base_path=tmp_path)

        # Create base directory first
        storage.create_base_directory()

        # Create agent directory
        agent_path = storage.create_agent_directory("test-dev", "test-agent")
        assert agent_path.exists()
        assert (agent_path / "agent.yaml").exists()
        assert (agent_path / "agent.py").exists()
        assert (agent_path / "requirements.txt").exists()
        assert (agent_path / "venv").exists()

    def test_list_agents(self, tmp_path):
        """Test agent listing."""
        storage = LocalStorageManager(base_path=tmp_path)

        # Create base directory
        storage.create_base_directory()

        # Create test agents
        storage.create_agent_directory("dev1", "agent1")
        storage.create_agent_directory("dev2", "agent2")

        # List agents
        agents = storage.list_agents()
        assert len(agents) == 2

        agent_names = [f"{a['developer']}/{a['name']}" for a in agents]
        assert "dev1/agent1" in agent_names
        assert "dev2/agent2" in agent_names
```

### **Agent Manager Test Example**
```python
# tests/phase1_foundation/storage/test_agent_manager.py
import pytest
from agenthub.storage.agent_manager import AgentManager

class TestAgentManager:
    def test_install_agent(self, tmp_path):
        """Test agent installation."""
        manager = AgentManager(base_path=tmp_path)

        # Create source agent directory
        source_dir = tmp_path / "source-agent"
        source_dir.mkdir()
        (source_dir / "agent.yaml").write_text("""
name: test-agent
version: 1.0.0
interface:
  methods:
    test_method:
      description: Test method
        """)
        (source_dir / "agent.py").write_text("print('Hello World')")
        (source_dir / "requirements.txt").write_text("requests>=2.31.0")

        # Install agent
        result = manager.install_agent("test-dev", "test-agent", str(source_dir))
        assert result["success"] is True

        # Verify installation
        agent_path = tmp_path / ".agenthub" / "agents" / "test-dev" / "test-agent"
        assert agent_path.exists()
        assert (agent_path / "agent.yaml").exists()
        assert (agent_path / "agent.py").exists()
        assert (agent_path / "requirements.txt").exists()

    def test_remove_agent(self, tmp_path):
        """Test agent removal."""
        manager = AgentManager(base_path=tmp_path)

        # Create and install agent first
        source_dir = tmp_path / "source-agent"
        source_dir.mkdir()
        (source_dir / "agent.yaml").write_text("name: test-agent")
        (source_dir / "agent.py").write_text("print('Hello')")

        manager.install_agent("test-dev", "test-agent", str(source_dir))

        # Remove agent
        result = manager.remove_agent("test-dev", "test-agent")
        assert result["success"] is True

        # Verify removal
        agent_path = tmp_path / ".agenthub" / "agents" / "test-dev" / "test-agent"
        assert not agent_path.exists()
```

### **Metadata Manager Test Example**
```python
# tests/phase1_foundation/storage/test_metadata_manager.py
import pytest
from agenthub.storage.metadata_manager import MetadataManager

class TestMetadataManager:
    def test_parse_manifest(self, tmp_path):
        """Test manifest parsing."""
        manager = MetadataManager(base_path=tmp_path)

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
        """

        manifest = manager.parse_manifest_from_string(manifest_content)
        assert manifest["name"] == "test-agent"
        assert manifest["version"] == "1.0.0"
        assert "test_method" in manifest["interface"]["methods"]

    def test_validate_manifest(self, tmp_path):
        """Test manifest validation."""
        manager = MetadataManager(base_path=tmp_path)

        # Valid manifest
        valid_manifest = {
            "name": "test-agent",
            "version": "1.0.0",
            "interface": {
                "methods": {
                    "test_method": {
                        "description": "Test method",
                        "parameters": {}
                    }
                }
            }
        }

        result = manager.validate_manifest(valid_manifest)
        assert result["valid"] is True

        # Invalid manifest (missing required fields)
        invalid_manifest = {
            "name": "test-agent"
            # Missing version and interface
        }

        result = manager.validate_manifest(invalid_manifest)
        assert result["valid"] is False
        assert "version" in result["errors"]
        assert "interface" in result["errors"]
```

---

## 📊 **Test Coverage Requirements**

### **Line Coverage Targets**
- **Local Storage Manager**: 90%+ line coverage
- **Agent Manager**: 85%+ line coverage
- **Metadata Manager**: 90%+ line coverage
- **File Manager**: 85%+ line coverage
- **Overall Storage Module**: 87%+ line coverage

### **Branch Coverage Targets**
- **Success Paths**: 100% coverage
- **Error Paths**: 80%+ coverage
- **Edge Cases**: 75%+ coverage

---

## 🚨 **Test Failure Scenarios**

### **Common Failure Modes**
- [ ] **File system errors**: Permission denied, disk full, corrupted files
- [ ] **Directory creation failures**: Invalid paths, permission issues
- [ ] **File operation failures**: Read/write errors, file locks
- [ ] **Metadata corruption**: Invalid YAML, corrupted JSON
- [ ] **Resource exhaustion**: Disk space, file descriptors

### **Error Recovery Testing**
- [ ] **Test graceful degradation**: System continues working after failures
- [ ] **Test error reporting**: Clear error messages for users
- [ ] **Test recovery mechanisms**: System can recover from failures
- [ ] **Test data integrity**: Data remains consistent after failures

---

## 🎯 **Storage Module Success Criteria**

### **Functional Success**
- [ ] **Can manage agent directories**: Creates and manages agent directory structures
- [ ] **Can handle agent files**: Manages agent.yaml, agent.py, requirements.txt
- [ ] **Can manage metadata**: Stores and retrieves agent metadata correctly
- [ ] **Can handle file operations**: File operations work reliably

### **Performance Success**
- [ ] **Directory operations < 100ms**: Fast directory creation and management
- [ ] **File operations < 50ms**: Fast file read/write operations
- [ ] **Metadata operations < 10ms**: Fast metadata operations
- [ ] **Concurrent operations**: Can handle multiple operations simultaneously

### **Integration Success**
- [ ] **Works with Runtime Module**: Provides files for agent execution
- [ ] **Works with Core Module**: Provides metadata for agent validation
- [ ] **Works with CLI Module**: Provides data for user commands
- [ ] **Works with real agents**: Can manage actual agentplug agents

---

## 📋 **Testing Checklist**

### **Pre-Testing Setup**
- [ ] Test environment configured
- [ ] Test directories prepared
- [ ] Test files created
- [ ] Mock file system configured

### **Unit Testing**
- [ ] Local Storage Manager tests pass
- [ ] Agent Manager tests pass
- [ ] Metadata Manager tests pass
- [ ] File Manager tests pass
- [ ] Coverage targets met

### **Integration Testing**
- [ ] Storage + Runtime integration tests pass
- [ ] Storage + Core integration tests pass
- [ ] Storage + CLI integration tests pass
- [ ] Cross-module coordination works

### **End-to-End Testing**
- [ ] Complete agent lifecycle workflows work
- [ ] File operations work reliably
- [ ] Multi-agent scenarios work correctly
- [ ] Real agentplug agents can be managed

### **Final Validation**
- [ ] All tests pass consistently
- [ ] Performance requirements met
- [ ] Integration points validated
- [ ] Ready for Phase 2 development

---

## 🚀 **Next Steps After Testing Success**

1. **Document test results** and coverage metrics
2. **Identify any edge cases** that need additional testing
3. **Plan Phase 2 testing** based on Storage Module learnings
4. **Prepare for integration testing** with other modules

The Storage Module testing ensures that the **data management foundation** works reliably and can handle real agentplug agents, providing a solid foundation for the entire system.
