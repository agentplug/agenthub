#!/usr/bin/env python3
"""
Agent Tools Benchmarking Example

This example demonstrates how to use the AgentHub benchmarking system
to evaluate tool performance, accuracy, and reliability.
"""

import sys
import time
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import agenthub as ah
from agenthub.core.tools.builtin.web import web_search, web_scrape
from agenthub.core.tools.builtin.document import document_parse, document_search


@dataclass
class BenchmarkResult:
    """Container for benchmark test results."""
    tool_name: str
    test_name: str
    execution_time: float
    memory_usage: float
    success: bool
    error_message: Optional[str] = None
    accuracy_score: Optional[float] = None
    result_quality: Optional[float] = None


class ToolBenchmarker:
    """Simple tool benchmarking implementation."""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.test_data = self._load_test_data()
    
    def _load_test_data(self) -> Dict[str, Any]:
        """Load test data for benchmarking."""
        return {
            "web_search_queries": [
                "Python programming tutorial",
                "Machine learning best practices",
                "Climate change research",
                "Web development trends 2024",
                "Artificial intelligence ethics"
            ],
            "web_scrape_urls": [
                "https://httpbin.org/html",
                "https://httpbin.org/json",
                "https://example.com",
                "https://httpbin.org/xml"
            ],
            "document_files": [
                "sample_report.txt",
                "technical_doc.pdf",
                "data_analysis.json"
            ],
            "document_search_queries": [
                "revenue growth metrics",
                "technical implementation details",
                "customer satisfaction data",
                "performance optimization"
            ]
        }
    
    def benchmark_web_search(self) -> List[BenchmarkResult]:
        """Benchmark web search tool performance."""
        print("🔍 Benchmarking Web Search Tool...")
        results = []
        
        for i, query in enumerate(self.test_data["web_search_queries"]):
            print(f"  Test {i+1}/5: '{query}'")
            
            start_time = time.time()
            start_memory = self._get_memory_usage()
            
            try:
                result = web_search(
                    query=query,
                    max_results=5,
                    engine="duckduckgo"
                )
                
                execution_time = time.time() - start_time
                memory_usage = self._get_memory_usage() - start_memory
                
                # Evaluate result quality
                quality_score = self._evaluate_search_quality(result, query)
                
                benchmark_result = BenchmarkResult(
                    tool_name="web_search",
                    test_name=f"search_query_{i+1}",
                    execution_time=execution_time,
                    memory_usage=memory_usage,
                    success=True,
                    accuracy_score=quality_score,
                    result_quality=quality_score
                )
                
            except Exception as e:
                execution_time = time.time() - start_time
                memory_usage = self._get_memory_usage() - start_memory
                
                benchmark_result = BenchmarkResult(
                    tool_name="web_search",
                    test_name=f"search_query_{i+1}",
                    execution_time=execution_time,
                    memory_usage=memory_usage,
                    success=False,
                    error_message=str(e)
                )
            
            results.append(benchmark_result)
            self.results.append(benchmark_result)
        
        return results
    
    def benchmark_web_scrape(self) -> List[BenchmarkResult]:
        """Benchmark web scraping tool performance."""
        print("🕷️  Benchmarking Web Scrape Tool...")
        results = []
        
        for i, url in enumerate(self.test_data["web_scrape_urls"]):
            print(f"  Test {i+1}/4: '{url}'")
            
            start_time = time.time()
            start_memory = self._get_memory_usage()
            
            try:
                result = web_scrape(
                    url=url,
                    extract_text=True,
                    extract_links=True
                )
                
                execution_time = time.time() - start_time
                memory_usage = self._get_memory_usage() - start_memory
                
                # Evaluate scraping quality
                quality_score = self._evaluate_scraping_quality(result, url)
                
                benchmark_result = BenchmarkResult(
                    tool_name="web_scrape",
                    test_name=f"scrape_url_{i+1}",
                    execution_time=execution_time,
                    memory_usage=memory_usage,
                    success=True,
                    accuracy_score=quality_score,
                    result_quality=quality_score
                )
                
            except Exception as e:
                execution_time = time.time() - start_time
                memory_usage = self._get_memory_usage() - start_memory
                
                benchmark_result = BenchmarkResult(
                    tool_name="web_scrape",
                    test_name=f"scrape_url_{i+1}",
                    execution_time=execution_time,
                    memory_usage=memory_usage,
                    success=False,
                    error_message=str(e)
                )
            
            results.append(benchmark_result)
            self.results.append(benchmark_result)
        
        return results
    
    def benchmark_document_parse(self) -> List[BenchmarkResult]:
        """Benchmark document parsing tool performance."""
        print("📄 Benchmarking Document Parse Tool...")
        results = []
        
        # Create sample documents for testing
        sample_docs = self._create_sample_documents()
        
        for i, (doc_name, doc_path) in enumerate(sample_docs.items()):
            print(f"  Test {i+1}/{len(sample_docs)}: '{doc_name}'")
            
            start_time = time.time()
            start_memory = self._get_memory_usage()
            
            try:
                result = document_parse(
                    file_path=doc_path,
                    extract_metadata=True,
                    extract_tables=True
                )
                
                execution_time = time.time() - start_time
                memory_usage = self._get_memory_usage() - start_memory
                
                # Evaluate parsing quality
                quality_score = self._evaluate_parsing_quality(result, doc_name)
                
                benchmark_result = BenchmarkResult(
                    tool_name="document_parse",
                    test_name=f"parse_{doc_name}",
                    execution_time=execution_time,
                    memory_usage=memory_usage,
                    success=True,
                    accuracy_score=quality_score,
                    result_quality=quality_score
                )
                
            except Exception as e:
                execution_time = time.time() - start_time
                memory_usage = self._get_memory_usage() - start_memory
                
                benchmark_result = BenchmarkResult(
                    tool_name="document_parse",
                    test_name=f"parse_{doc_name}",
                    execution_time=execution_time,
                    memory_usage=memory_usage,
                    success=False,
                    error_message=str(e)
                )
            
            results.append(benchmark_result)
            self.results.append(benchmark_result)
        
        return results
    
    def benchmark_document_search(self) -> List[BenchmarkResult]:
        """Benchmark document search tool performance."""
        print("🔍 Benchmarking Document Search Tool...")
        results = []
        
        # Create sample documents for search testing
        sample_docs = self._create_sample_documents()
        doc_directory = Path(sample_docs[list(sample_docs.keys())[0]]).parent
        
        for i, query in enumerate(self.test_data["document_search_queries"]):
            print(f"  Test {i+1}/4: '{query}'")
            
            start_time = time.time()
            start_memory = self._get_memory_usage()
            
            try:
                result = document_search(
                    query=query,
                    source_path=str(doc_directory),
                    max_results=5,
                    similarity_threshold=0.7
                )
                
                execution_time = time.time() - start_time
                memory_usage = self._get_memory_usage() - start_memory
                
                # Evaluate search quality
                quality_score = self._evaluate_search_quality(result, query)
                
                benchmark_result = BenchmarkResult(
                    tool_name="document_search",
                    test_name=f"search_query_{i+1}",
                    execution_time=execution_time,
                    memory_usage=memory_usage,
                    success=True,
                    accuracy_score=quality_score,
                    result_quality=quality_score
                )
                
            except Exception as e:
                execution_time = time.time() - start_time
                memory_usage = self._get_memory_usage() - start_memory
                
                benchmark_result = BenchmarkResult(
                    tool_name="document_search",
                    test_name=f"search_query_{i+1}",
                    execution_time=execution_time,
                    memory_usage=memory_usage,
                    success=False,
                    error_message=str(e)
                )
            
            results.append(benchmark_result)
            self.results.append(benchmark_result)
        
        return results
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return 0.0
    
    def _evaluate_search_quality(self, result: Dict[str, Any], query: str) -> float:
        """Evaluate the quality of search results."""
        if not result.get("success", False):
            return 0.0
        
        results = result.get("results", [])
        if not results:
            return 0.0
        
        # Simple quality evaluation based on result count and relevance
        quality_score = min(len(results) / 5.0, 1.0)  # Normalize to 0-1
        
        # Check for query terms in results
        query_terms = query.lower().split()
        relevance_bonus = 0.0
        
        for result_item in results:
            title = result_item.get("title", "").lower()
            snippet = result_item.get("snippet", "").lower()
            content = f"{title} {snippet}"
            
            term_matches = sum(1 for term in query_terms if term in content)
            relevance_bonus += term_matches / len(query_terms)
        
        relevance_bonus = relevance_bonus / len(results) if results else 0
        quality_score = (quality_score + relevance_bonus) / 2
        
        return min(quality_score, 1.0)
    
    def _evaluate_scraping_quality(self, result: Dict[str, Any], url: str) -> float:
        """Evaluate the quality of scraping results."""
        if not result.get("success", False):
            return 0.0
        
        # Check if we got meaningful content
        text_content = result.get("text", "")
        links = result.get("links", [])
        
        quality_score = 0.0
        
        # Text content quality
        if text_content and len(text_content) > 100:
            quality_score += 0.5
        
        # Links extraction quality
        if links and len(links) > 0:
            quality_score += 0.3
        
        # Metadata quality
        metadata = result.get("metadata", {})
        if metadata:
            quality_score += 0.2
        
        return min(quality_score, 1.0)
    
    def _evaluate_parsing_quality(self, result: Dict[str, Any], doc_name: str) -> float:
        """Evaluate the quality of document parsing results."""
        if not result.get("success", False):
            return 0.0
        
        quality_score = 0.0
        
        # Content extraction quality
        content = result.get("content", "")
        if content and len(content) > 50:
            quality_score += 0.4
        
        # Metadata extraction quality
        metadata = result.get("metadata", {})
        if metadata:
            quality_score += 0.3
        
        # Structure preservation quality
        structure = result.get("structure", {})
        if structure:
            quality_score += 0.3
        
        return min(quality_score, 1.0)
    
    def _create_sample_documents(self) -> Dict[str, str]:
        """Create sample documents for testing."""
        import tempfile
        import os
        
        temp_dir = tempfile.mkdtemp(prefix="benchmark_docs_")
        
        # Create sample text document
        txt_file = os.path.join(temp_dir, "sample_report.txt")
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write("""
            Quarterly Business Report
            ========================
            
            Executive Summary
            This quarter showed significant growth in revenue and customer satisfaction.
            Key metrics include:
            - Revenue growth: 15% increase
            - Customer satisfaction: 4.2/5.0
            - Market share: 12% increase
            
            Financial Performance
            Revenue: $2.5M (up 15% from last quarter)
            Profit margin: 18% (up 2% from last quarter)
            Customer acquisition cost: $150 (down 10%)
            
            Technology Initiatives
            - Implemented new AI-powered analytics platform
            - Upgraded customer service system
            - Enhanced security measures
            """)
        
        # Create sample JSON document
        json_file = os.path.join(temp_dir, "data_analysis.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump({
                "analysis_type": "customer_behavior",
                "period": "Q3_2024",
                "metrics": {
                    "total_customers": 12500,
                    "active_users": 8900,
                    "conversion_rate": 0.15,
                    "churn_rate": 0.05
                },
                "insights": [
                    "Mobile usage increased by 25%",
                    "Peak activity hours: 2-4 PM",
                    "Most popular features: search, recommendations"
                ]
            }, f, indent=2)
        
        # Create sample markdown document
        md_file = os.path.join(temp_dir, "technical_doc.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write("""
            # Technical Documentation
            
            ## System Architecture
            The system is built using microservices architecture with the following components:
            
            ### API Gateway
            - Handles all incoming requests
            - Implements rate limiting and authentication
            - Routes requests to appropriate services
            
            ### User Service
            - Manages user accounts and authentication
            - Handles user preferences and settings
            - Integrates with external identity providers
            
            ### Data Service
            - Manages data storage and retrieval
            - Implements caching for performance
            - Handles data synchronization
            
            ## Performance Optimization
            - Database indexing for fast queries
            - Redis caching for frequently accessed data
            - CDN for static content delivery
            """)
        
        return {
            "sample_report.txt": txt_file,
            "data_analysis.json": json_file,
            "technical_doc.md": md_file
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive benchmark report."""
        if not self.results:
            return {"error": "No benchmark results available"}
        
        # Group results by tool
        tool_results = {}
        for result in self.results:
            if result.tool_name not in tool_results:
                tool_results[result.tool_name] = []
            tool_results[result.tool_name].append(result)
        
        # Calculate metrics for each tool
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "tools": {}
        }
        
        for tool_name, results in tool_results.items():
            successful_tests = [r for r in results if r.success]
            failed_tests = [r for r in results if not r.success]
            
            if successful_tests:
                avg_execution_time = sum(r.execution_time for r in successful_tests) / len(successful_tests)
                avg_memory_usage = sum(r.memory_usage for r in successful_tests) / len(successful_tests)
                avg_accuracy = sum(r.accuracy_score or 0 for r in successful_tests) / len(successful_tests)
            else:
                avg_execution_time = 0
                avg_memory_usage = 0
                avg_accuracy = 0
            
            report["tools"][tool_name] = {
                "total_tests": len(results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(failed_tests),
                "success_rate": len(successful_tests) / len(results) if results else 0,
                "average_execution_time": avg_execution_time,
                "average_memory_usage": avg_memory_usage,
                "average_accuracy": avg_accuracy,
                "test_details": [
                    {
                        "test_name": r.test_name,
                        "execution_time": r.execution_time,
                        "memory_usage": r.memory_usage,
                        "success": r.success,
                        "accuracy_score": r.accuracy_score,
                        "error_message": r.error_message
                    }
                    for r in results
                ]
            }
        
        return report
    
    def print_summary(self):
        """Print a summary of benchmark results."""
        print("\n" + "="*80)
        print("📊 BENCHMARK RESULTS SUMMARY")
        print("="*80)
        
        if not self.results:
            print("No benchmark results available.")
            return
        
        # Group results by tool
        tool_results = {}
        for result in self.results:
            if result.tool_name not in tool_results:
                tool_results[result.tool_name] = []
            tool_results[result.tool_name].append(result)
        
        for tool_name, results in tool_results.items():
            successful_tests = [r for r in results if r.success]
            failed_tests = [r for r in results if not r.success]
            
            print(f"\n🔧 {tool_name.upper()}")
            print("-" * 40)
            print(f"Total Tests: {len(results)}")
            print(f"Successful: {len(successful_tests)}")
            print(f"Failed: {len(failed_tests)}")
            print(f"Success Rate: {len(successful_tests)/len(results)*100:.1f}%")
            
            if successful_tests:
                avg_time = sum(r.execution_time for r in successful_tests) / len(successful_tests)
                avg_memory = sum(r.memory_usage for r in successful_tests) / len(successful_tests)
                avg_accuracy = sum(r.accuracy_score or 0 for r in successful_tests) / len(successful_tests)
                
                print(f"Avg Execution Time: {avg_time:.3f}s")
                print(f"Avg Memory Usage: {avg_memory:.1f}MB")
                print(f"Avg Accuracy: {avg_accuracy:.2f}")
            
            if failed_tests:
                print(f"\n❌ Failed Tests:")
                for test in failed_tests:
                    print(f"  - {test.test_name}: {test.error_message}")


def main():
    """Run comprehensive tool benchmarking."""
    print("🚀 Starting Agent Tools Benchmarking")
    print("="*50)
    
    benchmarker = ToolBenchmarker()
    
    try:
        # Run all benchmarks
        print("\n1. Web Search Tool Benchmarking")
        benchmarker.benchmark_web_search()
        
        print("\n2. Web Scrape Tool Benchmarking")
        benchmarker.benchmark_web_scrape()
        
        print("\n3. Document Parse Tool Benchmarking")
        benchmarker.benchmark_document_parse()
        
        print("\n4. Document Search Tool Benchmarking")
        benchmarker.benchmark_document_search()
        
        # Generate and display results
        print("\n5. Generating Report...")
        report = benchmarker.generate_report()
        
        # Print summary
        benchmarker.print_summary()
        
        # Save detailed report
        report_file = "benchmark_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Benchmarking interrupted by user")
    except Exception as e:
        print(f"\n❌ Benchmarking failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Benchmarking completed!")


if __name__ == "__main__":
    main()
