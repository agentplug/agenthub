# Real MCP Modular Core Architecture Design

**Document Type**: Phase 2.5 Core Architecture Design
**Component**: Real MCP Modular Core Architecture
**Phase**: 2.5 - Real MCP Tool Integration
**Author**: William
**Date Created**: 2025-06-28
**Last Updated**: 2025-06-28
**Status**: Active
**Purpose**: Design modular architecture for real MCP core components to improve scalability and maintainability using official MCP Python SDK

## 🎯 **Overview**

The current core module structure is flat and not modular enough for scalability. This document outlines a comprehensive modular architecture that organizes **real MCP components** by responsibility and provides clear separation of concerns for **both built-in tools AND external tools** (populated through `amg.load_agent(tools=[])`) using the **official MCP Python SDK**.

## 🏗️ **Current vs. Proposed Architecture**

### **Current Structure (Flat)**
```
agentmanager/core/
├── __init__.py
├── agent_loader.py
├── agent_wrapper.py
├── interface_validator.py
├── manifest_parser.py
├── tool_decorators.py
├── tool_registration.py
├── tool_security.py
├── tool_service_host.py
└── tool_validation.py
```

### **Proposed Structure (Modular)**
```
agentmanager/core/
├── __init__.py
├── agents/
│   ├── __init__.py
│   ├── loader.py          # agent_loader.py
│   ├── wrapper.py         # agent_wrapper.py
│   ├── validator.py       # interface_validator.py
│   └── manifest.py        # manifest_parser.py
├── tools/
│   ├── __init__.py
│   ├── decorators.py      # tool_decorators.py
│   ├── registry.py        # tool_registration.py
│   ├── security.py        # tool_security.py
│   ├── service.py         # tool_service_host.py
│   ├── validation.py      # tool_validation.py
│   └── execution/
│       ├── __init__.py
│       ├── executor.py    # New: Tool execution engine
│       ├── monitor.py     # New: Execution monitoring
│       └── context.py     # New: Execution context management
├── runtime/
│   ├── __init__.py
│   ├── manager.py         # New: Runtime management
│   ├── lifecycle.py       # New: Component lifecycle
│   └── coordination.py    # New: Component coordination
└── common/
    ├── __init__.py
    ├── exceptions.py      # New: Common exceptions
    ├── types.py          # New: Common type definitions
    └── utils.py          # New: Common utilities
```

## 🔧 **Modular Component Design**

### **1. Agents Package (`core/agents/`)**
**Purpose**: Agent lifecycle management, loading, and execution

#### **Components**:
- **`loader.py`**: Agent discovery and loading logic
- **`wrapper.py`**: Agent execution wrapper and interface
- **`validator.py`**: Agent interface validation
- **`manifest.py`**: Agent manifest parsing and validation

#### **Key Features**:
- Agent discovery and loading
- Interface validation and compliance checking
- Manifest parsing and validation
- Agent execution wrapper with error handling

### **2. Tools Package (`core/tools/`)**
**Purpose**: Tool registration, validation, security, and execution

#### **Components**:
- **`decorators.py`**: Tool decorator system and metadata
- **`registry.py`**: Tool registration and management
- **`security.py`**: Tool security validation and sandboxing
- **`service.py`**: HTTP service hosting for tools
- **`validation.py`**: Tool validation and compliance checking
- **`execution/`**: Tool execution engine and monitoring

#### **Key Features**:
- Tool registration and discovery
- Security validation and sandboxing
- HTTP service hosting
- Execution monitoring and context management

### **3. Runtime Package (`core/runtime/`)**
**Purpose**: Runtime management and component coordination

#### **Components**:
- **`manager.py`**: Runtime lifecycle management
- **`lifecycle.py`**: Component lifecycle management
- **`coordination.py`**: Component coordination and communication

#### **Key Features**:
- Runtime lifecycle management
- Component coordination
- Service orchestration

### **4. Common Package (`core/common/`)**
**Purpose**: Shared utilities, types, and exceptions

#### **Components**:
- **`exceptions.py`**: Common exception classes
- **`types.py`**: Common type definitions and protocols
- **`utils.py`**: Shared utility functions

#### **Key Features**:
- Centralized exception handling
- Common type definitions
- Shared utility functions

## 🔄 **Migration Strategy**

### **Phase 1: Create Modular Structure**
1. Create new directory structure
2. Move existing files to appropriate packages
3. Update package `__init__.py` files
4. Create new components as needed

### **Phase 2: Update Imports**
1. Update all import statements throughout codebase
2. Update test imports
3. Update example imports
4. Update documentation

### **Phase 3: Enhance Components**
1. Add new execution engine components
2. Add runtime management components
3. Add common utilities and types
4. Enhance existing components with new features

### **Phase 4: Validation**
1. Run comprehensive tests
2. Validate all examples work
3. Update documentation
4. Performance testing

## 📋 **Benefits of Modular Architecture**

### **Scalability**
- Clear separation of concerns
- Easy to add new components
- Independent development of modules
- Better testability

### **Maintainability**
- Logical organization of code
- Easier to locate and fix issues
- Clear dependencies between modules
- Better code reusability

### **Extensibility**
- Easy to add new tool types
- Simple to extend agent capabilities
- Clear interfaces for plugins
- Better support for future phases

### **Developer Experience**
- Intuitive code organization
- Clear import paths
- Better IDE support
- Easier onboarding

## 🔗 **Integration Points**

### **Internal Dependencies**
```
agents/ → common/
tools/ → common/
runtime/ → agents/, tools/, common/
```

### **External Dependencies**
- CLI commands will import from specific modules
- Examples will use clear import paths
- Tests will be organized by module
- Documentation will reflect modular structure

## 🎯 **Success Criteria**

- ✅ All existing functionality preserved
- ✅ Clear modular organization
- ✅ All tests pass
- ✅ All examples work
- ✅ Documentation updated
- ✅ Performance maintained or improved
- ✅ Ready for future extensions

## 📝 **Implementation Notes**

### **Backward Compatibility**
- Maintain existing public APIs
- Use deprecation warnings for old imports
- Provide migration guide
- Gradual transition support

### **Testing Strategy**
- Unit tests for each module
- Integration tests for cross-module functionality
- End-to-end tests for complete workflows
- Performance regression tests

### **Documentation Updates**
- Update all import examples
- Create module-specific documentation
- Update architecture diagrams
- Provide migration guide

This modular architecture provides a solid foundation for future growth while maintaining the existing functionality and improving code organization.
