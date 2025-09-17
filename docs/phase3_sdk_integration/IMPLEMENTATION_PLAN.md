# Phase 3: Implementation Plan for Installation Commands

**Document Type**: Implementation Plan  
**Author**: AgentHub Team  
**Date Created**: 2025-01-27  
**Last Updated**: 2025-01-27  
**Status**: Ready for Implementation  
**Purpose**: Detailed plan for modifying current implementation to support installation commands

## 🎯 **Yes, Phase 3 Requires Implementation Changes**

You're absolutely correct! Phase 3 needs to modify the current implementation to align with the installation commands approach. **Important constraint**: The framework doesn't have direct access to agent built-in tools, so agent developers must implement tool management logic. Here's the comprehensive plan:

## 📋 **Current System Analysis**

### **What Currently Works**
- ✅ **UV Environment Creation**: `uv venv .venv`
- ✅ **Dependency Installation**: `uv pip install --python .venv/bin/python package1 package2`
- ✅ **Requirements.txt Fallback**: `uv pip install --python .venv/bin/python -r requirements.txt`
- ✅ **YAML Parsing**: Reads `dependencies` from `agent.yaml`

### **What Needs to Change**
- ❌ **Installation Commands**: Currently hardcoded UV commands
- ❌ **Command Execution**: Currently only supports UV pip install
- ❌ **Validation Commands**: Currently no validation step
- ❌ **Tool Detection**: Currently no detection of different setup tools
- ❌ **Agent Tool Management**: Currently no tool disabling logic in agents
- ❌ **Framework-Agent Communication**: Currently no disabled tools communication

## 🔧 **Implementation Changes Required**

### **1. Enhanced EnvironmentSetup Class**

#### **Current Implementation (Lines 159-221)**
```python
# Current: Hardcoded UV commands
if 'dependencies' in agent_config:
    dependencies = agent_config['dependencies']
    result = subprocess.run(
        ["uv", "pip", "install", "--python", str(venv_python)] + dependencies,
        cwd=agent_path,
        capture_output=True,
        text=True,
        timeout=300
    )
```

#### **Phase 3 Implementation**
```python
# New: Dynamic installation commands
if 'installation' in agent_config:
    installation_commands = agent_config['installation'].get('commands', [])
    validation_commands = agent_config['installation'].get('validation', [])
    
    # Execute installation commands
    for command in installation_commands:
        result = self._execute_installation_command(command, agent_path, venv_path)
        if not result.success:
            return self._create_failure_result(agent_name, start_time, result.error_message)
    
    # Execute validation commands
    for command in validation_commands:
        result = self._execute_validation_command(command, agent_path, venv_path)
        if not result.success:
            return self._create_failure_result(agent_name, start_time, f"Validation failed: {result.error_message}")
```

### **2. Agent Tool Management System (Agent Developer Implementation Required)**

**Important**: Since the framework doesn't have direct access to agent built-in tools, agent developers must implement tool management logic.

#### **Agent Tool Management Interface**
```python
class AgentToolManager:
    """Agent developer must implement this in their agent code"""
    
    def __init__(self):
        self.builtin_tools = {}  # Agent defines its built-in tools
        self.disabled_builtin_tools = set()  # Agent manages disabled tools
    
    def disable_builtin_tools(self, disabled_builtin_tools: Set[str]) -> None:
        """Agent developer must implement this method"""
        self.disabled_builtin_tools = disabled_builtin_tools
    
    def get_available_tools(self) -> List[str]:
        """Agent developer must implement this method"""
        return [name for name in self.builtin_tools.keys() 
                if name not in self.disabled_builtin_tools]
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Agent developer must implement this method"""
        if tool_name in self.disabled_builtin_tools:
            raise ValueError(f"Tool '{tool_name}' is disabled by user configuration")
        
        if tool_name not in self.builtin_tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        return self.builtin_tools[tool_name](parameters)
```

### **3. Framework Communication System**

#### **ProcessManager Enhancement**
```python
class ProcessManager:
    """Framework side - passes disabled tools to agent"""
    
    def execute_agent(self, agent_path: str, method: str, parameters: dict, 
                     disabled_builtin_tools: Set[str] = None) -> dict:
        """Execute agent with disabled tools information"""
        
        # Add disabled tools to execution data
        execution_data = {
            "method": method,
            "parameters": parameters,
            "disabled_builtin_tools": list(disabled_builtin_tools or []),  # Pass to agent
            "tool_context": self.tool_context
        }
        
        # Execute agent command
        result = subprocess.run(
            [python_executable, str(agent_script), json.dumps(execution_data)],
            cwd=str(agent_dir),
            capture_output=True,
            text=True,
            timeout=self.timeout,
        )
        
        return self._parse_result(result)
```

### **4. New Command Execution System**

#### **InstallationCommandExecutor Class**
```python
class InstallationCommandExecutor:
    """Executes installation commands from agent.yaml"""
    
    def __init__(self, agent_path: str, venv_path: str):
        self.agent_path = agent_path
        self.venv_path = venv_path
        self.environment = self._setup_environment()
    
    def execute_installation_command(self, command: str) -> CommandResult:
        """Execute a single installation command"""
        try:
            # Handle different command types
            if command.startswith("uv "):
                return self._execute_uv_command(command)
            elif command.startswith("make "):
                return self._execute_make_command(command)
            elif command.startswith("npm "):
                return self._execute_npm_command(command)
            elif command.startswith("cargo "):
                return self._execute_cargo_command(command)
            elif command.startswith("go "):
                return self._execute_go_command(command)
            elif command.startswith("docker "):
                return self._execute_docker_command(command)
            else:
                return self._execute_generic_command(command)
                
        except Exception as e:
            return CommandResult(
                success=False,
                command=command,
                error=str(e)
            )
    
    def _execute_uv_command(self, command: str) -> CommandResult:
        """Execute UV-specific commands"""
        # Handle UV commands with proper environment
        if "venv" in command:
            return self._execute_venv_creation(command)
        elif "pip install" in command:
            return self._execute_pip_install(command)
        else:
            return self._execute_generic_command(command)
    
    def _execute_make_command(self, command: str) -> CommandResult:
        """Execute Make commands"""
        return self._execute_generic_command(command)
    
    def _execute_npm_command(self, command: str) -> CommandCommand:
        """Execute npm commands"""
        return self._execute_generic_command(command)
    
    def _execute_cargo_command(self, command: str) -> CommandResult:
        """Execute Cargo commands"""
        return self._execute_generic_command(command)
    
    def _execute_go_command(self, command: str) -> CommandResult:
        """Execute Go commands"""
        return self._execute_generic_command(command)
    
    def _execute_docker_command(self, command: str) -> CommandResult:
        """Execute Docker commands"""
        return self._execute_generic_command(command)
    
    def _execute_generic_command(self, command: str) -> CommandResult:
        """Execute any generic command"""
        try:
            result = subprocess.run(
                command.split(),
                cwd=self.agent_path,
                env=self.environment,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return CommandResult(
                success=result.returncode == 0,
                command=command,
                stdout=result.stdout,
                stderr=result.stderr
            )
        except Exception as e:
            return CommandResult(
                success=False,
                command=command,
                error=str(e)
            )
```

### **3. Enhanced YAML Schema Support**

#### **Current agent.yaml Parsing (Lines 164-176)**
```python
# Current: Only reads dependencies
if 'dependencies' in agent_config:
    dependencies = agent_config['dependencies']
```

#### **Phase 3 agent.yaml Parsing**
```python
# New: Reads installation commands and validation
def parse_agent_yaml(self, agent_yaml_path: str) -> AgentConfig:
    """Parse agent.yaml with Phase 3 schema support"""
    with open(agent_yaml_path, 'r') as f:
        agent_config = yaml.safe_load(f)
    
    # Phase 3: Installation commands
    installation_config = agent_config.get('installation', {})
    commands = installation_config.get('commands', [])
    validation = installation_config.get('validation', [])
    
    # Phase 3: Built-in tools
    builtin_tools = agent_config.get('builtin_tools', {})
    
    # Backward compatibility: dependencies
    dependencies = agent_config.get('dependencies', [])
    
    return AgentConfig(
        name=agent_config.get('name'),
        version=agent_config.get('version'),
        description=agent_config.get('description'),
        author=agent_config.get('author'),
        license=agent_config.get('license'),
        python_version=agent_config.get('python_version'),
        interface=agent_config.get('interface', {}),
        installation=InstallationConfig(commands=commands, validation=validation),
        builtin_tools=builtin_tools,
        dependencies=dependencies  # For backward compatibility
    )
```

### **4. New Data Classes**

#### **AgentConfig Class**
```python
@dataclass
class AgentConfig:
    """Complete agent configuration from agent.yaml"""
    name: str
    version: str
    description: str
    author: str
    license: str
    python_version: str
    interface: Dict[str, Any]
    installation: 'InstallationConfig'
    builtin_tools: Dict[str, Any]
    dependencies: List[str]  # For backward compatibility

@dataclass
class InstallationConfig:
    """Installation configuration from agent.yaml"""
    commands: List[str]
    validation: List[str]

@dataclass
class CommandResult:
    """Result of command execution"""
    success: bool
    command: str
    stdout: str = ""
    stderr: str = ""
    error: str = ""
    execution_time: float = 0.0
```

### **5. Enhanced Error Handling**

#### **New Error Types**
```python
class InstallationCommandError(EnvironmentSetupError):
    """Raised when installation command fails"""
    def __init__(self, command: str, error_message: str, suggestions: List[str] = None):
        super().__init__(f"Installation command failed: {command}")
        self.command = command
        self.error_message = error_message
        self.suggestions = suggestions or []

class ValidationCommandError(EnvironmentSetupError):
    """Raised when validation command fails"""
    def __init__(self, command: str, error_message: str, suggestions: List[str] = None):
        super().__init__(f"Validation command failed: {command}")
        self.command = command
        self.error_message = error_message
        self.suggestions = suggestions or []

class UnsupportedCommandError(EnvironmentSetupError):
    """Raised when command is not supported"""
    def __init__(self, command: str, supported_commands: List[str] = None):
        super().__init__(f"Unsupported command: {command}")
        self.command = command
        self.supported_commands = supported_commands or []
```

## 🚀 **Implementation Steps**

### **Step 1: Create New Classes (Week 1)**
1. **InstallationCommandExecutor**: Command execution system
2. **AgentConfig**: Enhanced configuration parsing
3. **CommandResult**: Command execution results
4. **New Error Types**: Enhanced error handling

### **Step 2: Modify EnvironmentSetup (Week 2)**
1. **Update setup_environment()**: Use installation commands
2. **Add command execution**: Support different tools
3. **Add validation**: Execute validation commands
4. **Maintain backward compatibility**: Support old dependencies format

### **Step 3: Update YAML Parsing (Week 3)**
1. **Enhanced agent.yaml parsing**: Support Phase 3 schema
2. **Backward compatibility**: Support old format
3. **Validation**: Validate new schema fields
4. **Error handling**: Better error messages

### **Step 4: Update AutoInstaller (Week 4)**
1. **Integration**: Use new EnvironmentSetup
2. **Progress tracking**: Track command execution
3. **Error handling**: Better error reporting
4. **Testing**: Comprehensive testing

### **Step 5: Update CLI and SDK (Week 5)**
1. **CLI updates**: Support new installation process
2. **SDK updates**: Support new agent loading
3. **Documentation**: Update user guides
4. **Examples**: Create Phase 3 examples

## 🔄 **Backward Compatibility Strategy**

### **Phase 1: Add New Features (Weeks 1-2)**
- Add new classes and methods
- Keep existing functionality unchanged
- Add feature flags for new behavior

### **Phase 2: Gradual Migration (Weeks 3-4)**
- Support both old and new formats
- Add migration helpers
- Update documentation

### **Phase 3: Full Migration (Weeks 5-6)**
- Default to new format
- Deprecate old format
- Remove old code (if desired)

## 📊 **Testing Strategy**

### **Unit Tests**
- Test each command executor
- Test YAML parsing
- Test error handling
- Test backward compatibility

### **Integration Tests**
- Test complete installation flow
- Test different agent types
- Test error scenarios
- Test performance

### **End-to-End Tests**
- Test real agent installations
- Test different setup tools
- Test validation commands
- Test user experience

## 🎯 **Success Criteria**

### **Functional Requirements**
- ✅ Support installation commands from agent.yaml
- ✅ Support validation commands
- ✅ Support different setup tools (make, npm, cargo, etc.)
- ✅ Maintain backward compatibility
- ✅ Better error handling and messages

### **Performance Requirements**
- ✅ Installation time < 5 minutes for typical agents
- ✅ Command execution timeout handling
- ✅ Memory usage < 1GB per agent
- ✅ Concurrent installation support

### **User Experience Requirements**
- ✅ Clear error messages with suggestions
- ✅ Progress tracking for long installations
- ✅ Easy migration from old format
- ✅ Comprehensive documentation

## 📋 **File Changes Required**

### **New Files**
- `agentmanager/environment/command_executor.py`
- `agentmanager/environment/agent_config.py`
- `agentmanager/environment/command_result.py`
- `tests/environment/test_command_executor.py`
- `tests/environment/test_agent_config.py`

### **Modified Files**
- `agentmanager/environment/environment_setup.py` (Major changes)
- `agentmanager/github/auto_installer.py` (Integration)
- `agentmanager/cli/commands/agent/agent_install.py` (CLI updates)
- `agentmanager/sdk/load_agent.py` (SDK updates)

### **Configuration Files**
- `agentmanager/environment/__init__.py` (Export new classes)
- `pyproject.toml` (Add new dependencies if needed)

## ✅ **Conclusion**

**Yes, Phase 3 requires significant implementation changes!** The current system is hardcoded for UV and dependencies lists, but Phase 3 needs to support:

1. **Dynamic installation commands** from agent.yaml
2. **Multiple setup tools** (make, npm, cargo, etc.)
3. **Validation commands** for setup verification
4. **Enhanced error handling** with better messages
5. **Backward compatibility** with existing agents

The implementation plan above provides a clear roadmap for making these changes while maintaining backward compatibility and ensuring a smooth transition to the new Phase 3 approach.

---

**This implementation will make AgentHub truly language-agnostic and tool-agnostic, supporting any setup tool while maintaining the simplicity and power of the current UV-based system.**
