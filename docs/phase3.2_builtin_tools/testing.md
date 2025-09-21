# Built-in Tools Testing & Validation Plan

## 🎯 Testing Strategy Overview

Comprehensive testing strategy for built-in tools that ensures reliability, performance, security, and user experience. The testing approach covers unit tests, integration tests, performance tests, security tests, and user acceptance tests.

## 📋 Testing Categories

### 1. **Unit Testing** - Individual tool functionality
### 2. **Integration Testing** - Tool interactions and workflows
### 3. **Performance Testing** - Speed, memory, and scalability
### 4. **Security Testing** - Vulnerability and attack resistance
### 5. **User Acceptance Testing** - Real-world usage scenarios
### 6. **Regression Testing** - Ensure no breaking changes

## 🧪 Unit Testing Framework

### Test Structure

```python
# agenthub/core/tools/builtin/tests/
├── __init__.py
├── conftest.py                 # Test configuration and fixtures
├── unit/                       # Unit tests
│   ├── test_document_tools.py
│   ├── test_web_tools.py
│   ├── test_code_tools.py
│   ├── test_data_tools.py
│   └── test_external_tools.py
├── integration/                # Integration tests
│   ├── test_tool_workflows.py
│   ├── test_cross_tool_operations.py
│   └── test_agent_integration.py
├── performance/                # Performance tests
│   ├── test_benchmarks.py
│   ├── test_load_testing.py
│   └── test_memory_usage.py
├── security/                   # Security tests
│   ├── test_input_validation.py
│   ├── test_security_scanning.py
│   └── test_access_control.py
└── fixtures/                   # Test data and fixtures
    ├── sample_documents/
    ├── test_databases/
    └── mock_apis/
```

### Unit Test Examples

```python
# agenthub/core/tools/builtin/tests/unit/test_document_tools.py
import pytest
import tempfile
import os
from agenthub.core.tools.builtin.document import document_search, document_parse

class TestDocumentTools:
    """Unit tests for document processing tools."""
    
    def test_document_search_basic(self):
        """Test basic document search functionality."""
        # Create test document
        test_doc = "This is a test document about machine learning algorithms."
        
        # Test search
        result = document_search(
            query="machine learning",
            source_path=None,
            max_results=5
        )
        
        assert result["success"] == True
        assert "results" in result
        assert len(result["results"]) <= 5
    
    def test_document_parse_pdf(self):
        """Test PDF document parsing."""
        # Create test PDF (mock)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"Mock PDF content")
            pdf_path = f.name
        
        try:
            result = document_parse(
                file_path=pdf_path,
                extract_metadata=True,
                extract_tables=True
            )
            
            assert result["success"] == True
            assert "data" in result
            assert "metadata" in result["data"]
        
        finally:
            os.unlink(pdf_path)
    
    def test_document_search_validation(self):
        """Test input validation for document search."""
        # Test empty query
        with pytest.raises(ValueError):
            document_search("")
        
        # Test invalid similarity threshold
        with pytest.raises(ValueError):
            document_search(
                "test query",
                similarity_threshold=1.5  # Invalid range
            )
    
    def test_document_parse_error_handling(self):
        """Test error handling for document parsing."""
        # Test non-existent file
        result = document_parse("non_existent_file.pdf")
        assert result["success"] == False
        assert "error" in result
        
        # Test invalid file format
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Not a PDF")
            txt_path = f.name
        
        try:
            result = document_parse(txt_path)
            assert result["success"] == False
            assert "error" in result
        
        finally:
            os.unlink(txt_path)

class TestWebTools:
    """Unit tests for web search and scraping tools."""
    
    def test_web_search_basic(self):
        """Test basic web search functionality."""
        result = web_search(
            query="python programming",
            engine="duckduckgo",
            max_results=5
        )
        
        assert result["success"] == True
        assert "results" in result
        assert len(result["results"]) <= 5
        
        # Verify result structure
        for item in result["results"]:
            assert "title" in item
            assert "url" in item
            assert "snippet" in item
    
    def test_web_scrape_basic(self):
        """Test basic web scraping functionality."""
        result = web_scrape(
            url="https://httpbin.org/html",
            extract_text=True,
            extract_metadata=True
        )
        
        assert result["success"] == True
        assert "data" in result
        assert "text" in result["data"]
        assert "metadata" in result["data"]
    
    def test_web_search_rate_limiting(self):
        """Test rate limiting functionality."""
        # Make multiple rapid requests
        results = []
        for i in range(10):
            result = web_search(f"test query {i}")
            results.append(result)
        
        # Should handle rate limiting gracefully
        successful_results = [r for r in results if r["success"]]
        assert len(successful_results) > 0

class TestCodeTools:
    """Unit tests for code generation and execution tools."""
    
    def test_code_execute_python(self):
        """Test Python code execution."""
        result = code_execute(
            code="print('Hello, World!')\nresult = 2 + 3",
            language="python",
            timeout=10
        )
        
        assert result["success"] == True
        assert "Hello, World!" in result["output"]
        assert "5" in result["output"]
    
    def test_code_generate_basic(self):
        """Test basic code generation."""
        result = code_generate(
            description="Create a function that adds two numbers",
            language="python",
            style="clean"
        )
        
        assert result["success"] == True
        assert "def" in result["code"]
        assert "add" in result["code"].lower()
    
    def test_code_execute_security(self):
        """Test code execution security."""
        # Test dangerous code
        result = code_execute(
            code="import os; os.system('ls')",
            language="python"
        )
        
        assert result["success"] == False
        assert "security" in result["error"].lower()
    
    def test_code_analyze_basic(self):
        """Test code analysis functionality."""
        test_code = """
def calculate_sum(a, b):
    return a + b

result = calculate_sum(5, 3)
print(result)
"""
        
        result = code_analyze(
            code=test_code,
            language="python",
            checks=["syntax", "security"]
        )
        
        assert result["success"] == True
        assert "analysis" in result
        assert "suggestions" in result

class TestDataTools:
    """Unit tests for data analysis tools."""
    
    def test_data_load_csv(self):
        """Test CSV data loading."""
        # Create test CSV
        csv_content = "name,age,city\nJohn,25,New York\nJane,30,Los Angeles"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_path = f.name
        
        try:
            result = data_load(
                source=csv_path,
                format="csv"
            )
            
            assert result["success"] == True
            assert "data_id" in result
            
            # Verify data was loaded correctly
            data_id = result["data_id"]
            explore_result = data_explore(data_id, "overview")
            assert explore_result["success"] == True
        
        finally:
            os.unlink(csv_path)
    
    def test_data_analyze_descriptive(self):
        """Test descriptive data analysis."""
        # Create test data
        import pandas as pd
        import numpy as np
        
        test_data = pd.DataFrame({
            'values': np.random.randn(100),
            'categories': np.random.choice(['A', 'B', 'C'], 100)
        })
        
        result = data_analyze(
            data=test_data,
            analysis_type="descriptive"
        )
        
        assert result["success"] == True
        assert "overview" in result["data"]
        assert "numeric_summary" in result["data"]
    
    def test_data_visualize_scatter(self):
        """Test data visualization."""
        import pandas as pd
        import numpy as np
        
        test_data = pd.DataFrame({
            'x': np.random.randn(50),
            'y': np.random.randn(50)
        })
        
        result = data_visualize(
            data=test_data,
            chart_type="scatter",
            x_column="x",
            y_column="y"
        )
        
        assert result["success"] == True
        assert "chart_type" in result
        assert "data" in result

class TestExternalTools:
    """Unit tests for external resource tools."""
    
    def test_database_query_sqlite(self):
        """Test SQLite database query."""
        result = database_query(
            query="SELECT 1 as test_value",
            database_type="sqlite",
            connection_string=":memory:"
        )
        
        assert result["success"] == True
        assert "data" in result
        assert result["data"][0]["test_value"] == 1
    
    def test_api_request_basic(self):
        """Test basic API request."""
        result = api_request(
            url="https://httpbin.org/get",
            method="GET"
        )
        
        assert result["success"] == True
        assert "status_code" in result
        assert result["status_code"] == 200
    
    def test_file_system_read(self):
        """Test file system read operation."""
        # Create test file
        test_content = "This is a test file."
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(test_content)
            file_path = f.name
        
        try:
            result = file_system(
                operation="read",
                path=file_path
            )
            
            assert result["success"] == True
            assert "content" in result
            assert result["content"] == test_content
        
        finally:
            os.unlink(file_path)
```

## 🔗 Integration Testing

### Cross-Tool Workflow Tests

```python
# agenthub/core/tools/builtin/tests/integration/test_tool_workflows.py
import pytest
from agenthub.core.tools.builtin import *

class TestToolWorkflows:
    """Integration tests for tool workflows."""
    
    def test_document_analysis_workflow(self):
        """Test complete document analysis workflow."""
        # 1. Search for documents
        search_result = document_search(
            query="machine learning research papers",
            max_results=3
        )
        
        assert search_result["success"] == True
        
        # 2. Parse documents
        parsed_docs = []
        for result in search_result["results"][:2]:  # Limit to 2 for testing
            parse_result = document_parse(
                file_path=result["file_path"],
                extract_metadata=True,
                extract_tables=True
            )
            if parse_result["success"]:
                parsed_docs.append(parse_result)
        
        assert len(parsed_docs) > 0
        
        # 3. Analyze content
        analysis_result = data_analyze(
            data=parsed_docs,
            analysis_type="text_analysis"
        )
        
        assert analysis_result["success"] == True
    
    def test_web_research_workflow(self):
        """Test web research workflow."""
        # 1. Search web
        search_result = web_search(
            query="artificial intelligence trends 2024",
            max_results=5
        )
        
        assert search_result["success"] == True
        
        # 2. Scrape top results
        scraped_content = []
        for result in search_result["results"][:3]:
            scrape_result = web_scrape(
                url=result["url"],
                extract_text=True,
                extract_metadata=True
            )
            if scrape_result["success"]:
                scraped_content.append(scrape_result)
        
        assert len(scraped_content) > 0
        
        # 3. Summarize content
        summaries = []
        for content in scraped_content[:2]:
            summary_result = web_summarize(
                url=content["url"],
                max_length=300
            )
            if summary_result["success"]:
                summaries.append(summary_result)
        
        assert len(summaries) > 0
    
    def test_code_development_workflow(self):
        """Test code development workflow."""
        # 1. Generate code
        code_result = code_generate(
            description="Create a function to calculate fibonacci numbers",
            language="python",
            include_tests=True
        )
        
        assert code_result["success"] == True
        
        # 2. Analyze generated code
        analysis_result = code_analyze(
            code=code_result["code"],
            language="python",
            checks=["syntax", "security", "performance"]
        )
        
        assert analysis_result["success"] == True
        
        # 3. Execute code
        execute_result = code_execute(
            code=code_result["code"],
            language="python"
        )
        
        assert execute_result["success"] == True
    
    def test_data_analysis_workflow(self):
        """Test data analysis workflow."""
        # 1. Load data
        data_result = data_load(
            source="test_data.csv",
            format="csv"
        )
        
        assert data_result["success"] == True
        
        # 2. Clean data
        clean_result = data_clean(
            data=data_result["data_id"],
            operations=["missing", "outliers"]
        )
        
        assert clean_result["success"] == True
        
        # 3. Analyze data
        analysis_result = data_analyze(
            data=clean_result["data_id"],
            analysis_type="descriptive"
        )
        
        assert analysis_result["success"] == True
        
        # 4. Create visualization
        viz_result = data_visualize(
            data=clean_result["data_id"],
            chart_type="histogram",
            x_column="value"
        )
        
        assert viz_result["success"] == True
    
    def test_external_integration_workflow(self):
        """Test external resource integration workflow."""
        # 1. Query database
        db_result = database_query(
            query="SELECT * FROM users LIMIT 10",
            database_type="sqlite",
            connection_string=":memory:"
        )
        
        assert db_result["success"] == True
        
        # 2. Send data to API
        api_result = api_request(
            url="https://httpbin.org/post",
            method="POST",
            json_data=db_result["data"]
        )
        
        assert api_result["success"] == True
        
        # 3. Store result in file
        file_result = file_system(
            operation="write",
            path="output.json",
            content=str(api_result["data"])
        )
        
        assert file_result["success"] == True
```

## ⚡ Performance Testing

### Benchmark Tests

```python
# agenthub/core/tools/builtin/tests/performance/test_benchmarks.py
import pytest
import time
import psutil
import os
from agenthub.core.tools.builtin import *

class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    def test_document_search_performance(self):
        """Test document search performance."""
        start_time = time.time()
        start_memory = psutil.Process(os.getpid()).memory_info().rss
        
        result = document_search(
            query="machine learning algorithms",
            max_results=100
        )
        
        end_time = time.time()
        end_memory = psutil.Process(os.getpid()).memory_info().rss
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        assert result["success"] == True
        assert execution_time < 5.0  # Should complete within 5 seconds
        assert memory_usage < 100 * 1024 * 1024  # Less than 100MB
    
    def test_web_search_performance(self):
        """Test web search performance."""
        start_time = time.time()
        
        result = web_search(
            query="python programming tutorials",
            max_results=20
        )
        
        execution_time = time.time() - start_time
        
        assert result["success"] == True
        assert execution_time < 3.0  # Should complete within 3 seconds
    
    def test_code_execution_performance(self):
        """Test code execution performance."""
        test_code = """
import time
import random

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Calculate fibonacci for numbers 0-20
results = []
for i in range(21):
    results.append(fibonacci(i))

print(f"Fibonacci sequence: {results}")
"""
        
        start_time = time.time()
        
        result = code_execute(
            code=test_code,
            language="python",
            timeout=10
        )
        
        execution_time = time.time() - start_time
        
        assert result["success"] == True
        assert execution_time < 2.0  # Should complete within 2 seconds
    
    def test_data_analysis_performance(self):
        """Test data analysis performance."""
        import pandas as pd
        import numpy as np
        
        # Create large test dataset
        large_data = pd.DataFrame({
            'value1': np.random.randn(10000),
            'value2': np.random.randn(10000),
            'category': np.random.choice(['A', 'B', 'C'], 10000)
        })
        
        start_time = time.time()
        
        result = data_analyze(
            data=large_data,
            analysis_type="descriptive"
        )
        
        execution_time = time.time() - start_time
        
        assert result["success"] == True
        assert execution_time < 3.0  # Should complete within 3 seconds
    
    def test_concurrent_tool_execution(self):
        """Test concurrent tool execution performance."""
        import concurrent.futures
        import threading
        
        def execute_tool(tool_name, params):
            if tool_name == "document_search":
                return document_search(**params)
            elif tool_name == "web_search":
                return web_search(**params)
            elif tool_name == "code_execute":
                return code_execute(**params)
        
        # Define concurrent operations
        operations = [
            ("document_search", {"query": "test query 1", "max_results": 10}),
            ("web_search", {"query": "test query 2", "max_results": 10}),
            ("code_execute", {"code": "print('Hello World')", "language": "python"}),
            ("document_search", {"query": "test query 3", "max_results": 10}),
            ("web_search", {"query": "test query 4", "max_results": 10})
        ]
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(execute_tool, op[0], op[1]) for op in operations]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        execution_time = time.time() - start_time
        
        # Verify all operations completed successfully
        successful_results = [r for r in results if r["success"]]
        assert len(successful_results) == len(operations)
        assert execution_time < 10.0  # All operations should complete within 10 seconds
```

### Load Testing

```python
# agenthub/core/tools/builtin/tests/performance/test_load_testing.py
import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from agenthub.core.tools.builtin import *

class TestLoadTesting:
    """Load testing for built-in tools."""
    
    def test_document_search_load(self):
        """Test document search under load."""
        def search_worker(worker_id):
            results = []
            for i in range(10):  # 10 searches per worker
                result = document_search(
                    query=f"test query {worker_id}-{i}",
                    max_results=5
                )
                results.append(result)
            return results
        
        # Run 20 concurrent workers
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(search_worker, i) for i in range(20)]
            all_results = []
            for future in futures:
                all_results.extend(future.result())
        
        # Verify all operations completed
        successful_results = [r for r in all_results if r["success"]]
        assert len(successful_results) > 0
        assert len(successful_results) / len(all_results) > 0.8  # 80% success rate
    
    def test_web_search_load(self):
        """Test web search under load."""
        def search_worker(worker_id):
            results = []
            for i in range(5):  # 5 searches per worker
                result = web_search(
                    query=f"test query {worker_id}-{i}",
                    max_results=3
                )
                results.append(result)
            return results
        
        # Run 10 concurrent workers
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(search_worker, i) for i in range(10)]
            all_results = []
            for future in futures:
                all_results.extend(future.result())
        
        # Verify all operations completed
        successful_results = [r for r in all_results if r["success"]]
        assert len(successful_results) > 0
```

## 🔒 Security Testing

### Input Validation Tests

```python
# agenthub/core/tools/builtin/tests/security/test_input_validation.py
import pytest
from agenthub.core.tools.builtin import *

class TestInputValidation:
    """Security tests for input validation."""
    
    def test_document_search_security(self):
        """Test document search input validation."""
        # Test path traversal
        with pytest.raises(SecurityError):
            document_search(
                query="test",
                source_path="../../../etc/passwd"
            )
        
        # Test malicious query
        with pytest.raises(SecurityError):
            document_search(
                query="<script>alert('xss')</script>"
            )
    
    def test_web_scrape_security(self):
        """Test web scraping input validation."""
        # Test malicious URL
        with pytest.raises(SecurityError):
            web_scrape(
                url="javascript:alert('xss')"
            )
        
        # Test file protocol
        with pytest.raises(SecurityError):
            web_scrape(
                url="file:///etc/passwd"
            )
    
    def test_code_execute_security(self):
        """Test code execution security."""
        # Test dangerous imports
        dangerous_code = [
            "import os; os.system('rm -rf /')",
            "import subprocess; subprocess.call(['rm', '-rf', '/'])",
            "eval('__import__(\"os\").system(\"ls\")')",
            "exec('import os; os.system(\"ls\")')"
        ]
        
        for code in dangerous_code:
            result = code_execute(code=code, language="python")
            assert result["success"] == False
            assert "security" in result["error"].lower()
    
    def test_database_query_security(self):
        """Test database query security."""
        # Test SQL injection
        malicious_queries = [
            "SELECT * FROM users; DROP TABLE users;",
            "SELECT * FROM users WHERE id = 1 OR 1=1",
            "SELECT * FROM users UNION SELECT * FROM passwords"
        ]
        
        for query in malicious_queries:
            result = database_query(
                query=query,
                database_type="sqlite",
                connection_string=":memory:"
            )
            assert result["success"] == False
            assert "security" in result["error"].lower()
    
    def test_file_system_security(self):
        """Test file system security."""
        # Test path traversal
        with pytest.raises(SecurityError):
            file_system(
                operation="read",
                path="../../../etc/passwd"
            )
        
        # Test absolute path
        with pytest.raises(SecurityError):
            file_system(
                operation="read",
                path="/etc/passwd"
            )
```

### Access Control Tests

```python
# agenthub/core/tools/builtin/tests/security/test_access_control.py
import pytest
from agenthub.core.tools.builtin import *

class TestAccessControl:
    """Security tests for access control."""
    
    def test_database_access_control(self):
        """Test database access control."""
        # Test unauthorized database access
        with pytest.raises(AccessDeniedError):
            database_query(
                query="SELECT * FROM sensitive_data",
                database_type="postgresql",
                connection_string="postgresql://unauthorized:user@localhost/db"
            )
    
    def test_api_access_control(self):
        """Test API access control."""
        # Test unauthorized API access
        result = api_request(
            url="https://api.requires-auth.com/data",
            method="GET"
        )
        
        assert result["success"] == False
        assert result["status_code"] == 401
    
    def test_file_system_access_control(self):
        """Test file system access control."""
        # Test access to restricted file
        result = file_system(
            operation="read",
            path="/root/.ssh/id_rsa"
        )
        
        assert result["success"] == False
        assert "permission" in result["error"].lower()
```

## 👥 User Acceptance Testing

### Real-World Scenario Tests

```python
# agenthub/core/tools/builtin/tests/acceptance/test_user_scenarios.py
import pytest
from agenthub.core.tools.builtin import *

class TestUserScenarios:
    """User acceptance tests for real-world scenarios."""
    
    def test_research_assistant_scenario(self):
        """Test research assistant scenario."""
        # 1. Search for research papers
        papers = document_search(
            query="artificial intelligence machine learning",
            max_results=5
        )
        
        assert papers["success"] == True
        assert len(papers["results"]) > 0
        
        # 2. Analyze papers
        analysis = []
        for paper in papers["results"][:2]:
            paper_analysis = document_analyze(
                file_path=paper["file_path"],
                analysis_type="comprehensive"
            )
            if paper_analysis["success"]:
                analysis.append(paper_analysis)
        
        assert len(analysis) > 0
        
        # 3. Generate summary
        summary = data_analyze(
            data=analysis,
            analysis_type="text_summary"
        )
        
        assert summary["success"] == True
    
    def test_data_scientist_scenario(self):
        """Test data scientist scenario."""
        # 1. Load dataset
        data = data_load(
            source="sales_data.csv",
            format="csv"
        )
        
        assert data["success"] == True
        
        # 2. Clean data
        cleaned = data_clean(
            data=data["data_id"],
            operations=["missing", "outliers", "duplicates"]
        )
        
        assert cleaned["success"] == True
        
        # 3. Analyze data
        analysis = data_analyze(
            data=cleaned["data_id"],
            analysis_type="correlation"
        )
        
        assert analysis["success"] == True
        
        # 4. Create visualization
        viz = data_visualize(
            data=cleaned["data_id"],
            chart_type="scatter",
            x_column="sales",
            y_column="profit"
        )
        
        assert viz["success"] == True
    
    def test_developer_scenario(self):
        """Test developer scenario."""
        # 1. Generate code
        code = code_generate(
            description="Create a REST API endpoint for user authentication",
            language="python",
            include_tests=True
        )
        
        assert code["success"] == True
        
        # 2. Analyze code
        analysis = code_analyze(
            code=code["code"],
            language="python",
            checks=["syntax", "security", "performance"]
        )
        
        assert analysis["success"] == True
        
        # 3. Execute tests
        test_result = code_execute(
            code=code["tests"],
            language="python"
        )
        
        assert test_result["success"] == True
```

## 📊 Test Execution and Reporting

### Test Configuration

```python
# agenthub/core/tools/builtin/tests/conftest.py
import pytest
import tempfile
import os
from agenthub.core.tools.builtin import *

@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="function")
def sample_document():
    """Create sample document for testing."""
    content = "This is a sample document for testing purposes."
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        yield f.name
    os.unlink(f.name)

@pytest.fixture(scope="function")
def sample_database():
    """Create sample database for testing."""
    # Create in-memory SQLite database
    return ":memory:"

@pytest.fixture(scope="function")
def mock_api_server():
    """Start mock API server for testing."""
    # Implementation for mock API server
    pass
```

### Test Execution Script

```python
# agenthub/core/tools/builtin/tests/run_tests.py
#!/usr/bin/env python3
"""Test execution script for built-in tools."""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run all test suites."""
    test_dir = Path(__file__).parent
    
    # Unit tests
    print("Running unit tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        str(test_dir / "unit"),
        "-v", "--tb=short"
    ])
    
    if result.returncode != 0:
        print("Unit tests failed!")
        return False
    
    # Integration tests
    print("Running integration tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        str(test_dir / "integration"),
        "-v", "--tb=short"
    ])
    
    if result.returncode != 0:
        print("Integration tests failed!")
        return False
    
    # Performance tests
    print("Running performance tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        str(test_dir / "performance"),
        "-v", "--tb=short"
    ])
    
    if result.returncode != 0:
        print("Performance tests failed!")
        return False
    
    # Security tests
    print("Running security tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        str(test_dir / "security"),
        "-v", "--tb=short"
    ])
    
    if result.returncode != 0:
        print("Security tests failed!")
        return False
    
    print("All tests passed!")
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
```

## 📈 Test Metrics and Coverage

### Coverage Requirements

- **Unit Tests**: 90%+ code coverage
- **Integration Tests**: 80%+ workflow coverage
- **Performance Tests**: All tools meet performance benchmarks
- **Security Tests**: 100% security vulnerability coverage
- **User Acceptance Tests**: 100% user scenario coverage

### Test Reporting

```python
# agenthub/core/tools/builtin/tests/test_reporting.py
import json
import time
from datetime import datetime

class TestReporter:
    """Generate comprehensive test reports."""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_suites": {},
            "summary": {}
        }
    
    def record_test_suite(self, suite_name: str, results: dict):
        """Record test suite results."""
        self.results["test_suites"][suite_name] = results
    
    def generate_report(self) -> dict:
        """Generate comprehensive test report."""
        # Calculate summary statistics
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for suite_name, suite_results in self.results["test_suites"].items():
            total_tests += suite_results["total"]
            passed_tests += suite_results["passed"]
            failed_tests += suite_results["failed"]
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        }
        
        return self.results
    
    def save_report(self, filename: str):
        """Save test report to file."""
        report = self.generate_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
```

This comprehensive testing strategy ensures that built-in tools are reliable, performant, secure, and meet user expectations in real-world scenarios.
