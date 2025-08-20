# Custom Method Injection User Guide

**Document Type**: User Guide  
**Author**: William  
**Date Created**: 2025-06-28  
**Last Updated**: 2025-06-28  
**Status**: Final  
**Level**: L3 - User Level  
**Audience**: Developers, System Administrators, Security Engineers

## 🎯 **Overview**

Agent Hub's Custom Method Injection system allows you to dynamically inject custom method implementations into agents at runtime. This powerful feature enables:

- **Dynamic Functionality**: Add new capabilities to agents without restarting
- **Multi-Language Support**: Use Python, JavaScript, Shell, or Bash
- **Security-First Design**: Built-in validation and security checks
- **Runtime Flexibility**: Modify agent behavior on-the-fly

## 🚀 **Quick Start**

### **1. Inject Your First Custom Method**

```bash
# Create a simple Python function
cat > my_function.py << 'EOF'
def analyze_text(text: str) -> dict:
    """Analyze text and return statistics."""
    return {
        "length": len(text),
        "word_count": len(text.split()),
        "char_count": len(text.replace(" ", "")),
        "uppercase_count": sum(1 for c in text if c.isupper())
    }
EOF

# Inject the method into an agent
agenthub method inject agentplug/coding-agent analyze_text my_function.py --language python
```

### **2. Use the Injected Method**

```python
import agentmanager as amg

# Load the agent (custom methods are automatically available)
agent = amg.load_agent("agentplug/coding-agent")

# Use your custom method
result = agent.analyze_text("Hello World! This is a test.")
print(result)
# Output: {'length': 25, 'word_count': 6, 'char_count': 20, 'uppercase_count': 2}
```

## 🔧 **Supported Languages**

### **Python**
- **Best for**: Complex logic, data processing, API integrations
- **Features**: Full function support, parameter validation, docstring extraction
- **Example**:
```python
def process_data(data: list, operation: str = "sum") -> float:
    """Process numerical data with various operations."""
    if operation == "sum":
        return sum(data)
    elif operation == "average":
        return sum(data) / len(data)
    elif operation == "max":
        return max(data)
    else:
        raise ValueError(f"Unknown operation: {operation}")
```

### **JavaScript**
- **Best for**: Web-related processing, JSON manipulation, async operations
- **Features**: Node.js execution, parameter passing, error handling
- **Example**:
```javascript
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return {
        isValid: emailRegex.test(email),
        domain: email.split('@')[1],
        suggestions: emailRegex.test(email) ? [] : ['Check email format']
    };
}
```

### **Shell/Bash**
- **Best for**: System operations, file processing, command-line tools
- **Features**: Environment variable access, subprocess execution, error handling
- **Example**:
```bash
#!/bin/bash
set -e

# Access parameters via environment variables
input_file="$AGENT_PARAM_INPUT_FILE"
output_file="$AGENT_PARAM_OUTPUT_FILE"

# Process the file
if [ -f "$input_file" ]; then
    # Count lines, words, and characters
    line_count=$(wc -l < "$input_file")
    word_count=$(wc -w < "$input_file")
    char_count=$(wc -c < "$input_file")
    
    echo "{\"lines\": $line_count, \"words\": $word_count, \"chars\": $char_count}" > "$output_file"
else
    echo "Error: Input file not found" >&2
    exit 1
fi
```

## 🛡️ **Security Features**

### **Security Levels**
- **Low**: Minimal restrictions, suitable for trusted environments
- **Medium**: Balanced security, recommended for most use cases
- **High**: Strict security, suitable for production environments

### **Automatic Security Checks**
- **Dangerous Patterns**: Blocks `eval()`, `exec()`, `rm -rf`, etc.
- **Resource Limits**: Prevents infinite loops and excessive memory usage
- **Input Validation**: Checks for potential injection attacks
- **Integrity Verification**: SHA256 checksums prevent tampering

### **Security Configuration**
```bash
# Use high security level
agenthub method inject agentplug/coding-agent secure_function function.py --language python --security-level high

# Validate without injecting
agenthub method validate function.py --language python --security-level high
```

## 📋 **CLI Commands Reference**

### **Method Injection**
```bash
# Basic injection
agenthub method inject <agent_path> <method_name> <file> --language <lang>

# With security level
agenthub method inject agentplug/coding-agent my_func function.py --language python --security-level high

# Validate only (don't inject)
agenthub method inject agentplug/coding-agent my_func function.py --language python --validate-only
```

### **Method Management**
```bash
# List all custom methods
agenthub method list agentplug/coding-agent

# Get detailed information
agenthub method info agentplug/coding-agent my_func

# Remove a method
agenthub method remove agentplug/coding-agent my_func

# Clean up expired methods
agenthub method cleanup agentplug/coding-agent --max-age-hours 48
```

### **Validation and Security**
```bash
# Validate a method file
agenthub method validate function.py --language python --security-level medium

# List supported languages
agenthub method languages

# Show security patterns
agenthub method security-patterns
```

## 🔍 **Advanced Usage**

### **Parameter Passing**

#### **Python Functions**
```python
def advanced_processor(data: dict, config: dict = None) -> dict:
    """Advanced data processor with configuration."""
    if config is None:
        config = {"mode": "default", "limit": 100}
    
    # Process data based on configuration
    if config["mode"] == "filter":
        result = {k: v for k, v in data.items() if len(str(v)) <= config["limit"]}
    elif config["mode"] == "transform":
        result = {k.upper(): str(v).upper() for k, v in data.items()}
    else:
        result = data.copy()
    
    return {"processed": result, "config_used": config}
```

#### **JavaScript Functions**
```javascript
function processArray(data, options = {}) {
    const { filter, sort, limit = 10 } = options;
    
    let result = [...data];
    
    if (filter) {
        result = result.filter(item => filter(item));
    }
    
    if (sort) {
        result.sort(sort);
    }
    
    if (limit) {
        result = result.slice(0, limit);
    }
    
    return {
        items: result,
        total: data.length,
        filtered: result.length
    };
}
```

#### **Shell Scripts**
```bash
#!/bin/bash
set -e

# Parse parameters
input_data="$AGENT_PARAM_INPUT_DATA"
filter_pattern="$AGENT_PARAM_FILTER_PATTERN"
sort_order="${AGENT_PARAM_SORT_ORDER:-asc}"
limit="${AGENT_PARAM_LIMIT:-10}"

# Process data
if [ -n "$filter_pattern" ]; then
    filtered_data=$(echo "$input_data" | grep "$filter_pattern")
else
    filtered_data="$input_data"
fi

# Sort and limit
if [ "$sort_order" = "desc" ]; then
    sorted_data=$(echo "$filtered_data" | sort -r | head -n "$limit")
else
    sorted_data=$(echo "$filtered_data" | sort | head -n "$limit")
fi

# Output JSON result
echo "{\"result\": \"$sorted_data\", \"count\": $(echo "$sorted_data" | wc -l)}"
```

### **Error Handling**

#### **Python Error Handling**
```python
def robust_processor(data: any) -> dict:
    """Robust data processor with comprehensive error handling."""
    try:
        if data is None:
            raise ValueError("Data cannot be None")
        
        if isinstance(data, str):
            processed = data.upper()
        elif isinstance(data, (list, tuple)):
            processed = [str(item).upper() for item in data]
        elif isinstance(data, dict):
            processed = {k: str(v).upper() for k, v in data.items()}
        else:
            processed = str(data).upper()
        
        return {
            "success": True,
            "result": processed,
            "input_type": type(data).__name__,
            "processed_at": time.time()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "input_type": type(data).__name__ if data is not None else "None"
        }
```

#### **JavaScript Error Handling**
```javascript
function safeProcessor(data) {
    try {
        // Validate input
        if (data === null || data === undefined) {
            throw new Error("Data cannot be null or undefined");
        }
        
        let result;
        
        if (typeof data === "string") {
            result = data.toUpperCase();
        } else if (Array.isArray(data)) {
            result = data.map(item => String(item).toUpperCase());
        } else if (typeof data === "object") {
            result = Object.fromEntries(
                Object.entries(data).map(([k, v]) => [k, String(v).toUpperCase()])
            );
        } else {
            result = String(data).toUpperCase();
        }
        
        return {
            success: true,
            result: result,
            inputType: typeof data,
            processedAt: Date.now()
        };
        
    } catch (error) {
        return {
            success: false,
            error: error.message,
            errorType: error.constructor.name,
            inputType: typeof data
        };
    }
}
```

### **Performance Optimization**

#### **Python Performance Tips**
```python
def optimized_processor(data: list) -> dict:
    """Optimized data processor with performance considerations."""
    # Use list comprehension instead of loops
    processed = [item * 2 for item in data if item > 0]
    
    # Use set for unique values (faster than list)
    unique_values = set(processed)
    
    # Use generator for large datasets
    def generate_results():
        for item in processed:
            yield {"value": item, "doubled": item * 2}
    
    return {
        "count": len(processed),
        "unique_count": len(unique_values),
        "results": list(generate_results())
    }
```

#### **JavaScript Performance Tips**
```javascript
function optimizedProcessor(data) {
    // Use Set for unique values
    const uniqueValues = new Set(data);
    
    // Use Map for key-value operations
    const valueMap = new Map();
    
    // Process in batches for large datasets
    const batchSize = 1000;
    const results = [];
    
    for (let i = 0; i < data.length; i += batchSize) {
        const batch = data.slice(i, i + batchSize);
        const processedBatch = batch.map(item => item * 2);
        results.push(...processedBatch);
    }
    
    return {
        count: data.length,
        uniqueCount: uniqueValues.size,
        results: results
    };
}
```

## 🧪 **Testing and Validation**

### **Validation Examples**

#### **Valid Python Function**
```python
def test_function(x: int, y: int) -> int:
    """Simple addition function."""
    return x + y
```
**Validation Result**: ✅ Passed (Security: 95/100)

#### **Function with Warnings**
```python
def process_data(data: list) -> list:
    result = ""
    for item in data:  # Warning: String concatenation in loop
        result += str(item)
    return result
```
**Validation Result**: ✅ Passed with warnings (Security: 85/100)

#### **Dangerous Function (Blocked)**
```python
def dangerous_function():
    import os
    os.system("rm -rf /")  # Error: Dangerous pattern detected
```
**Validation Result**: ❌ Failed (Security: 0/100)

### **Running Tests**
```bash
# Test validation
agenthub method validate my_function.py --language python --verbose

# Test injection with validation
agenthub method inject agentplug/coding-agent test_func my_function.py --language python --verbose
```

## 🔒 **Security Best Practices**

### **1. Input Validation**
```python
def safe_function(user_input: str) -> str:
    """Safe function with input validation."""
    # Validate input type
    if not isinstance(user_input, str):
        raise ValueError("Input must be a string")
    
    # Validate input length
    if len(user_input) > 1000:
        raise ValueError("Input too long")
    
    # Sanitize input
    sanitized = user_input.replace("<script>", "").replace("javascript:", "")
    
    return sanitized.upper()
```

### **2. Resource Limits**
```python
def resource_aware_function(data: list) -> list:
    """Function with resource awareness."""
    # Check input size
    if len(data) > 10000:
        raise ValueError("Input too large")
    
    # Process in chunks
    chunk_size = 1000
    result = []
    
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        processed_chunk = [item * 2 for item in chunk]
        result.extend(processed_chunk)
    
    return result
```

### **3. Error Handling**
```python
def robust_function(data: any) -> dict:
    """Robust function with comprehensive error handling."""
    try:
        # Your processing logic here
        result = process_data(data)
        
        return {
            "success": True,
            "result": result,
            "timestamp": time.time()
        }
        
    except ValueError as e:
        return {
            "success": False,
            "error": "Invalid input",
            "details": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": "Processing failed",
            "details": str(e)
        }
```

## 🚨 **Common Issues and Solutions**

### **Issue: Method Not Found**
```bash
Error: Custom method 'my_function' not found for agent 'agentplug/coding-agent'
```
**Solution**: Check if the method was injected correctly:
```bash
agenthub method list agentplug/coding-agent
```

### **Issue: Validation Failed**
```bash
Error: Method validation failed: Dangerous pattern detected: eval(
```
**Solution**: Review your code for security issues:
```bash
agenthub method validate function.py --language python --verbose
```

### **Issue: Language Not Supported**
```bash
Error: Language 'rust' is not supported
```
**Solution**: Use a supported language:
```bash
agenthub method languages
```

### **Issue: Method Execution Failed**
```python
# Check method info
agent.list_custom_methods()

# Check method context
context = agent.get_custom_method_context()
print(context)
```

## 📚 **Examples Gallery**

### **Data Analysis Function**
```python
def analyze_dataset(data: list, analysis_type: str = "basic") -> dict:
    """Analyze dataset with various metrics."""
    if not data:
        return {"error": "Empty dataset"}
    
    result = {
        "count": len(data),
        "analysis_type": analysis_type,
        "timestamp": time.time()
    }
    
    if analysis_type == "basic":
        result.update({
            "min": min(data),
            "max": max(data),
            "sum": sum(data),
            "average": sum(data) / len(data)
        })
    elif analysis_type == "statistical":
        import statistics
        result.update({
            "mean": statistics.mean(data),
            "median": statistics.median(data),
            "mode": statistics.mode(data),
            "variance": statistics.variance(data),
            "std_dev": statistics.stdev(data)
        })
    
    return result
```

### **File Processing Function**
```python
def process_files(file_paths: list, operation: str = "count") -> dict:
    """Process multiple files with various operations."""
    results = {}
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if operation == "count":
                results[file_path] = {
                    "lines": len(content.splitlines()),
                    "words": len(content.split()),
                    "characters": len(content)
                }
            elif operation == "analyze":
                results[file_path] = {
                    "size": len(content),
                    "has_content": bool(content.strip()),
                    "line_count": len(content.splitlines())
                }
                
        except Exception as e:
            results[file_path] = {"error": str(e)}
    
    return results
```

### **API Integration Function**
```python
def fetch_and_process(url: str, processor: str = "json") -> dict:
    """Fetch data from API and process it."""
    try:
        import requests
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        if processor == "json":
            data = response.json()
        elif processor == "text":
            data = response.text
        elif processor == "xml":
            import xml.etree.ElementTree as ET
            data = ET.fromstring(response.text)
        else:
            data = response.content
        
        return {
            "success": True,
            "data": data,
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type")
        }
        
    except requests.RequestException as e:
        return {
            "success": False,
            "error": f"Request failed: {e}",
            "url": url
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Processing failed: {e}",
            "url": url
        }
```

## 🔄 **Integration with Existing Workflows**

### **Python Script Integration**
```python
import agentmanager as amg

# Load agent with custom methods
agent = amg.load_agent("agentplug/coding-agent")

# Use both built-in and custom methods
builtin_result = agent.generate_code("Create a simple calculator")
custom_result = agent.analyze_text("This is some sample text")

print("Built-in method result:", builtin_result)
print("Custom method result:", custom_result)
```

### **Batch Processing**
```python
# Process multiple items with custom methods
items = ["item1", "item2", "item3", "item4"]

for item in items:
    try:
        result = agent.process_item(item)
        print(f"Processed {item}: {result}")
    except Exception as e:
        print(f"Failed to process {item}: {e}")
```

### **Error Recovery**
```python
def safe_execution(agent, method_name, *args, **kwargs):
    """Safely execute agent methods with error recovery."""
    try:
        if hasattr(agent, method_name):
            method = getattr(agent, method_name)
            return method(*args, **kwargs)
        else:
            return {"error": f"Method {method_name} not found"}
    except Exception as e:
        return {"error": f"Execution failed: {e}"}

# Usage
result = safe_execution(agent, "custom_method", "input_data")
```

## 📖 **Additional Resources**

### **Related Documentation**
- [Agent Hub Architecture Guide](../architecture/overview.md)
- [Security Best Practices](../security/best_practices.md)
- [CLI Reference](../cli/reference.md)

### **Examples Repository**
- [GitHub Examples](https://github.com/agentplug/agenthub-examples)
- [Custom Method Templates](https://github.com/agentplug/agenthub-templates)

### **Community Support**
- [Discord Community](https://discord.gg/agenthub)
- [GitHub Discussions](https://github.com/agentplug/agenthub/discussions)
- [Documentation Issues](https://github.com/agentplug/agenthub/issues)

---

**Need Help?** If you encounter issues or have questions, please:
1. Check this guide for solutions
2. Review the CLI help: `agenthub method --help`
3. Validate your methods: `agenthub method validate --help`
4. Join our community for support
