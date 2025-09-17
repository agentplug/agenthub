# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of AgentHub
- Core agent loading and management functionality
- GitHub integration for agent discovery and installation
- Environment isolation using UV virtual environments
- Tool injection system with MCP (Model Context Protocol) support
- Comprehensive CLI interface for agent management
- Agent validation and repository validation
- Auto-installer for seamless agent setup
- Advanced environment management features

### Features
- **One-line agent loading**: `import agenthub as ah; agent = ah.load_agent("user/agent")`
- **Tool injection**: `agent = ah.load_agent("user/agent", tools=["tool1", "tool2"])`
- **CLI management**: Complete command-line interface for agent operations
- **Environment isolation**: Each agent runs in its own virtual environment
- **GitHub integration**: Automatic cloning and validation from GitHub repositories
- **MCP support**: Model Context Protocol for tool execution
- **Comprehensive testing**: 401 tests with full coverage

### Technical Details
- Python 3.11+ support
- Built with modern Python tooling (hatchling, pytest, mypy, ruff)
- Comprehensive error handling and validation
- Thread-safe tool registry
- Performance optimized for concurrent operations

## [0.1.0] - 2025-01-27

### Added
- Initial public release
- Core foundation with agent loading capabilities
- Phase 2.5 tool injection system
- Complete test suite (401 tests passing)
- Documentation and examples
- PyPI package preparation

### Security
- Isolated agent execution environments
- Git-based trust model for agent sources
- Runtime monitoring and resource limits

### Performance
- Optimized tool registration and execution
- Concurrent operation support
- Memory-efficient agent management

---

## Development

### Testing
- Run all tests: `pytest tests/`
- Run specific test suite: `pytest tests/phase2.5_tool_injection/`
- Coverage report: `pytest --cov=agenthub --cov-report=html`

### Building
- Build package: `python -m build`
- Install in development mode: `pip install -e .`
- Install with all dependencies: `pip install -e ".[dev,rag,code]"`

### Contributing
- Follow the existing code style (black, ruff)
- Add tests for new features
- Update documentation as needed
- Submit pull requests for review
