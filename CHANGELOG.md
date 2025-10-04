# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2025-01-27

### Added
- **Builtin Web Search Tool**: Complete web search module with AI-powered query rewriting
- **Modular Tool Architecture**: New `agenthub.builtin.tools` package for easy tool integration
- **Web Search Features**:
  - DuckDuckGo search integration with fallback support
  - AI-powered query optimization using LLM service
  - Content extraction from HTML and PDF sources
  - Asynchronous content fetching with timeout handling
  - Result filtering and validation
  - Configurable search parameters (max results, exclude URLs)
- **Example Implementation**: `examples/builtin_tools/web_search_example.py` showing usage

### Technical Details
- **Smart Model Selection**: Leverages existing LLM service for automatic model detection
- **Type Safety**: Full mypy compliance with comprehensive type hints
- **Error Handling**: Robust error handling with graceful fallbacks
- **Performance**: Asynchronous operations for better performance
- **Extensibility**: Modular design allows easy addition of new builtin tools

### Developer Experience
- **Simple Integration**: Import and wrap with `@tool` decorator
- **Selective Hosting**: Users choose which tools to host, not all at once
- **Clean API**: `WebSearchTool().search(query, exclude_urls, max_results)`
- **Documentation**: Comprehensive README with usage examples

## [0.1.3] - 2025-01-27

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
