# Environment Management Module - Interface Design

## Overview
The Environment Management Module handles the creation and management of isolated UV environments for each agent, ensuring complete dependency isolation and reproducible execution.

## Core Principles
- **Automated Setup**: No manual intervention required from users
- **Standardized Process**: Consistent setup flow for all agents
- **Complete Isolation**: Each agent runs in its own environment
- **Fallback Mechanisms**: Robust error handling and recovery
- **Resource Management**: Configurable limits and constraints

## UV Environment Setup Interface

### Primary Interface
```python
class UVEnvironmentSetup:
    """Standardized UV environment setup for automated agent installation"""
    
    def setup_uv_environment(self, agent_path: str, agent_config: AgentConfig, progress_callback=None) -> UVEnvironmentSetupResult:
        """
        Automated setup of UV environment for an agent
        
        Args:
            agent_path: Path to agent repository
            agent_config: Parsed agent.yaml configuration
            progress_callback: Optional progress tracking callback
            
        Returns:
            UVEnvironmentSetupResult with setup status and details
        """
        pass
    
    def create_uv_environment(self, agent_path: str, python_version: str) -> UVEnvironmentResult:
        """
        Create isolated UV environment
        
        Args:
            agent_path: Path to agent repository
            python_version: Python version to use
            
        Returns:
            UVEnvironmentResult with environment details
        """
        pass
    
    def execute_setup_commands(self, agent_path: str, agent_config: AgentConfig, progress_callback=None) -> UVDependencyResult:
        """
        Execute setup commands from agent.yaml with proper virtual environment activation
        
        This method executes the commands defined in agent.yaml setup.commands, ensuring
        each command runs in the activated virtual environment for proper isolation.
        
        Expected command format in agent.yaml:
        setup:
          commands:
            - "source .venv/bin/activate && uv sync"
            - "source .venv/bin/activate && uv pip install -e ."
            - "source .venv/bin/activate && uv pip install -r requirements.txt"
        
        Args:
            agent_path: Path to agent repository
            agent_config: Agent configuration with setup commands
            progress_callback: Progress tracking callback for real-time updates
            
        Returns:
            UVDependencyResult with setup status, including failed packages and rollback info
        """
        pass
    
    def validate_environment(self, agent_path: str, agent_config: AgentConfig) -> UVEnvironmentValidationResult:
        """
        Validate agent environment setup using validation steps from agent.yaml
        
        Args:
            agent_path: Path to agent repository
            agent_config: Agent configuration with validation steps
            
        Returns:
            UVEnvironmentValidationResult with validation status
        """
        pass
    
    def cleanup_failed_setup(self, agent_path: str) -> RollbackResult:
        """
        Clean up failed environment setup
        
        Args:
            agent_path: Path to agent repository
            
        Returns:
            RollbackResult with cleanup status
        """
        pass
    
    def get_environment_info(self, agent_path: str) -> UVEnvironmentInfo:
        """
        Get information about agent environment
        
        Args:
            agent_path: Path to agent repository
            
        Returns:
            UVEnvironmentInfo with environment details
        """
        pass
```

### Dynamic Setup Execution
```python
class SetupCommandExecutor:
    """Execute setup commands dynamically from agent.yaml"""
    
    def execute_setup_commands(self, agent_path: str, setup_config: SetupConfig, progress_callback=None) -> SetupExecutionResult:
        """
        Execute setup commands in sequence as specified in agent.yaml
        
        Args:
            agent_path: Path to agent repository
            setup_config: Setup configuration from agent.yaml
            progress_callback: Progress tracking callback
            
        Returns:
            SetupExecutionResult with execution status
        """
        commands = setup_config.commands
        total_commands = len(commands)
        
        for i, command in enumerate(commands):
            try:
                # Execute command
                result = self._execute_command(agent_path, command)
                
                # Update progress
                if progress_callback:
                    progress_percentage = ((i + 1) / total_commands) * 100
                    progress_callback(f"Executing: {command}", progress_percentage)
                
                # Check if command succeeded
                if not result.success:
                    return SetupExecutionResult(
                        success=False,
                        failed_command=command,
                        error_message=result.error_message,
                        commands_executed=i + 1,
                        total_commands=total_commands
                    )
                    
            except Exception as e:
                return SetupExecutionResult(
                    success=False,
                    failed_command=command,
                    error_message=str(e),
                    commands_executed=i + 1,
                    total_commands=total_commands
                )
        
        return SetupExecutionResult(
            success=True,
            commands_executed=total_commands,
            total_commands=total_commands
        )
    
    def _execute_command(self, agent_path: str, command: str) -> CommandExecutionResult:
        """Execute a single setup command"""
        # Implementation details for command execution
        pass
```

### Progress Tracking Interface
```python
class SetupProgressTracker:
    """Track and report setup progress for automated installation"""
    
    def get_setup_progress(self, agent_name: str) -> SetupProgress:
        """Get current setup progress for an agent"""
        pass
    
    def pause_setup(self, agent_name: str) -> bool:
        """Pause ongoing setup process"""
        pass
    
    def resume_setup(self, agent_name: str) -> bool:
        """Resume paused setup process"""
        pass
    
    def cancel_setup(self, agent_name: str) -> bool:
        """Cancel ongoing setup process"""
        pass
```

## UV Environment Data Models

### Core Setup Models
```python
@dataclass
class UVEnvironmentSetupResult:
    """Result of automated UV environment setup"""
    success: bool
    agent_path: str
    environment_path: str
    setup_time: float
    python_version: str
    uv_version: str
    commands_executed: List[str]
    commands_failed: List[str]
    errors: List[str]
    warnings: List[str]
    setup_log: str
    rollback_available: bool

@dataclass
class SetupExecutionResult:
    """Result of setup command execution"""
    success: bool
    commands_executed: int
    total_commands: int
    failed_command: Optional[str]
    error_message: Optional[str]
    execution_time: float
    setup_log: str

@dataclass
class CommandExecutionResult:
    """Result of individual command execution"""
    success: bool
    command: str
    output: str
    error_message: Optional[str]
    execution_time: float
    exit_code: int

@dataclass
class UVEnvironmentResult:
    """Result of UV environment creation"""
    success: bool
    agent_path: str
    environment_path: str
    python_version: str
    creation_time: float
    errors: List[str]

@dataclass
class UVDependencyResult:
    """Result of dependency installation"""
    success: bool
    agent_path: str
    installed_packages: List[str]
    install_time: float
    errors: List[str]
    warnings: List[str]
    failed_packages: List[FailedPackage]
    installation_log: str
    rollback_available: bool
    conflicts_resolved: List[str]

@dataclass
class FailedPackage:
    """Information about a failed package installation"""
    package_name: str
    version_attempted: str
    error_type: str
    error_message: str
    conflicting_packages: List[str]
    suggested_solutions: List[str]
    can_retry: bool
    retry_count: int

@dataclass
class UVEnvironmentValidationResult:
    """Result of environment validation"""
    success: bool
    agent_path: str
    validation_steps: List[ValidationStep]
    validation_time: float
    errors: List[str]
    warnings: List[str]

@dataclass
class ValidationStep:
    """Individual validation step result"""
    step_name: str
    command: str
    success: bool
    output: str
    error: Optional[str]
    execution_time: float

@dataclass
class UVEnvironmentInfo:
    """Information about UV environment"""
    agent_path: str
    environment_path: str
    python_version: str
    uv_version: str
    created_at: datetime
    last_used: datetime
    status: str
    resource_usage: ResourceUsage

@dataclass
class ResourceUsage:
    """Resource usage information"""
    memory_usage: str
    disk_usage: str
    cpu_usage: float
    active_processes: int
```

### Progress Tracking Models
```python
@dataclass
class SetupProgress:
    """Overall setup progress tracking"""
    agent_name: str
    current_phase: str
    phase_number: int
    total_phases: int
    overall_progress: float
    current_step: str
    step_progress: float
    start_time: datetime
    estimated_total_time: Optional[float]
    estimated_remaining: Optional[float]
    status: str
    current_operation: str
    details: Dict[str, Any]

@dataclass
class InstallationProgress:
    """Dependency installation progress"""
    agent_name: str
    current_step: str
    step_number: int
    total_steps: int
    progress_percentage: float
    current_package: Optional[str]
    packages_installed: int
    total_packages: int
    start_time: datetime
    estimated_remaining: Optional[float]
    status: str
    current_operation: str
    package_details: Dict[str, Any]

@dataclass
class RollbackResult:
    """Result of failed setup rollback"""
    success: bool
    agent_path: str
    cleaned_resources: List[str]
    rollback_time: float
    errors: List[str]
    warnings: List[str]
    partial_cleanup: bool
```

### Configuration Models
```python
@dataclass
class AgentConfig:
    """Parsed agent configuration from agent.yaml"""
    name: str
    version: str
    description: str
    python_version: str
    dependencies: DependencyConfig
    setup: SetupConfig
    interface: InterfaceConfig
    resources: ResourceConfig

@dataclass
class DependencyConfig:
    """Dependency configuration"""
    source: str  # "requirements.txt" or "pyproject.toml"
    python_version: str
    packages: List[str]

@dataclass
class SetupConfig:
    """Setup configuration for automated installation"""
    commands: List[str]  # Dynamic setup commands from agent.yaml
    validation: List[str]  # Validation commands from agent.yaml
    timeout: int  # Setup timeout in seconds
    resources: ResourceConfig

@dataclass
class ResourceConfig:
    """Resource limits and constraints"""
    memory_limit: str
    cpu_limit: str
    disk_limit: str
    timeout: int

@dataclass
class InterfaceConfig:
    """Agent interface configuration"""
    methods: Dict[str, MethodConfig]

@dataclass
class MethodConfig:
    """Individual method configuration"""
    description: str
    parameters: Dict[str, ParameterConfig]
    returns: ReturnConfig

@dataclass
class ParameterConfig:
    """Method parameter configuration"""
    type: str
    description: str
    required: bool
    default: Optional[Any]

@dataclass
class ReturnConfig:
    """Method return value configuration"""
    type: str
    description: str
```

## UV Environment Requirements & Constraints

### System Requirements
- **UV Installation**: UV package manager must be available and functional
- **Python Versions**: Support for Python 3.11+ with configurable per-agent requirements
- **System Resources**: Sufficient disk space, memory, and CPU for environment creation
- **Network Access**: Access to PyPI and other package repositories
- **File Permissions**: Write access to agent storage directories

### UV Project Structure Requirements
- **pyproject.toml**: UV-compatible project configuration (required)
- **requirements.txt**: Standard pip format dependencies (required)
- **Python Version**: Specified in agent.yaml and compatible with system
- **Build System**: Compatible with UV's build system requirements

### Agent Configuration Requirements
- **agent.yaml**: Must contain standardized setup configuration
- **Setup Commands**: Dynamic list of setup commands (not hardcoded)
- **Validation Steps**: Commands to verify successful setup
- **Resource Limits**: Memory, CPU, disk, and timeout constraints
- **Python Version**: Specific Python version requirements

### Environment Setup Flow Requirements
1. **Configuration Parsing**: Parse agent.yaml for setup requirements
2. **Environment Creation**: Create isolated UV environment with specified Python version
3. **Dynamic Command Execution**: Execute setup commands from agent.yaml in sequence
4. **Environment Validation**: Execute validation commands to verify setup
5. **Resource Verification**: Check resource usage and limits
6. **Status Recording**: Record successful setup in agent registry
7. **Cleanup Handling**: Handle failed setups with rollback capability

### Dynamic Setup Command Requirements
- **Flexible Commands**: Number of commands varies by agent
- **Sequential Execution**: Commands executed in order from agent.yaml
- **Fallback Support**: Multiple setup strategies supported
- **Error Handling**: Graceful failure handling for individual commands
- **Progress Tracking**: Real-time progress updates for each command

### Dependency Management Requirements
- **Isolation**: Complete dependency isolation between agents
- **Version Resolution**: Handle version conflicts and compatibility
- **Fallback Methods**: Multiple installation strategies for reliability
- **Conflict Detection**: Identify and resolve dependency conflicts
- **Rollback Support**: Clean recovery from failed installations

### Validation Requirements
- **Command Execution**: Execute validation commands in isolated environment
- **Output Analysis**: Parse and validate command outputs
- **Error Detection**: Identify setup failures and issues
- **Health Checks**: Verify agent functionality and imports
- **Resource Verification**: Check resource usage and limits

### Performance Requirements
- **Setup Time**: Environment creation < 30 seconds
- **Installation Time**: Dependency installation < 90 seconds
- **Validation Time**: Environment validation < 30 seconds
- **Total Setup**: Complete setup < 2 minutes for typical agents
- **Resource Usage**: Memory usage < 500MB during setup

### Scalability Requirements
- **Concurrent Setups**: Support multiple simultaneous agent installations
- **Resource Management**: Efficient resource allocation and cleanup
- **Queue Management**: Handle setup requests in order
- **Progress Tracking**: Track multiple installations simultaneously
- **Error Isolation**: Failures don't affect other installations

## UV Environment Mock Implementations

### Mock UV Environment Setup
```python
class MockUVEnvironmentSetup(UVEnvironmentSetup):
    """Mock implementation for testing and development"""
    
    def setup_uv_environment(self, agent_path: str, agent_config: AgentConfig, progress_callback=None) -> UVEnvironmentSetupResult:
        """Mock environment setup for testing"""
        if progress_callback:
            progress_callback("Creating mock environment", 25)
            progress_callback("Installing mock dependencies", 75)
            progress_callback("Validating mock setup", 100)
        
        return UVEnvironmentSetupResult(
            success=True,
            agent_path=agent_path,
            environment_path=f"{agent_path}/.venv",
            setup_time=2.5,
            python_version="3.11.5",
            uv_version="0.1.0",
            errors=[],
            warnings=[],
            setup_log="Mock setup completed successfully",
            rollback_available=False
        )
    
    def create_uv_environment(self, agent_path: str, python_version: str) -> UVEnvironmentResult:
        """Mock environment creation"""
        return UVEnvironmentResult(
            success=True,
            agent_path=agent_path,
            environment_path=f"{agent_path}/.venv",
            python_version=python_version,
            creation_time=1.0,
            errors=[]
        )
    
    def install_dependencies(self, agent_path: str, agent_config: AgentConfig, progress_callback=None) -> UVDependencyResult:
        """Mock dependency installation"""
        if progress_callback:
            progress_callback("Installing mock packages", 50)
            progress_callback("Resolving dependencies", 100)
        
        return UVDependencyResult(
            success=True,
            agent_path=agent_path,
            installed_packages=["mock-package-1", "mock-package-2"],
            install_time=3.0,
            errors=[],
            warnings=[],
            failed_packages=[],
            installation_log="Mock installation completed",
            rollback_available=False,
            conflicts_resolved=[]
        )
    
    def validate_environment(self, agent_path: str, agent_config: AgentConfig) -> UVEnvironmentValidationResult:
        """Mock environment validation"""
        validation_steps = [
            ValidationStep(
                step_name="Agent executable test",
                command="python agent.py --help",
                success=True,
                output="Mock agent help output",
                error=None,
                execution_time=0.5
            ),
            ValidationStep(
                step_name="Module import test",
                command="python -c 'import core.module'",
                success=True,
                output="Module imported successfully",
                error=None,
                execution_time=0.3
            )
        ]
        
        return UVEnvironmentValidationResult(
            success=True,
            agent_path=agent_path,
            validation_steps=validation_steps,
            validation_time=0.8,
            errors=[],
            warnings=[]
        )
```

### Mock Progress Tracker
```python
class MockSetupProgressTracker(SetupProgressTracker):
    """Mock progress tracker for testing"""
    
    def get_setup_progress(self, agent_name: str) -> SetupProgress:
        """Get mock setup progress"""
        return SetupProgress(
            agent_name=agent_name,
            current_phase="Dependency Installation",
            phase_number=3,
            total_phases=5,
            overall_progress=60.0,
            current_step="Installing packages",
            step_progress=75.0,
            start_time=datetime.now(),
            estimated_total_time=120.0,
            estimated_remaining=48.0,
            status="running",
            current_operation="pip install",
            details={"packages_installed": 15, "total_packages": 20}
        )
```

## 🔧 **Correct Setup Process & Commands**

### **Setup Commands in agent.yaml**
The `setup.commands` section in `agent.yaml` defines the exact commands AgentHub will execute to set up your agent:

```yaml
setup:
  commands:
    - "source .venv/bin/activate && uv sync"                                    # Step 1: Activate + sync
    - "source .venv/bin/activate && uv pip install -e ."                        # Step 2: Install project
    - "source .venv/bin/activate && uv pip install -r requirements.txt"         # Step 3: Install deps
  validation:
    - "python -c 'import core.rag_system'"         # Verify core modules
    - "python -c 'import core.llamaindex_store'"   # Verify LlamaIndex integration
    - "python -c 'import aisuite'"                 # Verify aisuite integration
```

### **Why This Approach Works**
1. **Virtual Environment Activation**: `source .venv/bin/activate` ensures all subsequent commands run in the isolated environment
2. **Command Chaining**: Using `&&` ensures each command only runs if the previous succeeds
3. **Proper Isolation**: All packages install in `.venv/lib/python3.11/site-packages/`
4. **Standard UV Commands**: Uses standard UV commands that users expect

### **Setup Process Flow**
1. **Environment Creation**: AgentHub creates `.venv/` using `uv venv --python 3.11`
2. **Command Execution**: AgentHub executes each command from `setup.commands`
3. **Virtual Environment Activation**: Each command activates the environment first
4. **Package Installation**: Packages install in the isolated environment
5. **Validation**: AgentHub runs validation commands to verify setup
6. **Registration**: Agent is registered and ready for use

### **Benefits of This Setup Process**
- **🎯 Reliability**: Virtual environment activation ensures proper isolation
- **🔧 Simplicity**: Standard UV commands that users understand
- **📊 Progress Tracking**: Each step can be monitored and reported
- **🔄 Consistency**: Same process works for all agents
- **🐛 Debugging**: Easy to reproduce setup manually for troubleshooting

## Integration Points

### With GitHub Module
- **Repository Validation**: Verify agent.yaml contains valid setup configuration
- **Structure Validation**: Ensure required files are present
- **Configuration Parsing**: Extract setup requirements from agent.yaml

### With Storage Module
- **Installation Tracking**: Record setup progress and status
- **Environment Metadata**: Store environment information and configuration
- **Rollback Support**: Track setup state for rollback operations

### With Core Module
- **Agent Registration**: Register successfully set up agents
- **Interface Validation**: Verify agent interface compliance
- **Health Monitoring**: Monitor agent environment health

### With CLI Module
- **Progress Reporting**: Provide real-time setup progress updates
- **User Feedback**: Display setup status and completion information
- **Error Reporting**: Show detailed error information and recovery options

## Error Handling & Recovery

### Setup Failure Scenarios
- **UV Installation Issues**: UV not available or malfunctioning
- **Python Version Conflicts**: Incompatible Python versions
- **Dependency Conflicts**: Package version conflicts and resolution failures
- **Resource Exhaustion**: Insufficient disk space, memory, or CPU
- **Network Failures**: Package download and installation failures
- **Permission Issues**: File system access and permission problems

### Recovery Strategies
- **Automatic Retry**: Retry failed operations with exponential backoff
- **Fallback Methods**: Use alternative installation strategies
- **Conflict Resolution**: Automatically resolve dependency conflicts
- **Resource Cleanup**: Clean up partial installations and retry
- **Rollback Operations**: Revert to previous working state
- **User Guidance**: Provide clear error messages and recovery steps

### Error Reporting
- **Detailed Error Messages**: Specific error causes and context
- **Recovery Instructions**: Clear steps to resolve issues
- **Log Information**: Detailed logs for debugging
- **Progress Preservation**: Maintain progress across retries
- **User Notifications**: Real-time error status updates
