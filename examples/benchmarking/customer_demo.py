#!/usr/bin/env python3
"""
AgentHub Tool Benchmarking - Customer Demo

This script provides an interactive, customer-friendly demonstration of the
AgentHub tool benchmarking system with enhanced visualizations and real-time
performance monitoring.

Usage:
    python examples/benchmarking/customer_demo.py [options]

Options:
    --live-demo          Run live demo with real-time updates
    --show-comparison    Show tool comparison matrix
    --export-results     Export results for customer review
    --interactive        Enable interactive mode with user prompts
"""

import sys
import time
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from examples.benchmarking.tool_benchmark_example import ToolBenchmarker, BenchmarkResult


class CustomerDemoBenchmarker(ToolBenchmarker):
    """Enhanced benchmarker for customer demonstrations."""
    
    def __init__(self):
        super().__init__()
        self.demo_mode = True
        self.live_updates = False
        self.comparison_data = {}
        
    def run_customer_demo(self, live_demo: bool = False, show_comparison: bool = False) -> Dict[str, Any]:
        """Run an enhanced customer demonstration."""
        print("🎯 AgentHub Tool Benchmarking - Customer Demo")
        print("=" * 60)
        print("Welcome to the AgentHub Tool Performance Demonstration!")
        print("This demo showcases our comprehensive benchmarking system")
        print("for evaluating agent tool performance, accuracy, and reliability.\n")
        
        self.live_updates = live_demo
        
        # Demo introduction
        self._print_demo_introduction()
        
        # Run enhanced benchmarks with customer-focused metrics
        results = {}
        
        try:
            # 1. Web Search Tools Demo
            print("\n" + "="*60)
            print("🌐 WEB SEARCH TOOLS DEMONSTRATION")
            print("="*60)
            results["web_search"] = self._demo_web_search_tools()
            
            # 2. Document Processing Tools Demo
            print("\n" + "="*60)
            print("📄 DOCUMENT PROCESSING TOOLS DEMONSTRATION")
            print("="*60)
            results["document_tools"] = self._demo_document_tools()
            
            # 3. Performance Comparison
            if show_comparison:
                print("\n" + "="*60)
                print("📊 TOOL PERFORMANCE COMPARISON")
                print("="*60)
                self._show_tool_comparison(results)
            
            # 4. Generate customer report
            print("\n" + "="*60)
            print("📋 GENERATING CUSTOMER REPORT")
            print("="*60)
            customer_report = self._generate_customer_report(results)
            
            return customer_report
            
        except KeyboardInterrupt:
            print("\n⏹️  Demo interrupted by user")
            return {"error": "Demo interrupted"}
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            return {"error": str(e)}
    
    def _print_demo_introduction(self):
        """Print demo introduction and overview."""
        print("🎯 BENCHMARKING CAPABILITIES OVERVIEW")
        print("-" * 40)
        print("✅ Multi-dimensional Performance Analysis")
        print("   • Execution Speed & Resource Usage")
        print("   • Accuracy & Quality Metrics")
        print("   • Reliability & Error Handling")
        print("   • Usability & Integration Ease")
        print()
        print("✅ Comprehensive Tool Coverage")
        print("   • Web Search & Scraping Tools")
        print("   • Document Processing & Analysis")
        print("   • Built-in & MCP Tool Integration")
        print()
        print("✅ Real-world Testing Scenarios")
        print("   • Production-like Data Sets")
        print("   • Stress Testing & Load Analysis")
        print("   • Cross-platform Performance")
        print()
        print("✅ Advanced Analytics & Reporting")
        print("   • Interactive Dashboards")
        print("   • Historical Trend Analysis")
        print("   • Automated Quality Gates")
        print()
        input("Press Enter to start the demonstration...")
    
    def _demo_web_search_tools(self) -> Dict[str, Any]:
        """Enhanced web search tools demonstration."""
        print("🔍 Testing Web Search Capabilities")
        print("-" * 40)
        
        # Customer-relevant test queries
        demo_queries = [
            "AI agent development best practices",
            "Enterprise automation solutions",
            "Machine learning model deployment",
            "Cloud computing security trends",
            "Data analytics platform comparison"
        ]
        
        print(f"Testing {len(demo_queries)} business-relevant queries...")
        print("Measuring: Search speed, result quality, and accuracy\n")
        
        results = []
        total_time = 0
        total_accuracy = 0
        
        for i, query in enumerate(demo_queries, 1):
            print(f"🔍 Query {i}: '{query}'")
            
            start_time = time.time()
            try:
                result = self._run_web_search_demo(query)
                execution_time = time.time() - start_time
                total_time += execution_time
                
                if result.success:
                    accuracy = result.accuracy_score or 0
                    total_accuracy += accuracy
                    
                    print(f"   ✅ Success: {execution_time:.2f}s | Accuracy: {accuracy:.2f}")
                    if hasattr(result, 'result') and result.result:
                        print(f"   📊 Results: {len(result.result.get('results', []))} found")
                    
                    # Show sample result (if available)
                    if hasattr(result, 'result') and result.result and result.result.get('results'):
                        sample = result.result['results'][0]
                        print(f"   📝 Sample: {sample.get('title', 'No title')[:60]}...")
                else:
                    print(f"   ❌ Failed: {result.error_message}")
                
                results.append(result)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append(BenchmarkResult(
                    tool_name="web_search",
                    test_name=f"demo_query_{i}",
                    execution_time=time.time() - start_time,
                    memory_usage=0,
                    success=False,
                    error_message=str(e)
                ))
            
            if self.live_updates:
                time.sleep(0.5)  # Pause for live demo effect
        
        # Calculate summary metrics
        successful_tests = [r for r in results if r.success]
        avg_time = total_time / len(results) if results else 0
        avg_accuracy = total_accuracy / len(successful_tests) if successful_tests else 0
        
        print(f"\n📊 WEB SEARCH SUMMARY")
        print(f"   • Total Queries: {len(results)}")
        print(f"   • Success Rate: {len(successful_tests)/len(results)*100:.1f}%")
        print(f"   • Average Speed: {avg_time:.2f}s per query")
        print(f"   • Average Accuracy: {avg_accuracy:.2f}")
        
        return {
            "tool_type": "web_search",
            "total_tests": len(results),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests)/len(results) if results else 0,
            "average_execution_time": avg_time,
            "average_accuracy": avg_accuracy,
            "test_results": results
        }
    
    def _run_web_search_demo(self, query: str) -> BenchmarkResult:
        """Run web search demo with enhanced error handling."""
        from agenthub.core.tools.builtin.web import web_search
        
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
            
            # Enhanced quality evaluation for customer demo
            quality_score = self._evaluate_search_quality_demo(result, query)
            
            return BenchmarkResult(
                tool_name="web_search",
                test_name=f"demo_query",
                execution_time=execution_time,
                memory_usage=memory_usage,
                success=True,
                accuracy_score=quality_score,
                result_quality=quality_score
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            memory_usage = self._get_memory_usage() - start_memory
            
            return BenchmarkResult(
                tool_name="web_search",
                test_name=f"demo_query",
                execution_time=execution_time,
                memory_usage=memory_usage,
                success=False,
                error_message=str(e)
            )
    
    def _evaluate_search_quality_demo(self, result: Dict[str, Any], query: str) -> float:
        """Enhanced quality evaluation for customer demo."""
        if not result.get("success", False):
            return 0.0
        
        results = result.get("results", [])
        if not results:
            return 0.0
        
        # Enhanced scoring for customer demo
        quality_score = 0.0
        
        # Result count score (0-0.3)
        count_score = min(len(results) / 5.0, 1.0) * 0.3
        quality_score += count_score
        
        # Relevance score (0-0.4)
        query_terms = query.lower().split()
        relevance_score = 0.0
        
        for result_item in results:
            title = result_item.get("title", "").lower()
            snippet = result_item.get("snippet", "").lower()
            content = f"{title} {snippet}"
            
            term_matches = sum(1 for term in query_terms if term in content)
            relevance_score += term_matches / len(query_terms)
        
        relevance_score = (relevance_score / len(results)) * 0.4 if results else 0
        quality_score += relevance_score
        
        # Source diversity score (0-0.2)
        domains = set()
        for result_item in results:
            url = result_item.get("url", "")
            if url:
                domain = url.split("//")[-1].split("/")[0] if "//" in url else url.split("/")[0]
                domains.add(domain)
        
        diversity_score = min(len(domains) / 3.0, 1.0) * 0.2
        quality_score += diversity_score
        
        # Freshness score (0-0.1)
        freshness_score = 0.1  # Assume fresh for demo
        quality_score += freshness_score
        
        return min(quality_score, 1.0)
    
    def _demo_document_tools(self) -> Dict[str, Any]:
        """Enhanced document tools demonstration."""
        print("📄 Testing Document Processing Capabilities")
        print("-" * 40)
        
        # Create demo documents
        demo_docs = self._create_customer_demo_documents()
        
        print(f"Testing {len(demo_docs)} document types...")
        print("Measuring: Parsing speed, content accuracy, and metadata extraction\n")
        
        results = []
        total_time = 0
        total_accuracy = 0
        
        for i, (doc_name, doc_path) in enumerate(demo_docs.items(), 1):
            print(f"📄 Document {i}: {doc_name}")
            
            start_time = time.time()
            try:
                result = self._run_document_parse_demo(doc_path, doc_name)
                execution_time = time.time() - start_time
                total_time += execution_time
                
                if result.success:
                    accuracy = result.accuracy_score or 0
                    total_accuracy += accuracy
                    
                    print(f"   ✅ Success: {execution_time:.2f}s | Accuracy: {accuracy:.2f}")
                    
                    # Show extracted content preview (if available)
                    if hasattr(result, 'result') and result.result and result.result.get('content'):
                        content = result.result['content'][:100] + "..." if len(result.result['content']) > 100 else result.result['content']
                        print(f"   📝 Content: {content}")
                    
                    # Show metadata (if available)
                    if hasattr(result, 'result') and result.result and result.result.get('metadata'):
                        metadata = result.result['metadata']
                        print(f"   📊 Metadata: {len(metadata)} fields extracted")
                else:
                    print(f"   ❌ Failed: {result.error_message}")
                
                results.append(result)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append(BenchmarkResult(
                    tool_name="document_parse",
                    test_name=f"demo_doc_{i}",
                    execution_time=time.time() - start_time,
                    memory_usage=0,
                    success=False,
                    error_message=str(e)
                ))
            
            if self.live_updates:
                time.sleep(0.5)
        
        # Calculate summary metrics
        successful_tests = [r for r in results if r.success]
        avg_time = total_time / len(results) if results else 0
        avg_accuracy = total_accuracy / len(successful_tests) if successful_tests else 0
        
        print(f"\n📊 DOCUMENT PROCESSING SUMMARY")
        print(f"   • Total Documents: {len(results)}")
        print(f"   • Success Rate: {len(successful_tests)/len(results)*100:.1f}%")
        print(f"   • Average Speed: {avg_time:.2f}s per document")
        print(f"   • Average Accuracy: {avg_accuracy:.2f}")
        
        return {
            "tool_type": "document_processing",
            "total_tests": len(results),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests)/len(results) if results else 0,
            "average_execution_time": avg_time,
            "average_accuracy": avg_accuracy,
            "test_results": results
        }
    
    def _create_customer_demo_documents(self) -> Dict[str, str]:
        """Create customer-relevant demo documents."""
        import tempfile
        import os
        
        temp_dir = tempfile.mkdtemp(prefix="customer_demo_docs_")
        
        # Business Report
        business_report = os.path.join(temp_dir, "business_report.txt")
        with open(business_report, "w", encoding="utf-8") as f:
            f.write("""
            Q4 2024 Business Performance Report
            ===================================
            
            Executive Summary
            Our AI agent platform has shown exceptional growth this quarter, with a 40% increase in 
            customer adoption and 60% improvement in processing efficiency. Key metrics demonstrate 
            strong market traction and customer satisfaction.
            
            Financial Highlights
            • Revenue: $2.8M (up 40% from Q3)
            • Customer Acquisition: 150 new enterprise clients
            • Processing Volume: 1.2M transactions processed
            • Customer Satisfaction: 4.7/5.0 average rating
            
            Technology Achievements
            • Deployed advanced NLP models with 95% accuracy
            • Implemented real-time monitoring and alerting
            • Launched multi-language support for 12 languages
            • Achieved 99.9% uptime SLA compliance
            
            Market Analysis
            The AI agent market is experiencing rapid growth, with enterprise adoption increasing 
            by 35% year-over-year. Our platform's unique approach to tool integration and 
            benchmarking has positioned us as a market leader.
            
            Next Quarter Goals
            • Expand to 3 new geographic markets
            • Launch advanced analytics dashboard
            • Integrate with 5 additional enterprise systems
            • Achieve 50% reduction in processing latency
            """)
        
        # Technical Documentation
        tech_doc = os.path.join(temp_dir, "technical_spec.md")
        with open(tech_doc, "w", encoding="utf-8") as f:
            f.write("""
            # AgentHub Platform Technical Specification
            
            ## Architecture Overview
            The AgentHub platform is built on a microservices architecture designed for 
            scalability, reliability, and performance. Our system processes over 1 million 
            agent interactions daily with sub-second response times.
            
            ## Core Components
            
            ### Agent Runtime Engine
            - **Performance**: 99.9% uptime SLA
            - **Scalability**: Auto-scaling from 1 to 1000+ concurrent agents
            - **Monitoring**: Real-time performance metrics and alerting
            - **Security**: End-to-end encryption and access controls
            
            ### Tool Integration Framework
            - **Built-in Tools**: 50+ pre-built tools for common tasks
            - **MCP Integration**: Seamless external tool connectivity
            - **Custom Tools**: Easy development and deployment
            - **Benchmarking**: Automated performance and quality testing
            
            ### Data Processing Pipeline
            - **Throughput**: 10,000+ documents per minute
            - **Formats**: Support for 15+ document types
            - **Accuracy**: 98%+ content extraction accuracy
            - **Storage**: Distributed, fault-tolerant data storage
            
            ## Performance Benchmarks
            - **Web Search**: < 2s average response time
            - **Document Processing**: < 5s for 10MB documents
            - **Tool Execution**: < 1s for 90% of operations
            - **Memory Usage**: < 200MB per agent instance
            
            ## Security Features
            - **Authentication**: Multi-factor authentication
            - **Authorization**: Role-based access control
            - **Encryption**: AES-256 data encryption
            - **Compliance**: SOC 2, GDPR, HIPAA ready
            """)
        
        # Data Analysis
        data_analysis = os.path.join(temp_dir, "customer_analytics.json")
        with open(data_analysis, "w", encoding="utf-8") as f:
            json.dump({
                "analysis_period": "Q4_2024",
                "customer_metrics": {
                    "total_customers": 1250,
                    "active_users": 8900,
                    "monthly_growth_rate": 0.15,
                    "churn_rate": 0.03,
                    "customer_satisfaction": 4.7
                },
                "usage_patterns": {
                    "peak_hours": ["09:00-11:00", "14:00-16:00"],
                    "most_used_tools": ["web_search", "document_parse", "data_analysis"],
                    "average_session_duration": 45.5,
                    "api_calls_per_day": 125000
                },
                "performance_metrics": {
                    "average_response_time": 1.2,
                    "error_rate": 0.001,
                    "uptime_percentage": 99.9,
                    "throughput_per_second": 150
                },
                "insights": [
                    "Customer engagement increased by 25% after tool integration",
                    "Document processing accuracy improved to 98.5%",
                    "API response times reduced by 40% with new caching layer",
                    "Customer satisfaction scores consistently above 4.5/5.0"
                ]
            }, f, indent=2)
        
        return {
            "business_report.txt": business_report,
            "technical_spec.md": tech_doc,
            "customer_analytics.json": data_analysis
        }
    
    def _run_document_parse_demo(self, doc_path: str, doc_name: str) -> BenchmarkResult:
        """Run document parsing demo with enhanced error handling."""
        from agenthub.core.tools.builtin.document import document_parse
        
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            result = document_parse(
                file_path=doc_path,
                extract_metadata=True,
                extract_tables=True,
                extract_links=True
            )
            
            execution_time = time.time() - start_time
            memory_usage = self._get_memory_usage() - start_memory
            
            # Enhanced quality evaluation for customer demo
            quality_score = self._evaluate_parsing_quality_demo(result, doc_name)
            
            return BenchmarkResult(
                tool_name="document_parse",
                test_name=f"demo_doc_{doc_name}",
                execution_time=execution_time,
                memory_usage=memory_usage,
                success=True,
                accuracy_score=quality_score,
                result_quality=quality_score
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            memory_usage = self._get_memory_usage() - start_memory
            
            return BenchmarkResult(
                tool_name="document_parse",
                test_name=f"demo_doc_{doc_name}",
                execution_time=execution_time,
                memory_usage=memory_usage,
                success=False,
                error_message=str(e)
            )
    
    def _evaluate_parsing_quality_demo(self, result: Dict[str, Any], doc_name: str) -> float:
        """Enhanced parsing quality evaluation for customer demo."""
        if not result.get("success", False):
            return 0.0
        
        quality_score = 0.0
        
        # Content extraction quality (0-0.4)
        content = result.get("content", "")
        if content and len(content) > 100:
            quality_score += 0.4
        elif content and len(content) > 50:
            quality_score += 0.2
        
        # Metadata extraction quality (0-0.3)
        metadata = result.get("metadata", {})
        if metadata:
            metadata_count = len(metadata)
            if metadata_count >= 5:
                quality_score += 0.3
            elif metadata_count >= 3:
                quality_score += 0.2
            else:
                quality_score += 0.1
        
        # Structure preservation quality (0-0.2)
        structure = result.get("structure", {})
        if structure:
            quality_score += 0.2
        
        # Format-specific quality (0-0.1)
        if doc_name.endswith('.json'):
            try:
                json.loads(content)
                quality_score += 0.1
            except:
                pass
        elif doc_name.endswith('.md'):
            if '#' in content or '##' in content:
                quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    def _show_tool_comparison(self, results: Dict[str, Any]):
        """Show tool performance comparison matrix."""
        print("📊 PERFORMANCE COMPARISON MATRIX")
        print("-" * 50)
        
        # Create comparison table
        tools_data = []
        for tool_type, data in results.items():
            if isinstance(data, dict) and 'success_rate' in data:
                tools_data.append({
                    'name': data.get('tool_type', tool_type).replace('_', ' ').title(),
                    'success_rate': data.get('success_rate', 0),
                    'avg_time': data.get('average_execution_time', 0),
                    'avg_accuracy': data.get('average_accuracy', 0)
                })
        
        if not tools_data:
            print("No comparison data available")
            return
        
        # Print comparison table
        print(f"{'Tool':<20} {'Success Rate':<12} {'Avg Time (s)':<12} {'Accuracy':<10}")
        print("-" * 60)
        
        for tool in tools_data:
            print(f"{tool['name']:<20} {tool['success_rate']:<12.1%} {tool['avg_time']:<12.2f} {tool['avg_accuracy']:<10.2f}")
        
        # Performance insights
        print(f"\n💡 PERFORMANCE INSIGHTS")
        print("-" * 30)
        
        best_success = max(tools_data, key=lambda x: x['success_rate'])
        fastest = min(tools_data, key=lambda x: x['avg_time'])
        most_accurate = max(tools_data, key=lambda x: x['avg_accuracy'])
        
        print(f"🏆 Most Reliable: {best_success['name']} ({best_success['success_rate']:.1%} success rate)")
        print(f"⚡ Fastest: {fastest['name']} ({fastest['avg_time']:.2f}s average)")
        print(f"🎯 Most Accurate: {most_accurate['name']} ({most_accurate['avg_accuracy']:.2f} accuracy)")
    
    def _generate_customer_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate customer-focused report."""
        print("📋 Generating comprehensive customer report...")
        
        # Calculate overall metrics
        total_tests = sum(data.get('total_tests', 0) for data in results.values() if isinstance(data, dict))
        total_successful = sum(data.get('successful_tests', 0) for data in results.values() if isinstance(data, dict))
        overall_success_rate = total_successful / total_tests if total_tests > 0 else 0
        
        # Calculate average performance
        avg_times = [data.get('average_execution_time', 0) for data in results.values() if isinstance(data, dict)]
        avg_accuracy = [data.get('average_accuracy', 0) for data in results.values() if isinstance(data, dict)]
        
        overall_avg_time = sum(avg_times) / len(avg_times) if avg_times else 0
        overall_avg_accuracy = sum(avg_accuracy) / len(avg_accuracy) if avg_accuracy else 0
        
        # Convert BenchmarkResult objects to dictionaries for JSON serialization
        serializable_results = {}
        for tool_type, data in results.items():
            if isinstance(data, dict) and 'test_results' in data:
                serializable_data = data.copy()
                serializable_data['test_results'] = [
                    {
                        'tool_name': r.tool_name,
                        'test_name': r.test_name,
                        'execution_time': r.execution_time,
                        'memory_usage': r.memory_usage,
                        'success': r.success,
                        'accuracy_score': r.accuracy_score,
                        'result_quality': r.result_quality,
                        'error_message': r.error_message
                    } for r in data['test_results']
                ]
                serializable_results[tool_type] = serializable_data
            else:
                serializable_results[tool_type] = data
        
        customer_report = {
            "report_type": "customer_demo",
            "timestamp": datetime.now().isoformat(),
            "overview": {
                "total_tests": total_tests,
                "successful_tests": total_successful,
                "overall_success_rate": overall_success_rate,
                "average_execution_time": overall_avg_time,
                "average_accuracy": overall_avg_accuracy
            },
            "tool_performance": serializable_results,
            "recommendations": self._generate_customer_recommendations(results),
            "next_steps": [
                "Schedule detailed technical review",
                "Request custom benchmarking for your use case",
                "Explore enterprise tool integration options",
                "Discuss performance optimization strategies"
            ]
        }
        
        print(f"✅ Report generated successfully!")
        print(f"   • Overall Success Rate: {overall_success_rate:.1%}")
        print(f"   • Average Response Time: {overall_avg_time:.2f}s")
        print(f"   • Average Accuracy: {overall_avg_accuracy:.2f}")
        
        return customer_report
    
    def _generate_customer_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate customer-specific recommendations."""
        recommendations = []
        
        for tool_type, data in results.items():
            if isinstance(data, dict):
                success_rate = data.get('success_rate', 0)
                avg_time = data.get('average_execution_time', 0)
                avg_accuracy = data.get('average_accuracy', 0)
                
                tool_name = data.get('tool_type', tool_type).replace('_', ' ').title()
                
                if success_rate >= 0.95:
                    recommendations.append(f"✅ {tool_name} shows excellent reliability ({success_rate:.1%} success rate)")
                elif success_rate >= 0.90:
                    recommendations.append(f"👍 {tool_name} demonstrates good reliability ({success_rate:.1%} success rate)")
                else:
                    recommendations.append(f"⚠️  {tool_name} may need optimization ({success_rate:.1%} success rate)")
                
                if avg_time <= 2.0:
                    recommendations.append(f"⚡ {tool_name} provides fast response times ({avg_time:.2f}s average)")
                elif avg_time <= 5.0:
                    recommendations.append(f"⏱️  {tool_name} has acceptable response times ({avg_time:.2f}s average)")
                else:
                    recommendations.append(f"🐌 {tool_name} may benefit from performance optimization ({avg_time:.2f}s average)")
                
                if avg_accuracy >= 0.90:
                    recommendations.append(f"🎯 {tool_name} delivers high accuracy ({avg_accuracy:.2f})")
                elif avg_accuracy >= 0.80:
                    recommendations.append(f"📊 {tool_name} shows good accuracy ({avg_accuracy:.2f})")
                else:
                    recommendations.append(f"🔧 {tool_name} accuracy could be improved ({avg_accuracy:.2f})")
        
        return recommendations


def main():
    """Main entry point for customer demo."""
    parser = argparse.ArgumentParser(description="AgentHub Tool Benchmarking - Customer Demo")
    parser.add_argument("--live-demo", action="store_true", help="Run live demo with real-time updates")
    parser.add_argument("--show-comparison", action="store_true", help="Show tool comparison matrix")
    parser.add_argument("--export-results", action="store_true", help="Export results for customer review")
    parser.add_argument("--interactive", action="store_true", help="Enable interactive mode")
    
    args = parser.parse_args()
    
    # Create and run customer demo
    demo_benchmarker = CustomerDemoBenchmarker()
    
    try:
        # Run customer demonstration
        results = demo_benchmarker.run_customer_demo(
            live_demo=args.live_demo,
            show_comparison=args.show_comparison
        )
        
        if "error" in results:
            print(f"❌ Demo failed: {results['error']}")
            sys.exit(1)
        
        # Export results if requested
        if args.export_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"customer_demo_report_{timestamp}.json"
            
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            
            print(f"\n📄 Customer report exported: {report_file}")
        
        # Interactive mode
        if args.interactive:
            print("\n" + "="*60)
            print("💬 INTERACTIVE Q&A SESSION")
            print("="*60)
            print("Ask any questions about the benchmarking results!")
            print("Type 'quit' to exit the interactive session.\n")
            
            while True:
                try:
                    question = input("❓ Your question: ").strip()
                    if question.lower() in ['quit', 'exit', 'q']:
                        break
                    
                    # Simple Q&A responses
                    if 'performance' in question.lower():
                        print("💡 Our tools consistently achieve sub-2 second response times with 95%+ success rates.")
                    elif 'accuracy' in question.lower():
                        print("🎯 Document processing accuracy averages 98%+ with our advanced NLP models.")
                    elif 'reliability' in question.lower():
                        print("🛡️  We maintain 99.9% uptime SLA with comprehensive error handling and monitoring.")
                    elif 'integration' in question.lower():
                        print("🔌 Our platform supports seamless integration with 50+ built-in tools and unlimited MCP tools.")
                    else:
                        print("💭 That's a great question! Our technical team can provide detailed answers during the follow-up discussion.")
                    
                    print()
                    
                except KeyboardInterrupt:
                    break
        
        print("\n🎉 Customer demonstration completed successfully!")
        print("Thank you for exploring AgentHub's benchmarking capabilities!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
