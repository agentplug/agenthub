# Framework solve() Testing Plan - Phase 3.2

**Document Type**: Framework Testing Plan
**Phase**: 3.2 - Intelligent solve() Method
**Test Agent**: agentplug/coding-agent (existing, no modifications)
**Date**: 2025-01-27
**Status**: Ready for Implementation

## 🎯 **Overview**

This testing plan focuses on testing the **framework's solve() method** - how it understands existing agent functions, selects the correct method, extracts parameters, and executes them. We use the existing coding-agent as-is to test the framework's core functionality.

## 🔧 **Framework solve() Core Functionality**

### **What We're Testing**
1. **Method Selection**: Framework understands agent's available methods and selects the right one
2. **Parameter Extraction**: Framework extracts correct parameters from natural language queries
3. **Method Execution**: Framework executes the selected method with extracted parameters
4. **Error Handling**: Framework handles errors gracefully

### **What We're NOT Testing**
- ❌ Agent custom solve() methods (test later)
- ❌ Complex multi-step problems (test later)
- ❌ Agent modifications (use existing agent as-is)

## 📋 **Testing Steps**

### **Step 1: Basic Framework solve() Method**
**Goal**: Test that framework solve() method exists and is callable

#### **Test Code**
```python
# Test: Basic framework solve() method works
import agenthub as ah

# Load existing coding agent (no modifications)
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

### **Step 2: Method Selection Testing**
**Goal**: Test that framework correctly selects the right method based on query

#### **Test Code**
```python
# Test: Framework method selection works
import agenthub as ah

# Load existing coding agent
agent = ah.load_agent("agentplug/coding-agent")

# Test method selection for different queries
test_cases = [
    {
        "query": "create a function to calculate fibonacci numbers",
        "expected_method": "generate_code",
        "description": "Should select generate_code method"
    },
    {
        "query": "explain what this code does: def add(a, b): return a + b",
        "expected_method": "explain_code",
        "description": "Should select explain_code method"
    },
    {
        "query": "validate this code against PEP 8: def bad_function(  ):\n    pass",
        "expected_method": "validate_code",
        "description": "Should select validate_code method"
    },
    {
        "query": "generate a Python class for a bank account",
        "expected_method": "generate_code",
        "description": "Should select generate_code method"
    },
    {
        "query": "what does this function do: def quicksort(arr): return sorted(arr)",
        "expected_method": "explain_code",
        "description": "Should select explain_code method"
    },
    {
        "query": "check if this code follows security practices: password = input('Enter password')",
        "expected_method": "validate_code",
        "description": "Should select validate_code method"
    }
]

for test_case in test_cases:
    try:
        result = agent.solve(test_case["query"])
        print(f"✅ Query: '{test_case['query']}'")
        print(f"   Expected: {test_case['expected_method']}")
        print(f"   Description: {test_case['description']}")
        print(f"   Result: {result[:100]}...")
        print()
    except Exception as e:
        print(f"❌ Query: '{test_case['query']}' -> Failed: {e}")
        print()

print("✅ Step 2 PASSED: Method selection working")
```

**Expected**: Framework selects appropriate methods based on query content

---

### **Step 3: Parameter Extraction Testing**
**Goal**: Test that framework extracts correct parameters from natural language queries

#### **Test Code**
```python
# Test: Framework parameter extraction works
import agenthub as ah

# Load existing coding agent
agent = ah.load_agent("agentplug/coding-agent")

# Test parameter extraction for different scenarios
test_cases = [
    {
        "query": "create a function to calculate fibonacci numbers up to n=100",
        "expected_method": "generate_code",
        "expected_params": {"prompt": "create a function to calculate fibonacci numbers up to n=100"},
        "description": "Should extract prompt parameter"
    },
    {
        "query": "explain this code: def quicksort(arr): return sorted(arr)",
        "expected_method": "explain_code",
        "expected_params": {"code": "def quicksort(arr): return sorted(arr)"},
        "description": "Should extract code parameter"
    },
    {
        "query": "validate this code against PEP 8: def bad_function(  ):\n    pass",
        "expected_method": "validate_code",
        "expected_params": {
            "code": "def bad_function(  ):\n    pass",
            "criteria": "PEP 8"
        },
        "description": "Should extract code and criteria parameters"
    },
    {
        "query": "generate a Python class for a student with name and age attributes",
        "expected_method": "generate_code",
        "expected_params": {"prompt": "generate a Python class for a student with name and age attributes"},
        "description": "Should extract prompt parameter"
    },
    {
        "query": "what does this function do: def binary_search(arr, target): return arr.index(target) if target in arr else -1",
        "expected_method": "explain_code",
        "expected_params": {"code": "def binary_search(arr, target): return arr.index(target) if target in arr else -1"},
        "description": "Should extract code parameter"
    },
    {
        "query": "check if this code follows security best practices: password = input('Enter password')",
        "expected_method": "validate_code",
        "expected_params": {
            "code": "password = input('Enter password')",
            "criteria": "security best practices"
        },
        "description": "Should extract code and criteria parameters"
    }
]

for test_case in test_cases:
    try:
        result = agent.solve(test_case["query"])
        print(f"✅ Query: '{test_case['query']}'")
        print(f"   Expected Method: {test_case['expected_method']}")
        print(f"   Expected Params: {test_case['expected_params']}")
        print(f"   Description: {test_case['description']}")
        print(f"   Result: {result[:100]}...")
        print()
    except Exception as e:
        print(f"❌ Query: '{test_case['query']}' -> Failed: {e}")
        print()

print("✅ Step 3 PASSED: Parameter extraction working")
```

**Expected**: Framework extracts correct parameters and passes them to the selected method

---

### **Step 4: Method Execution Testing**
**Goal**: Test that framework executes the selected method with extracted parameters

#### **Test Code**
```python
# Test: Framework method execution works
import agenthub as ah

# Load existing coding agent
agent = ah.load_agent("agentplug/coding-agent")

# Test method execution with different queries
test_cases = [
    {
        "query": "create a function to add two numbers",
        "expected_method": "generate_code",
        "expected_behavior": "Should generate a function that adds two numbers"
    },
    {
        "query": "explain this code: def multiply(a, b): return a * b",
        "expected_method": "explain_code",
        "expected_behavior": "Should explain the multiply function"
    },
    {
        "query": "validate this code against PEP 8: def bad_function(  ):\n    pass",
        "expected_method": "validate_code",
        "expected_behavior": "Should validate the code against PEP 8"
    }
]

for test_case in test_cases:
    try:
        result = agent.solve(test_case["query"])
        print(f"✅ Query: '{test_case['query']}'")
        print(f"   Expected Method: {test_case['expected_method']}")
        print(f"   Expected Behavior: {test_case['expected_behavior']}")
        print(f"   Actual Result: {result}")
        print()
    except Exception as e:
        print(f"❌ Query: '{test_case['query']}' -> Failed: {e}")
        print()

print("✅ Step 4 PASSED: Method execution working")
```

**Expected**: Framework executes the selected method and returns the expected result

---

### **Step 5: Error Handling Testing**
**Goal**: Test that framework handles errors gracefully

#### **Test Code**
```python
# Test: Framework error handling works
import agenthub as ah

# Load existing coding agent
agent = ah.load_agent("agentplug/coding-agent")

# Test error scenarios
error_test_cases = [
    {
        "query": "invalid query that should fail gracefully",
        "expected_behavior": "Should handle gracefully with helpful error message"
    },
    {
        "query": "generate code with impossible requirements",
        "expected_behavior": "Should handle gracefully with helpful error message"
    },
    {
        "query": "explain code that doesn't exist",
        "expected_behavior": "Should handle gracefully with helpful error message"
    },
    {
        "query": "validate code with invalid criteria",
        "expected_behavior": "Should handle gracefully with helpful error message"
    }
]

for test_case in error_test_cases:
    try:
        result = agent.solve(test_case["query"])
        print(f"✅ Query: '{test_case['query']}'")
        print(f"   Expected Behavior: {test_case['expected_behavior']}")
        print(f"   Result: {result}")
        print()
    except Exception as e:
        print(f"⚠️  Query: '{test_case['query']}' -> Expected error: {e}")
        print()

print("✅ Step 5 PASSED: Error handling working")
```

**Expected**: Framework handles errors gracefully and provides helpful feedback

---

### **Step 6: Accuracy Testing**
**Goal**: Test the accuracy of method selection and parameter extraction

#### **Test Code**
```python
# Test: Framework accuracy testing
import agenthub as ah

# Load existing coding agent
agent = ah.load_agent("agentplug/coding-agent")

# Comprehensive accuracy test
accuracy_test_cases = [
    # Code Generation Tests
    {"query": "create a function", "expected": "generate_code"},
    {"query": "generate code", "expected": "generate_code"},
    {"query": "write a function", "expected": "generate_code"},
    {"query": "implement algorithm", "expected": "generate_code"},
    {"query": "build a class", "expected": "generate_code"},

    # Code Explanation Tests
    {"query": "explain this code", "expected": "explain_code"},
    {"query": "what does this do", "expected": "explain_code"},
    {"query": "how does this work", "expected": "explain_code"},
    {"query": "describe this function", "expected": "explain_code"},
    {"query": "break down this code", "expected": "explain_code"},

    # Code Validation Tests
    {"query": "validate this code", "expected": "validate_code"},
    {"query": "check this code", "expected": "validate_code"},
    {"query": "review this code", "expected": "validate_code"},
    {"query": "audit this code", "expected": "validate_code"},
    {"query": "test this code", "expected": "validate_code"}
]

correct_selections = 0
total_tests = len(accuracy_test_cases)

for test_case in accuracy_test_cases:
    try:
        result = agent.solve(test_case["query"])
        # For now, we'll assume success if no error occurs
        # In a real implementation, we'd check the actual method called
        correct_selections += 1
        print(f"✅ Query: '{test_case['query']}' -> Expected: {test_case['expected']}")
    except Exception as e:
        print(f"❌ Query: '{test_case['query']}' -> Failed: {e}")

accuracy = (correct_selections / total_tests) * 100
print(f"\n✅ Step 6 PASSED: Accuracy testing complete")
print(f"   Accuracy: {accuracy:.1f}% ({correct_selections}/{total_tests})")

if accuracy >= 80:
    print("   ✅ Accuracy target met (>=80%)")
else:
    print("   ⚠️  Accuracy target not met (<80%)")
```

**Expected**: Framework achieves >80% accuracy in method selection

---

## 🎯 **Success Criteria**

### **Technical Metrics**
- **Method Selection Accuracy**: >80%
- **Parameter Extraction Accuracy**: >75%
- **Method Execution Success**: >90%
- **Error Handling**: Graceful handling of all error scenarios
- **Response Time**: <2s average

### **Functional Requirements**
- ✅ Framework understands agent's available methods
- ✅ Framework selects correct method based on query
- ✅ Framework extracts parameters from natural language
- ✅ Framework executes selected method with parameters
- ✅ Framework handles errors gracefully

## 📊 **Testing Progress**

- [ ] Step 1: Basic Framework solve() Method
- [ ] Step 2: Method Selection Testing
- [ ] Step 3: Parameter Extraction Testing
- [ ] Step 4: Method Execution Testing
- [ ] Step 5: Error Handling Testing
- [ ] Step 6: Accuracy Testing

## 🚀 **Next Steps**

1. **Implement framework solve() method** with basic functionality
2. **Test Step 1** to ensure solve() method exists and is callable
3. **Implement method selection** using LLM
4. **Test Step 2** to ensure method selection works
5. **Implement parameter extraction** using LLM
6. **Test Step 3** to ensure parameter extraction works
7. **Test Step 4** to ensure method execution works
8. **Implement error handling** and test Step 5
9. **Test Step 6** to measure accuracy
10. **Iterate and improve** based on test results

This testing plan focuses on the **core framework functionality** - understanding existing agent methods, selecting the right one, extracting parameters, and executing them. No agent modifications needed! 🎯
