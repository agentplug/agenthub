# Built-in Tool Categories Specification

## Overview

This document provides detailed specifications for each built-in tool category, including tool definitions, usage examples, and implementation details. The categories are organized by functionality and loading strategy.

## Category 1: Math Tools (Auto-loaded)

**Purpose:** Basic mathematical operations and calculations
**Dependencies:** None (pure Python)
**Auto-load:** Yes (critical for agent functionality)
**Namespace:** `builtin`

### Tool Specifications

#### `add(a: int, b: int) -> int`
- **Description:** Add two numbers together
- **Parameters:** 
  - `a` (int): First number
  - `b` (int): Second number
- **Returns:** Sum of the two numbers
- **Example:** `add(5, 3)` → `8`
- **Use Case:** Basic arithmetic in agent responses

**Implementation Context:** This tool is moved from `examples/tools/mcp_tool_server.py` and provides essential arithmetic functionality that agents commonly need for calculations.

```python
@tool(name="add", description="Add two numbers", namespace="builtin")
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    print(f"[TOOL] Adding {a} + {b}")
    return a + b
```

#### `subtract(a: int, b: int) -> int`
- **Description:** Subtract second number from first
- **Parameters:**
  - `a` (int): First number
  - `b` (int): Second number
- **Returns:** Difference of the two numbers
- **Example:** `subtract(10, 3)` → `7`
- **Use Case:** Basic arithmetic calculations

**Implementation Context:** Provides subtraction functionality with the same interface as addition, maintaining consistency across math tools.

```python
@tool(name="subtract", description="Subtract two numbers", namespace="builtin")
def subtract(a: int, b: int) -> int:
    """Subtract the second number from the first."""
    print(f"[TOOL] Subtracting {a} - {b}")
    return a - b
```

#### `multiply(a: int, b: int) -> int`
- **Description:** Multiply two numbers
- **Parameters:**
  - `a` (int): First number
  - `b` (int): Second number
- **Returns:** Product of the two numbers
- **Example:** `multiply(4, 5)` → `20`
- **Use Case:** Mathematical computations

**Implementation Context:** Essential for more complex calculations that agents might need to perform.

```python
@tool(name="multiply", description="Multiply two numbers", namespace="builtin")
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    print(f"[TOOL] Multiplying {a} * {b}")
    return a * b
```

#### `divide(a: float, b: float) -> float`
- **Description:** Divide first number by second
- **Parameters:**
  - `a` (float): Dividend
  - `b` (float): Divisor
- **Returns:** Quotient of the division
- **Example:** `divide(15, 3)` → `5.0`
- **Error Handling:** Raises `ValueError` if dividing by zero
- **Use Case:** Division operations

**Implementation Context:** Includes proper error handling for division by zero, which is a common edge case that needs to be handled gracefully.

```python
@tool(name="divide", description="Divide two numbers", namespace="builtin")
def divide(a: float, b: float) -> float:
    """Divide the first number by the second."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    print(f"[TOOL] Dividing {a} / {b}")
    return a / b
```

#### `compare_numbers(a: float, b: float) -> str`
- **Description:** Compare two numbers and return the larger one
- **Parameters:**
  - `a` (float): First number
  - `b` (float): Second number
- **Returns:** String describing which number is larger
- **Example:** `compare_numbers(9.8, 9.11)` → `"The larger number is 9.8"`
- **Use Case:** Number comparisons in agent logic

**Implementation Context:** This tool is particularly useful for agents that need to make decisions based on numerical comparisons.

```python
@tool(name="compare_numbers", description="Compare two numbers", namespace="builtin")
def compare_numbers(a: float, b: float) -> str:
    """Compare two numbers and return the larger one."""
    print(f"[TOOL] Comparing {a} and {b}")
    if type(a) != float:
        a = float(a)
    if type(b) != float:
        b = float(b)
    return f"The larger number is {float(max(a, b))}"
```

### Category Implementation

```python
# agentmanager/builtin/tools/categories/math.py
from ...core.tools import tool
from ..base import BuiltinTool

class MathTools(BuiltinTool):
    """Math tools category."""
    
    def get_tools(self):
        return [
            {'name': 'add', 'func': add, 'description': 'Add two numbers'},
            {'name': 'subtract', 'func': subtract, 'description': 'Subtract two numbers'},
            {'name': 'multiply', 'func': multiply, 'description': 'Multiply two numbers'},
            {'name': 'divide', 'func': divide, 'description': 'Divide two numbers'},
            {'name': 'compare_numbers', 'func': compare_numbers, 'description': 'Compare two numbers'},
        ]

# Tool implementations...
```

**Context:** This category provides essential mathematical operations that agents commonly need, with consistent interfaces and proper error handling.

## Category 2: Text Tools (Auto-loaded)

**Purpose:** Text processing and manipulation
**Dependencies:** None (pure Python)
**Auto-load:** Yes (commonly used)
**Namespace:** `builtin`

### Tool Specifications

#### `process_text(text: str, operation: str = "uppercase") -> str`
- **Description:** Process text with various operations
- **Parameters:**
  - `text` (str): Text to process
  - `operation` (str): Operation to perform (default: "uppercase")
- **Operations:** `uppercase`, `lowercase`, `titlecase`, `reverse`, `wordcount`, `charcount`
- **Returns:** Processed text
- **Example:** `process_text("hello world", "uppercase")` → `"HELLO WORLD"`
- **Use Case:** Text formatting and analysis

**Implementation Context:** This tool provides a unified interface for common text processing operations, making it easy for agents to manipulate text data.

```python
@tool(name="process_text", description="Process text with operations", namespace="builtin")
def process_text(text: str, operation: str = "uppercase") -> str:
    """Process text with various operations."""
    print(f"[TOOL] Processing text with operation: {operation}")
    
    operations = {
        "uppercase": text.upper(),
        "lowercase": text.lower(),
        "titlecase": text.title(),
        "reverse": text[::-1],
        "wordcount": str(len(text.split())),
        "charcount": str(len(text))
    }
    
    if operation not in operations:
        raise ValueError(f"Unknown operation: {operation}. Available: {list(operations.keys())}")
    
    return operations[operation]
```

#### `greet(name: str, greeting: str = "Hello") -> str`
- **Description:** Generate personalized greeting
- **Parameters:**
  - `name` (str): Name to greet
  - `greeting` (str): Greeting message (default: "Hello")
- **Returns:** Personalized greeting string
- **Example:** `greet("Alice", "Hi")` → `"Hi, Alice!"`
- **Use Case:** Personalized agent responses

**Implementation Context:** This tool enables agents to create personalized responses, which is important for user interaction.

```python
@tool(name="greet", description="Generate personalized greeting", namespace="builtin")
def greet(name: str, greeting: str = "Hello") -> str:
    """Generate a personalized greeting."""
    print(f"[TOOL] Greeting {name} with '{greeting}'")
    return f"{greeting}, {name}!"
```

#### `text_length(text: str) -> int`
- **Description:** Get character count of text
- **Parameters:**
  - `text` (str): Text to measure
- **Returns:** Character count
- **Example:** `text_length("hello")` → `5`
- **Use Case:** Text analysis

**Implementation Context:** Simple utility for text analysis that agents might need for various tasks.

```python
@tool(name="text_length", description="Get character count of text", namespace="builtin")
def text_length(text: str) -> int:
    """Get character count of text."""
    return len(text)
```

#### `extract_numbers(text: str) -> List[float]`
- **Description:** Extract all numbers from text
- **Parameters:**
  - `text` (str): Text to extract numbers from
- **Returns:** List of numbers found in text
- **Example:** `extract_numbers("I have 5 apples and 3 oranges")` → `[5.0, 3.0]`
- **Use Case:** Data extraction from text

**Implementation Context:** This tool is useful for agents that need to extract numerical data from text inputs.

```python
@tool(name="extract_numbers", description="Extract numbers from text", namespace="builtin")
def extract_numbers(text: str) -> list:
    """Extract all numbers from text."""
    import re
    numbers = re.findall(r'-?\d+\.?\d*', text)
    return [float(num) if '.' in num else int(num) for num in numbers]
```

### Category Implementation

```python
# agentmanager/builtin/tools/categories/text.py
from ...core.tools import tool
from ..base import BuiltinTool
import re

class TextTools(BuiltinTool):
    """Text tools category."""
    
    def get_tools(self):
        return [
            {'name': 'process_text', 'func': process_text, 'description': 'Process text with operations'},
            {'name': 'greet', 'func': greet, 'description': 'Generate personalized greeting'},
            {'name': 'text_length', 'func': text_length, 'description': 'Get character count of text'},
            {'name': 'extract_numbers', 'func': extract_numbers, 'description': 'Extract numbers from text'},
        ]

# Tool implementations...
```

**Context:** This category provides essential text processing capabilities that agents commonly need, with clear operation definitions and proper error handling.

## Category 3: Web Tools (Auto-loaded)

**Purpose:** Web-related operations and data fetching
**Dependencies:** `ddgs`, `requests`, `beautifulsoup4`, `aiohttp`
**Auto-load:** Yes (critical for agent functionality)
**Namespace:** `builtin`

### Tool Specifications

#### `web_search(query: str) -> dict`
- **Description:** Search the web and return summarized results
- **Parameters:**
  - `query` (str): Search query
- **Returns:** Dictionary with search results
- **Example:** `web_search("weather today")` → `{"results": [...]}`
- **Use Case:** Real-time information gathering
- **Error Handling:** Graceful degradation if dependencies missing

**Implementation Context:** This is the most critical tool as web search is essential for agent functionality. The implementation is moved from `examples/tools/mcp_tool_server.py` and enhanced with proper error handling.

```python
@tool(name="web_search", description="Search the web", namespace="builtin")
def web_search(query: str) -> dict:
    """Search the web for a query using DuckDuckGo and return summarized results.
    
    Args:
        query (str): The search query.
    
    Returns:
        dict: A dictionary with 'results' containing search results.
    """
    print(f"[TOOL] Performing web search for: '{query}' (max_results=5)")
    
    try:
        from ddgs import DDGS
        import requests
        from bs4 import BeautifulSoup
        import asyncio
        import aiohttp
        from concurrent.futures import ThreadPoolExecutor
    except ImportError:
        raise ImportError("Required packages 'ddgs', 'requests', 'beautifulsoup4', and 'aiohttp' are not installed.")

    # Implementation moved from examples/tools/mcp_tool_server.py
    # ... existing web search implementation ...
    
    return {"results": results}
```

#### `fetch_url(url: str) -> str`
- **Description:** Fetch content from a URL
- **Parameters:**
  - `url` (str): URL to fetch
- **Returns:** Content from the URL
- **Example:** `fetch_url("https://example.com")` → `"<html>..."`
- **Use Case:** Web content retrieval
- **Dependencies:** `requests`

**Implementation Context:** This tool provides simple URL content fetching for cases where web search is not needed.

```python
@tool(name="fetch_url", description="Fetch content from URL", namespace="builtin")
def fetch_url(url: str) -> str:
    """Fetch content from a URL."""
    try:
        import requests
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except ImportError:
        raise ImportError("Required package 'requests' not installed")
    except Exception as e:
        raise ValueError(f"Failed to fetch URL: {e}")
```

#### `validate_url(url: str) -> bool`
- **Description:** Validate if URL is properly formatted
- **Parameters:**
  - `url` (str): URL to validate
- **Returns:** True if URL is valid
- **Example:** `validate_url("https://example.com")` → `True`
- **Use Case:** URL validation before fetching
- **Dependencies:** None

**Implementation Context:** This tool provides URL validation to prevent errors when fetching content.

```python
@tool(name="validate_url", description="Validate URL format", namespace="builtin")
def validate_url(url: str) -> bool:
    """Validate if URL is properly formatted."""
    import re
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return pattern.match(url) is not None
```

### Category Implementation

```python
# agentmanager/builtin/tools/categories/web.py
from ...core.tools import tool
from ..base import BuiltinTool

class WebTools(BuiltinTool):
    """Web tools category - web-related operations and data fetching."""
    
    def get_tools(self):
        return [
            {'name': 'web_search', 'func': web_search, 'description': 'Search the web'},
            {'name': 'fetch_url', 'func': fetch_url, 'description': 'Fetch content from URL'},
            {'name': 'validate_url', 'func': validate_url, 'description': 'Validate URL format'},
        ]

# Tool implementations...
```

**Context:** This is the most critical category as web search is essential for agent functionality. The implementation is moved from examples and enhanced with proper error handling.

## Category 4: Data Tools (Lazy-loaded)

**Purpose:** Data manipulation and format conversion
**Dependencies:** `pandas`, `numpy` (optional)
**Auto-load:** No (heavy dependencies)
**Namespace:** `builtin`

### Tool Specifications

#### `json_parse(json_string: str) -> dict`
- **Description:** Parse JSON string to Python object
- **Parameters:**
  - `json_string` (str): JSON string to parse
- **Returns:** Parsed Python object
- **Example:** `json_parse('{"name": "John"}')` → `{"name": "John"}`
- **Error Handling:** Raises `ValueError` for invalid JSON
- **Dependencies:** None

**Implementation Context:** This tool provides essential JSON parsing functionality that agents commonly need for data processing.

```python
@tool(name="json_parse", description="Parse JSON string", namespace="builtin")
def json_parse(json_string: str) -> dict:
    """Parse JSON string to Python object."""
    import json
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
```

#### `json_stringify(obj: dict) -> str`
- **Description:** Convert Python object to JSON string
- **Parameters:**
  - `obj` (dict): Python object to convert
- **Returns:** JSON string
- **Example:** `json_stringify({"name": "John"})` → `'{"name": "John"}'`
- **Dependencies:** None

**Implementation Context:** This tool provides the reverse of JSON parsing, allowing agents to convert data back to JSON format.

```python
@tool(name="json_stringify", description="Convert to JSON string", namespace="builtin")
def json_stringify(obj: dict) -> str:
    """Convert Python object to JSON string."""
    import json
    return json.dumps(obj)
```

#### `csv_to_json(csv_string: str) -> List[dict]`
- **Description:** Convert CSV string to JSON array
- **Parameters:**
  - `csv_string` (str): CSV string to convert
- **Returns:** List of dictionaries
- **Example:** `csv_to_json("name,age\nJohn,25")` → `[{"name": "John", "age": "25"}]`
- **Dependencies:** None

**Implementation Context:** This tool enables agents to work with CSV data by converting it to a more manageable JSON format.

```python
@tool(name="csv_to_json", description="Convert CSV to JSON", namespace="builtin")
def csv_to_json(csv_string: str) -> list:
    """Convert CSV string to JSON array."""
    import csv
    import io
    import json
    
    reader = csv.DictReader(io.StringIO(csv_string))
    return list(reader)
```

### Category Implementation

```python
# agentmanager/builtin/tools/categories/data.py
from ...core.tools import tool
from ..base import BuiltinTool
import json
import csv
import io

class DataTools(BuiltinTool):
    """Data tools category."""
    
    def get_tools(self):
        return [
            {'name': 'json_parse', 'func': json_parse, 'description': 'Parse JSON string'},
            {'name': 'json_stringify', 'func': json_stringify, 'description': 'Convert to JSON string'},
            {'name': 'csv_to_json', 'func': csv_to_json, 'description': 'Convert CSV to JSON'},
        ]

# Tool implementations...
```

**Context:** This category provides essential data manipulation capabilities that agents might need, with proper error handling and no heavy dependencies.

## Category 5: System Tools (Lazy-loaded)

**Purpose:** System information and utilities
**Dependencies:** `psutil` (optional)
**Auto-load:** No (platform-specific)
**Namespace:** `builtin`

### Tool Specifications

#### `get_timestamp() -> str`
- **Description:** Get current timestamp
- **Parameters:** None
- **Returns:** Current timestamp string
- **Example:** `get_timestamp()` → `"2025-01-16T10:30:00Z"`
- **Use Case:** Logging and time-sensitive operations
- **Dependencies:** None

**Implementation Context:** This tool provides timestamp functionality that agents might need for logging or time-sensitive operations.

```python
@tool(name="get_timestamp", description="Get current timestamp", namespace="builtin")
def get_timestamp() -> str:
    """Get current timestamp."""
    from datetime import datetime
    return datetime.now().isoformat() + "Z"
```

#### `get_system_info() -> dict`
- **Description:** Get basic system information
- **Parameters:** None
- **Returns:** Dictionary with system information
- **Example:** `get_system_info()` → `{"platform": "Windows", "python_version": "3.9"}`
- **Error Handling:** Graceful degradation if psutil not available
- **Dependencies:** `psutil` (optional)

**Implementation Context:** This tool provides system information that agents might need, with graceful degradation when optional dependencies are not available.

```python
@tool(name="get_system_info", description="Get system information", namespace="builtin")
def get_system_info() -> dict:
    """Get basic system information."""
    import platform
    from datetime import datetime
    
    info = {
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "timestamp": get_timestamp()
    }
    
    try:
        import psutil
        info.update({
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total
        })
    except ImportError:
        pass  # Graceful degradation
    
    return info
```

### Category Implementation

```python
# agentmanager/builtin/tools/categories/system.py
from ...core.tools import tool
from ..base import BuiltinTool
import platform
from datetime import datetime

class SystemTools(BuiltinTool):
    """System tools category."""
    
    def get_tools(self):
        return [
            {'name': 'get_timestamp', 'func': get_timestamp, 'description': 'Get current timestamp'},
            {'name': 'get_system_info', 'func': get_system_info, 'description': 'Get system information'},
        ]

# Tool implementations...
```

**Context:** This category provides system-level functionality that agents might need, with proper error handling and graceful degradation.

## Tool Registration and Discovery

### Auto-loaded Categories
```python
# agentmanager/builtin/config.py
AUTO_LOAD_CATEGORIES = ['math', 'text', 'web']
```

### Lazy-loaded Categories
```python
LAZY_LOAD_CATEGORIES = ['data', 'system']
```

### Tool Discovery
```python
def list_builtin_tools() -> Dict[str, List[str]]:
    return {
        'math': ['add', 'subtract', 'multiply', 'divide', 'compare_numbers'],
        'text': ['process_text', 'greet', 'text_length', 'extract_numbers'],
        'web': ['web_search', 'fetch_url', 'validate_url'],
        'data': ['json_parse', 'json_stringify', 'csv_to_json'],
        'system': ['get_timestamp', 'get_system_info']
    }
```

## Error Handling Strategy

### Dependency Errors
```python
try:
    import pandas
    # Load data tools
except ImportError:
    logger.warning("Pandas not available, data tools disabled")
    # Skip data tools
```

### Tool Execution Errors
```python
try:
    result = tool_func(*args, **kwargs)
    return result
except Exception as e:
    logger.error(f"Tool execution failed: {e}")
    raise ToolExecutionError(f"Tool '{tool_name}' failed: {e}")
```

### Graceful Degradation
- Tools with missing dependencies are skipped
- Clear error messages for missing tools
- Fallback behavior when possible

## Performance Considerations

### Auto-loaded Tools
- **Math & Text**: Minimal overhead, loaded on import
- **Web**: Critical functionality, loaded on import

### Lazy-loaded Tools
- **Data**: Heavy dependencies, loaded only when needed
- **System**: Platform-specific, loaded only when needed

### Memory Usage
- Tool functions: ~1KB each
- Tool metadata: ~500 bytes each
- Total overhead: < 1MB for all tools

## Testing Strategy

### Unit Tests
- Test each tool individually
- Test error conditions
- Test edge cases

### Integration Tests
- Test tool loading mechanisms
- Test mixed tool usage
- Test backward compatibility

### Performance Tests
- Measure loading time
- Measure execution time
- Measure memory usage

---

*This specification provides detailed information about each tool category, ensuring consistent implementation and clear understanding of functionality.*
