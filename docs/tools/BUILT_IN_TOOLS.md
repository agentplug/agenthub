# Built-in Tools Catalog

## Overview

AgentHub comes with a comprehensive set of built-in tools that provide essential functionality for agents. These tools are always available and don't require additional installation or configuration.

## Tool Categories

## Web Tools

### web_search
- **Description**: Search the web for a query and return summarized results using DuckDuckGo
- **Parameters**: 
  - `query: str` - The search query
- **Returns**: `dict` with structure:
  ```json
  {
    "results": [
      {
        "title": "Result title",
        "url": "https://example.com",
        "snippet": "Result description"
      }
    ]
  }
  ```
- **Version**: 1.0.0
- **Features**:
  - AI-enhanced query rewriting
  - Async web scraping
  - Structured result format
  - Error handling and timeouts

### http_request
- **Description**: Make HTTP requests to external APIs and web services
- **Parameters**:
  - `method: str` - HTTP method (GET, POST, PUT, DELETE)
  - `url: str` - Target URL
  - `headers: dict = None` - Request headers
  - `data: dict = None` - Request body data
- **Returns**: `dict` with response data
- **Version**: 1.0.0
- **Features**:
  - Support for all HTTP methods
  - JSON request/response handling
  - Custom headers support
  - Error handling

## Data Tools

### file_operations
- **Description**: Read, write, and manipulate files on the local system
- **Parameters**:
  - `operation: str` - Operation type (read, write, append, delete)
  - `path: str` - File path
  - `content: str = None` - Content to write (for write/append operations)
- **Returns**: `dict` with operation result
- **Version**: 1.0.0
- **Features**:
  - Multiple file operations
  - Path validation
  - Content encoding handling
  - Permission checking

### parse_json
- **Description**: Parse and validate JSON data
- **Parameters**:
  - `json_string: str` - JSON string to parse
  - `validate_schema: dict = None` - Optional JSON schema for validation
- **Returns**: `dict` with parsed JSON data
- **Version**: 1.0.0
- **Features**:
  - JSON parsing with error handling
  - Schema validation
  - Pretty printing
  - Type conversion

## AI Tools

### rag_query
- **Description**: Query a RAG (Retrieval-Augmented Generation) system for information
- **Parameters**:
  - `query: str` - The question or query
  - `context: str = None` - Additional context for the query
  - `max_results: int = 5` - Maximum number of results to return
- **Returns**: `dict` with RAG results
- **Version**: 1.0.0
- **Features**:
  - Vector similarity search
  - Context-aware responses
  - Configurable result limits
  - Relevance scoring

### text_analysis
- **Description**: Analyze text for sentiment, entities, and other linguistic features
- **Parameters**:
  - `text: str` - Text to analyze
  - `analysis_type: str` - Type of analysis (sentiment, entities, keywords)
- **Returns**: `dict` with analysis results
- **Version**: 1.0.0
- **Features**:
  - Sentiment analysis
  - Named entity recognition
  - Keyword extraction
  - Language detection

## System Tools

### shell_command
- **Description**: Execute shell commands safely with controlled permissions
- **Parameters**:
  - `command: str` - Shell command to execute
  - `timeout: int = 30` - Command timeout in seconds
  - `working_dir: str = None` - Working directory for command execution
- **Returns**: `dict` with command output and status
- **Version**: 1.0.0
- **Features**:
  - Safe command execution
  - Timeout protection
  - Working directory control
  - Output capture

### system_info
- **Description**: Get system information and status
- **Parameters**:
  - `info_type: str` - Type of system info (cpu, memory, disk, network)
- **Returns**: `dict` with system information
- **Version**: 1.0.0
- **Features**:
  - CPU usage monitoring
  - Memory usage tracking
  - Disk space information
  - Network status

## Tool Usage Examples

### Web Search
```python
from agenthub import load_agent

agent = load_agent("coding-agent")
result = agent.web_search("Python async programming")
print(result["results"][0]["title"])
```

### File Operations
```python
# Read a file
result = agent.file_operations("read", "/path/to/file.txt")
print(result["content"])

# Write to a file
agent.file_operations("write", "/path/to/output.txt", "Hello, World!")
```

### RAG Query
```python
# Query knowledge base
result = agent.rag_query("What is machine learning?", max_results=3)
for item in result["results"]:
    print(f"Relevance: {item['score']}, Content: {item['text'][:100]}...")
```

## Tool Metadata

All built-in tools include comprehensive metadata:

- **Name**: Unique tool identifier
- **Version**: Semantic version number
- **Description**: Detailed tool description
- **Parameters**: Parameter types and requirements
- **Return Type**: Expected return value structure
- **Examples**: Usage examples
- **Dependencies**: Required external libraries
- **Security Level**: Security and permission requirements

## Performance Characteristics

### Response Times
- **web_search**: 2-5 seconds (depending on query complexity)
- **file_operations**: < 100ms (for typical file sizes)
- **rag_query**: 1-3 seconds (depending on knowledge base size)
- **shell_command**: Variable (depends on command execution time)

### Resource Usage
- **Memory**: Tools are designed for minimal memory footprint
- **CPU**: Optimized for efficient execution
- **Network**: Built-in rate limiting and connection pooling
- **Storage**: Minimal temporary storage requirements

## Security Considerations

### Built-in Security Features
- **Input Validation**: All inputs are validated before processing
- **Permission Checks**: File operations check permissions
- **Command Sanitization**: Shell commands are sanitized
- **Rate Limiting**: API calls include rate limiting
- **Error Handling**: Comprehensive error handling prevents information leakage

### Best Practices
- Always validate tool inputs
- Use appropriate timeouts for long-running operations
- Handle errors gracefully in agent code
- Monitor tool usage for performance optimization
