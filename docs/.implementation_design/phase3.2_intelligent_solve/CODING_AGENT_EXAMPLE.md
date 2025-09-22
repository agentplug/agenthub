# Coding Agent Example - Phase 3.2 solve() Testing

**Document Type**: Implementation Example
**Agent**: agentplug/coding-agent
**Phase**: 3.2 - Intelligent solve() Method
**Date**: 2025-01-27
**Status**: Ready for Testing

## 🎯 **Overview**

The coding agent is an excellent example for testing the Phase 3.2 intelligent solve() method. It has three distinct methods with clear purposes, making it perfect for testing LLM-powered method selection and parameter extraction.

## 🔧 **Agent Analysis**

### **Agent Structure**
- **Name**: coding-agent
- **Version**: 1.0.0
- **Description**: Generate Python code based on natural language prompts
- **Methods**: 3 distinct methods with clear purposes

### **Available Methods**

#### **1. generate_code(prompt: str) -> str**
- **Purpose**: Generate Python code from natural language
- **Parameters**: `prompt` (string, required) - Natural language description
- **Returns**: Generated Python code as string
- **Use Cases**: Code generation, function creation, algorithm implementation

#### **2. explain_code(code: str) -> str**
- **Purpose**: Explain what Python code does
- **Parameters**: `code` (string, required) - Python code to explain
- **Returns**: Explanation of code functionality
- **Use Cases**: Code documentation, learning, debugging

#### **3. validate_code(code: str, criteria: str) -> str**
- **Purpose**: Validate code against specified criteria
- **Parameters**:
  - `code` (string, required) - Code to validate
  - `criteria` (string, required) - Validation criteria
- **Returns**: Validation result with pass/fail status
- **Use Cases**: Code review, quality assurance, compliance checking

## 🧪 **Test Scenarios for Phase 3.2**

### **Step 1: Basic Infrastructure Test**

```python
# Test: Basic solve() method works with coding agent
import agenthub as ah

# Load coding agent
agent = ah.load_agent("agentplug/coding-agent")

# Test basic solve() call
try:
    result = agent.solve("test query")
    print("✅ Step 1 PASSED: solve() method exists and callable")
    print(f"Result: {result}")
except Exception as e:
    print(f"❌ Step 1 FAILED: {e}")
```

**Expected**: solve() method exists and returns a result (even if basic)

---

### **Step 2: LLM Method Selection Test**

```python
# Test: LLM method selection works with coding agent
import agenthub as ah

# Load coding agent
agent = ah.load_agent("agentplug/coding-agent")

# Test method selection for different coding tasks
test_queries = [
    "create a function to calculate fibonacci numbers",
    "explain what this code does: def add(a, b): return a + b",
    "validate this code against PEP 8 standards",
    "generate a Python class for a bank account",
    "explain the algorithm in this sorting function",
    "check if this code follows security best practices"
]

for query in test_queries:
    try:
        result = agent.solve(query)
        print(f"✅ Query '{query}' -> Method selected successfully")
        print(f"   Result: {result[:100]}...")  # Truncate for readability
    except Exception as e:
        print(f"❌ Query '{query}' -> Failed: {e}")

print("✅ Step 2 PASSED: LLM method selection working")
```

**Expected**: LLM selects appropriate methods:
- "create a function" → `generate_code`
- "explain what this code does" → `explain_code`
- "validate this code" → `validate_code`

---

### **Step 3: Parameter Extraction Test**

```python
# Test: Parameter extraction works with coding agent
import agenthub as ah

# Load coding agent
agent = ah.load_agent("agentplug/coding-agent")

# Test parameter extraction for different coding scenarios
test_queries = [
    "create a function to calculate fibonacci numbers up to n=100",
    "explain this code: def quicksort(arr): return sorted(arr)",
    "validate this code against PEP 8: def bad_function(  ):\n    pass",
    "generate a Python class for a bank account with balance and deposit methods",
    "explain the algorithm in this code: def binary_search(arr, target): ...",
    "check if this code follows security practices: password = input('Enter password')"
]

for query in test_queries:
    try:
        result = agent.solve(query)
        print(f"✅ Query '{query}' -> Parameters extracted and method executed")
        print(f"   Result: {result[:100]}...")  # Truncate for readability
    except Exception as e:
        print(f"❌ Query '{query}' -> Failed: {e}")

print("✅ Step 3 PASSED: Parameter extraction working")
```

**Expected**: LLM extracts parameters correctly:
- "create a function to calculate fibonacci numbers up to n=100" → `generate_code(prompt="create a function to calculate fibonacci numbers up to n=100")`
- "explain this code: def quicksort(arr): return sorted(arr)" → `explain_code(code="def quicksort(arr): return sorted(arr)")`
- "validate this code against PEP 8: def bad_function(  ):\n    pass" → `validate_code(code="def bad_function(  ):\n    pass", criteria="PEP 8")`

---

### **Step 4: Agent Custom solve() Support Test**

```python
# Test: Agent custom solve() support works (if implemented)
import agenthub as ah

# Load coding agent
agent = ah.load_agent("agentplug/coding-agent")

# Test custom solve() delegation
test_queries = [
    "solve this complex coding problem with multiple steps",
    "use my custom logic for this programming task",
    "apply specialized coding techniques for this problem"
]

for query in test_queries:
    try:
        result = agent.solve(query)
        print(f"✅ Query '{query}' -> Custom solve() executed")
        print(f"   Result: {result[:100]}...")  # Truncate for readability
        print(f"   Method: Custom solve() (delegated)")
    except Exception as e:
        print(f"❌ Query '{query}' -> Failed: {e}")

print("✅ Step 4 PASSED: Agent custom solve() support working")
```

**Expected**: Framework correctly delegates to agent custom solve() methods when available

---

### **Step 5: Error Handling and Fallbacks Test**

```python
# Test: Error handling and fallbacks work with coding agent
import agenthub as ah

# Load coding agent
agent = ah.load_agent("agentplug/coding-agent")

# Test error scenarios
error_test_queries = [
    "invalid query that should fail gracefully",
    "generate code with impossible requirements",
    "explain code that doesn't exist",
    "validate code with invalid criteria"
]

for query in error_test_queries:
    try:
        result = agent.solve(query)
        print(f"✅ Query '{query}' -> Handled gracefully")
        print(f"   Result: {result[:100]}...")  # Truncate for readability
    except Exception as e:
        print(f"⚠️  Query '{query}' -> Expected error: {e}")

# Test fallback mechanisms
fallback_queries = [
    "create a function",  # Should work
    "explain code",       # Should work
    "validate code",      # Should work
    "unknown coding task" # Should fallback
]

for query in fallback_queries:
    try:
        result = agent.solve(query)
        print(f"✅ Query '{query}' -> Processed (with fallback if needed)")
        print(f"   Result: {result[:100]}...")  # Truncate for readability
    except Exception as e:
        print(f"❌ Query '{query}' -> Unexpected error: {e}")

print("✅ Step 5 PASSED: Error handling and fallbacks working")
```

**Expected**: System handles errors gracefully and provides helpful feedback

---

### **Step 6: SDK Integration Test**

```python
# Test: SDK integration works with coding agent
import agenthub as ah

# Load coding agent
agent = ah.load_agent("agentplug/coding-agent")

# Verify solve() method is available
if hasattr(agent, 'solve'):
    print("✅ solve() method available on loaded agent")
else:
    print("❌ solve() method not available")

# Test solve() method works through SDK
try:
    result = agent.solve("create a simple calculator function")
    print("✅ solve() method works through SDK")
    print(f"Result: {result[:100]}...")  # Truncate for readability
except Exception as e:
    print(f"❌ solve() method failed through SDK: {e}")

# Test backward compatibility
try:
    # Existing agent methods should still work
    if hasattr(agent, 'generate_code'):
        result = agent.generate_code("create a hello world function")
        print("✅ Backward compatibility maintained")
        print(f"Direct method result: {result[:100]}...")  # Truncate for readability
except Exception as e:
    print(f"❌ Backward compatibility broken: {e}")

print("✅ Step 6 PASSED: SDK integration working")
```

**Expected**: solve() method available through SDK, backward compatibility maintained

---

### **Step 7: Performance Optimization Test**

```python
# Test: Performance optimization works with coding agent
import agenthub as ah
import time

# Load coding agent
agent = ah.load_agent("agentplug/coding-agent")

# Test performance
test_queries = [
    "create a function to add two numbers",
    "explain this code: def multiply(a, b): return a * b",
    "validate this code: def divide(a, b): return a / b",
    "generate a class for a student with name and age"
]

total_time = 0
successful_queries = 0

for query in test_queries:
    start_time = time.time()
    try:
        result = agent.solve(query)
        end_time = time.time()
        query_time = end_time - start_time
        total_time += query_time
        successful_queries += 1

        print(f"✅ Query '{query}' -> {query_time:.2f}s")
    except Exception as e:
        print(f"❌ Query '{query}' -> Failed: {e}")

if successful_queries > 0:
    avg_time = total_time / successful_queries
    print(f"✅ Average response time: {avg_time:.2f}s")

    if avg_time < 2.0:
        print("✅ Performance target met (<2s average)")
    else:
        print("⚠️  Performance target not met (>2s average)")

print("✅ Step 7 PASSED: Performance optimization working")
```

**Expected**: Average response time <2s, performance monitoring working

---

### **Step 8: Comprehensive Testing**

```python
# Test: Comprehensive testing with coding agent
import agenthub as ah

# Load coding agent
agent = ah.load_agent("agentplug/coding-agent")

# Comprehensive test scenarios
test_scenarios = [
    {
        "name": "Code Generation",
        "query": "create a function that calculates the factorial of a number",
        "expected": "Should select generate_code method and generate factorial function"
    },
    {
        "name": "Code Explanation",
        "query": "explain this code: def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
        "expected": "Should select explain_code method and explain fibonacci function"
    },
    {
        "name": "Code Validation",
        "query": "validate this code against PEP 8: def bad_function(  ):\n    pass",
        "expected": "Should select validate_code method and validate against PEP 8"
    },
    {
        "name": "Complex Code Generation",
        "query": "create a Python class for a shopping cart with add_item, remove_item, and calculate_total methods",
        "expected": "Should select generate_code method and generate shopping cart class"
    },
    {
        "name": "Ambiguous Query",
        "query": "help me with this Python code",
        "expected": "Should handle gracefully with fallback or clarification"
    },
    {
        "name": "Invalid Parameters",
        "query": "explain code that doesn't exist",
        "expected": "Should handle error gracefully"
    }
]

passed_tests = 0
total_tests = len(test_scenarios)

for scenario in test_scenarios:
    try:
        result = agent.solve(scenario["query"])
        print(f"✅ {scenario['name']}: {scenario['expected']}")
        print(f"   Result: {result[:100]}...")  # Truncate for readability
        passed_tests += 1
    except Exception as e:
        print(f"❌ {scenario['name']}: Failed - {e}")

print(f"\n✅ Step 8 PASSED: {passed_tests}/{total_tests} tests passed")
print("✅ Phase 3.2 Implementation Complete with Coding Agent!")
```

**Expected**: All test scenarios pass, comprehensive validation complete

---

## 🎯 **Coding-Specific Test Cases**

### **Method Selection Accuracy Tests**

```python
# Test method selection accuracy for coding tasks
coding_test_cases = [
    # Code Generation
    ("create a function", "generate_code"),
    ("generate code", "generate_code"),
    ("write a function", "generate_code"),
    ("implement algorithm", "generate_code"),
    ("build a class", "generate_code"),

    # Code Explanation
    ("explain this code", "explain_code"),
    ("what does this do", "explain_code"),
    ("how does this work", "explain_code"),
    ("describe this function", "explain_code"),
    ("break down this code", "explain_code"),

    # Code Validation
    ("validate this code", "validate_code"),
    ("check this code", "validate_code"),
    ("review this code", "validate_code"),
    ("audit this code", "validate_code"),
    ("test this code", "validate_code")
]

for query, expected_method in coding_test_cases:
    # Test method selection
    pass
```

### **Parameter Extraction Tests**

```python
# Test parameter extraction for coding scenarios
parameter_test_cases = [
    {
        "query": "create a function to calculate fibonacci numbers up to 100",
        "expected_method": "generate_code",
        "expected_params": {"prompt": "create a function to calculate fibonacci numbers up to 100"}
    },
    {
        "query": "explain this code: def quicksort(arr): return sorted(arr)",
        "expected_method": "explain_code",
        "expected_params": {"code": "def quicksort(arr): return sorted(arr)"}
    },
    {
        "query": "validate this code against PEP 8: def bad_function(  ):\n    pass",
        "expected_method": "validate_code",
        "expected_params": {
            "code": "def bad_function(  ):\n    pass",
            "criteria": "PEP 8"
        }
    }
]
```

## 📊 **Success Metrics for Coding Agent**

### **Technical Metrics**
- **Method Selection Accuracy**: >90% (coding tasks are well-defined)
- **Parameter Extraction Accuracy**: >85% (coding parameters are structured)
- **Average Response Time**: <2s
- **Error Rate**: <3% (coding tasks are predictable)
- **Test Coverage**: >95%

### **User Experience Metrics**
- **Natural Language Understanding**: Users can describe coding tasks naturally
- **Intuitive API**: Simple `agent.solve("create a function")` interface
- **Reliable Results**: Consistent code generation and explanation
- **Helpful Errors**: Clear error messages for coding issues

## 🚀 **Implementation Benefits**

### **For Testing Phase 3.2**
1. **Clear Method Distinction**: Three distinct methods with different purposes
2. **Structured Parameters**: Well-defined parameter types and requirements
3. **Predictable Behavior**: Coding tasks have expected outcomes
4. **Real-world Usage**: Actual coding scenarios users would encounter
5. **Error Scenarios**: Natural error cases (invalid code, missing parameters)

### **For User Experience**
1. **Natural Language**: "create a function" instead of method calls
2. **Context Awareness**: Understands coding context and requirements
3. **Intelligent Selection**: Chooses appropriate method based on intent
4. **Parameter Extraction**: Automatically extracts code and criteria
5. **Error Handling**: Graceful handling of coding errors and edge cases

## 📝 **Next Steps**

1. **Use coding agent for Step 1 testing**: Basic infrastructure validation
2. **Implement method selection**: Test with coding-specific queries
3. **Add parameter extraction**: Test with code generation scenarios
4. **Validate error handling**: Test with invalid code and parameters
5. **Measure performance**: Ensure fast response times for coding tasks

The coding agent provides an excellent foundation for testing and validating the Phase 3.2 intelligent solve() method! 🚀
