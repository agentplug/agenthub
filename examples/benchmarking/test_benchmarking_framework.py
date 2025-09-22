#!/usr/bin/env python3
"""
Test Suite for AgentHub Benchmarking Framework

This test suite validates the benchmarking framework functionality,
ensures accurate metrics collection, and verifies report generation.

Usage:
    python examples/benchmarking/test_benchmarking_framework.py
"""

import sys
import unittest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from examples.benchmarking.tool_benchmark_example import ToolBenchmarker, BenchmarkResult
from examples.benchmarking.customer_demo import CustomerDemoBenchmarker


class TestBenchmarkingFramework(unittest.TestCase):
    """Test cases for the benchmarking framework."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.benchmarker = ToolBenchmarker()
        self.customer_demo = CustomerDemoBenchmarker()
        
    def test_benchmark_result_creation(self):
        """Test BenchmarkResult object creation."""
        result = BenchmarkResult(
            tool_name="test_tool",
            test_name="test_case",
            execution_time=1.5,
            memory_usage=50.0,
            success=True,
            accuracy_score=0.95
        )
        
        self.assertEqual(result.tool_name, "test_tool")
        self.assertEqual(result.test_name, "test_case")
        self.assertEqual(result.execution_time, 1.5)
        self.assertEqual(result.memory_usage, 50.0)
        self.assertTrue(result.success)
        self.assertEqual(result.accuracy_score, 0.95)
    
    def test_benchmark_result_error_handling(self):
        """Test BenchmarkResult with error handling."""
        result = BenchmarkResult(
            tool_name="test_tool",
            test_name="test_case",
            execution_time=0.5,
            memory_usage=10.0,
            success=False,
            error_message="Test error"
        )
        
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Test error")
        self.assertIsNone(result.accuracy_score)
    
    def test_memory_usage_tracking(self):
        """Test memory usage tracking functionality."""
        # Test with psutil available
        with patch('psutil.Process') as mock_process:
            mock_memory = Mock()
            mock_memory.rss = 100 * 1024 * 1024  # 100 MB
            mock_process.return_value.memory_info.return_value = mock_memory
            
            memory_usage = self.benchmarker._get_memory_usage()
            self.assertEqual(memory_usage, 100.0)
        
        # Test without psutil
        with patch('psutil.Process', side_effect=ImportError):
            memory_usage = self.benchmarker._get_memory_usage()
            self.assertEqual(memory_usage, 0.0)
    
    def test_search_quality_evaluation(self):
        """Test search quality evaluation."""
        # Test successful search result
        mock_result = {
            "success": True,
            "results": [
                {
                    "title": "Python programming tutorial",
                    "snippet": "Learn Python programming with this comprehensive tutorial",
                    "url": "https://example.com/python-tutorial"
                },
                {
                    "title": "Advanced Python concepts",
                    "snippet": "Master advanced Python programming techniques",
                    "url": "https://example.com/advanced-python"
                }
            ]
        }
        
        quality_score = self.benchmarker._evaluate_search_quality(mock_result, "Python programming")
        self.assertGreater(quality_score, 0.0)
        self.assertLessEqual(quality_score, 1.0)
        
        # Test failed search result
        failed_result = {"success": False, "results": []}
        quality_score = self.benchmarker._evaluate_search_quality(failed_result, "test query")
        self.assertEqual(quality_score, 0.0)
    
    def test_scraping_quality_evaluation(self):
        """Test scraping quality evaluation."""
        # Test successful scraping result
        mock_result = {
            "success": True,
            "text": "This is a sample web page content with meaningful information.",
            "links": ["https://example.com/link1", "https://example.com/link2"],
            "metadata": {"title": "Sample Page", "description": "A sample web page"}
        }
        
        quality_score = self.benchmarker._evaluate_scraping_quality(mock_result, "https://example.com")
        self.assertGreater(quality_score, 0.0)
        self.assertLessEqual(quality_score, 1.0)
        
        # Test failed scraping result
        failed_result = {"success": False}
        quality_score = self.benchmarker._evaluate_scraping_quality(failed_result, "https://example.com")
        self.assertEqual(quality_score, 0.0)
    
    def test_parsing_quality_evaluation(self):
        """Test parsing quality evaluation."""
        # Test successful parsing result
        mock_result = {
            "success": True,
            "content": "This is a sample document with meaningful content that should be extracted properly.",
            "metadata": {"title": "Sample Document", "author": "Test Author", "created": "2024-01-01"},
            "structure": {"headings": ["Introduction", "Main Content"], "paragraphs": 3}
        }
        
        quality_score = self.benchmarker._evaluate_parsing_quality(mock_result, "sample.txt")
        self.assertGreater(quality_score, 0.0)
        self.assertLessEqual(quality_score, 1.0)
        
        # Test failed parsing result
        failed_result = {"success": False}
        quality_score = self.benchmarker._evaluate_parsing_quality(failed_result, "sample.txt")
        self.assertEqual(quality_score, 0.0)
    
    def test_sample_document_creation(self):
        """Test sample document creation."""
        docs = self.benchmarker._create_sample_documents()
        
        self.assertIsInstance(docs, dict)
        self.assertGreater(len(docs), 0)
        
        # Check that all files exist
        for doc_name, doc_path in docs.items():
            self.assertTrue(os.path.exists(doc_path))
            self.assertTrue(os.path.getsize(doc_path) > 0)
        
        # Clean up
        for doc_path in docs.values():
            os.unlink(doc_path)
        os.rmdir(os.path.dirname(list(docs.values())[0]))
    
    def test_report_generation(self):
        """Test report generation functionality."""
        # Create mock results
        self.benchmarker.results = [
            BenchmarkResult(
                tool_name="test_tool",
                test_name="test_1",
                execution_time=1.0,
                memory_usage=50.0,
                success=True,
                accuracy_score=0.9
            ),
            BenchmarkResult(
                tool_name="test_tool",
                test_name="test_2",
                execution_time=2.0,
                memory_usage=75.0,
                success=True,
                accuracy_score=0.8
            ),
            BenchmarkResult(
                tool_name="test_tool",
                test_name="test_3",
                execution_time=0.5,
                memory_usage=25.0,
                success=False,
                error_message="Test error"
            )
        ]
        
        report = self.benchmarker.generate_report()
        
        self.assertIsInstance(report, dict)
        self.assertIn("timestamp", report)
        self.assertIn("total_tests", report)
        self.assertIn("tools", report)
        
        # Check tool-specific data
        self.assertIn("test_tool", report["tools"])
        tool_data = report["tools"]["test_tool"]
        
        self.assertEqual(tool_data["total_tests"], 3)
        self.assertEqual(tool_data["successful_tests"], 2)
        self.assertEqual(tool_data["failed_tests"], 1)
        self.assertEqual(tool_data["success_rate"], 2/3)
    
    def test_customer_demo_document_creation(self):
        """Test customer demo document creation."""
        docs = self.customer_demo._create_customer_demo_documents()
        
        self.assertIsInstance(docs, dict)
        self.assertGreater(len(docs), 0)
        
        # Check that all files exist and have content
        for doc_name, doc_path in docs.items():
            self.assertTrue(os.path.exists(doc_path))
            self.assertTrue(os.path.getsize(doc_path) > 0)
            
            # Check file content based on type
            if doc_name.endswith('.txt'):
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.assertIn("Business Performance Report", content)
            elif doc_name.endswith('.md'):
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.assertIn("AgentHub Platform", content)
            elif doc_name.endswith('.json'):
                with open(doc_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.assertIn("customer_metrics", data)
        
        # Clean up
        for doc_path in docs.values():
            os.unlink(doc_path)
        os.rmdir(os.path.dirname(list(docs.values())[0]))
    
    def test_customer_demo_search_quality(self):
        """Test customer demo search quality evaluation."""
        # Test with high-quality results
        mock_result = {
            "success": True,
            "results": [
                {
                    "title": "AI agent development best practices",
                    "snippet": "Comprehensive guide to developing AI agents with best practices and patterns",
                    "url": "https://example.com/ai-agents"
                },
                {
                    "title": "Enterprise AI solutions",
                    "snippet": "Enterprise-grade AI agent platforms for business automation",
                    "url": "https://example.com/enterprise-ai"
                }
            ]
        }
        
        quality_score = self.customer_demo._evaluate_search_quality_demo(mock_result, "AI agent development")
        self.assertGreater(quality_score, 0.0)
        self.assertLessEqual(quality_score, 1.0)
        
        # Test with low-quality results
        low_quality_result = {
            "success": True,
            "results": [
                {
                    "title": "Unrelated content",
                    "snippet": "This has nothing to do with the query",
                    "url": "https://example.com/unrelated"
                }
            ]
        }
        
        quality_score = self.customer_demo._evaluate_search_quality_demo(low_quality_result, "AI agent development")
        self.assertLess(quality_score, 0.5)
    
    def test_customer_demo_parsing_quality(self):
        """Test customer demo parsing quality evaluation."""
        # Test with high-quality parsing result
        mock_result = {
            "success": True,
            "content": "This is a comprehensive business report with detailed financial metrics and analysis.",
            "metadata": {
                "title": "Q4 Business Report",
                "author": "Finance Team",
                "created": "2024-01-15",
                "pages": 10,
                "word_count": 2500
            },
            "structure": {
                "headings": ["Executive Summary", "Financial Highlights", "Market Analysis"],
                "paragraphs": 15,
                "tables": 3
            }
        }
        
        quality_score = self.customer_demo._evaluate_parsing_quality_demo(mock_result, "business_report.txt")
        self.assertGreater(quality_score, 0.0)
        self.assertLessEqual(quality_score, 1.0)
        
        # Test with low-quality parsing result
        low_quality_result = {
            "success": True,
            "content": "Short content",
            "metadata": {},
            "structure": {}
        }
        
        quality_score = self.customer_demo._evaluate_parsing_quality_demo(low_quality_result, "sample.txt")
        self.assertLess(quality_score, 0.5)
    
    @patch('examples.benchmarking.tool_benchmark_example.web_search')
    def test_web_search_benchmark_mock(self, mock_web_search):
        """Test web search benchmarking with mocked function."""
        # Mock the web_search function
        mock_web_search.return_value = {
            "success": True,
            "results": [
                {
                    "title": "Test Result",
                    "snippet": "Test snippet",
                    "url": "https://example.com"
                }
            ]
        }
        
        # Mock memory usage tracking
        with patch.object(self.benchmarker, '_get_memory_usage', return_value=100.0):
            results = self.benchmarker.benchmark_web_search()
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Check that web_search was called
        self.assertTrue(mock_web_search.called)
    
    @patch('examples.benchmarking.tool_benchmark_example.document_parse')
    def test_document_parse_benchmark_mock(self, mock_document_parse):
        """Test document parsing benchmarking with mocked function."""
        # Mock the document_parse function
        mock_document_parse.return_value = {
            "success": True,
            "content": "Test document content",
            "metadata": {"title": "Test Document"},
            "structure": {"headings": ["Test Heading"]}
        }
        
        # Mock memory usage tracking
        with patch.object(self.benchmarker, '_get_memory_usage', return_value=100.0):
            results = self.benchmarker.benchmark_document_parse()
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Check that document_parse was called
        self.assertTrue(mock_document_parse.called)
    
    def test_benchmark_config_loading(self):
        """Test benchmark configuration loading."""
        # Test with default config
        config = self.benchmarker._load_config(None)
        self.assertIsInstance(config, dict)
        self.assertIn("benchmark", config)
        self.assertIn("tools", config)
    
    def test_customer_recommendations_generation(self):
        """Test customer recommendations generation."""
        mock_results = {
            "web_search": {
                "tool_type": "web_search",
                "success_rate": 0.95,
                "average_execution_time": 1.5,
                "average_accuracy": 0.88
            },
            "document_parse": {
                "tool_type": "document_parse",
                "success_rate": 0.90,
                "average_execution_time": 3.0,
                "average_accuracy": 0.92
            }
        }
        
        recommendations = self.customer_demo._generate_customer_recommendations(mock_results)
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Check that recommendations contain expected content
        recommendations_text = " ".join(recommendations)
        self.assertIn("excellent reliability", recommendations_text.lower())
        self.assertIn("fast response times", recommendations_text.lower())
        self.assertIn("high accuracy", recommendations_text.lower())


class TestBenchmarkingIntegration(unittest.TestCase):
    """Integration tests for the benchmarking framework."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.benchmarker = ToolBenchmarker()
    
    def test_end_to_end_benchmarking(self):
        """Test end-to-end benchmarking workflow."""
        # This test would run actual benchmarks if tools are available
        # For now, we'll test the workflow structure
        
        # Test configuration loading
        config = self.benchmarker._load_config(None)
        self.assertIsInstance(config, dict)
        
        # Test sample document creation
        docs = self.benchmarker._create_sample_documents()
        self.assertIsInstance(docs, dict)
        
        # Clean up
        for doc_path in docs.values():
            if os.path.exists(doc_path):
                os.unlink(doc_path)
        if docs:
            os.rmdir(os.path.dirname(list(docs.values())[0]))
    
    def test_report_export_formats(self):
        """Test report export in different formats."""
        # Create mock results
        self.benchmarker.results = [
            BenchmarkResult(
                tool_name="test_tool",
                test_name="test_1",
                execution_time=1.0,
                memory_usage=50.0,
                success=True,
                accuracy_score=0.9
            )
        ]
        
        # Test JSON report generation
        report = self.benchmarker.generate_report()
        self.assertIsInstance(report, dict)
        
        # Test that report can be serialized to JSON
        json_str = json.dumps(report)
        self.assertIsInstance(json_str, str)
        
        # Test that JSON can be parsed back
        parsed_report = json.loads(json_str)
        self.assertEqual(parsed_report["total_tests"], 1)


def run_benchmarking_tests():
    """Run all benchmarking tests."""
    print("🧪 Running AgentHub Benchmarking Framework Tests")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestBenchmarkingFramework))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestBenchmarkingIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_benchmarking_tests()
    sys.exit(0 if success else 1)
