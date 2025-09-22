#!/usr/bin/env python3
"""
AgentHub Tool Benchmarking Runner

This script runs comprehensive benchmarks on AgentHub tools and generates
detailed performance reports.

Usage:
    python examples/benchmarking/run_benchmarks.py [options]

Options:
    --config FILE     Use custom configuration file
    --tools TOOLS     Comma-separated list of tools to benchmark
    --output DIR      Output directory for results
    --format FORMATS  Comma-separated list of output formats
    --quick           Run quick benchmark (fewer tests)
    --verbose         Enable verbose output
    --help            Show this help message
"""

import sys
import argparse
import yaml
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from examples.benchmarking.tool_benchmark_example import ToolBenchmarker


class BenchmarkRunner:
    """Main benchmark runner with configuration support."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize benchmark runner with configuration."""
        self.config = self._load_config(config_path)
        self.benchmarker = ToolBenchmarker()
        self.results = {}
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load benchmark configuration."""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            # Use default configuration
            default_config_path = Path(__file__).parent / "benchmark_config.yaml"
            if default_config_path.exists():
                with open(default_config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if no config file is available."""
        return {
            "benchmark": {
                "name": "AgentHub Tool Benchmark",
                "timeout": 300,
                "max_retries": 3
            },
            "tools": {
                "web_search": {"enabled": True},
                "web_scrape": {"enabled": True},
                "document_parse": {"enabled": True},
                "document_search": {"enabled": True}
            },
            "output": {
                "format": ["json"],
                "directory": "benchmark_results"
            }
        }
    
    def run_benchmarks(self, tools: Optional[List[str]] = None, quick: bool = False) -> Dict[str, Any]:
        """Run benchmarks for specified tools."""
        print("🚀 Starting AgentHub Tool Benchmarking")
        print("=" * 60)
        
        # Determine which tools to benchmark
        enabled_tools = self._get_enabled_tools(tools)
        
        if not enabled_tools:
            print("❌ No tools enabled for benchmarking")
            return {}
        
        print(f"📋 Tools to benchmark: {', '.join(enabled_tools)}")
        print(f"⚡ Quick mode: {'Yes' if quick else 'No'}")
        print()
        
        # Run benchmarks
        start_time = time.time()
        
        try:
            if "web_search" in enabled_tools:
                print("1️⃣  Web Search Tool Benchmarking")
                self.results["web_search"] = self.benchmarker.benchmark_web_search()
                print()
            
            if "web_scrape" in enabled_tools:
                print("2️⃣  Web Scrape Tool Benchmarking")
                self.results["web_scrape"] = self.benchmarker.benchmark_web_scrape()
                print()
            
            if "document_parse" in enabled_tools:
                print("3️⃣  Document Parse Tool Benchmarking")
                self.results["document_parse"] = self.benchmarker.benchmark_document_parse()
                print()
            
            if "document_search" in enabled_tools:
                print("4️⃣  Document Search Tool Benchmarking")
                self.results["document_search"] = self.benchmarker.benchmark_document_search()
                print()
            
            # Generate comprehensive report
            print("5️⃣  Generating Report...")
            report = self.benchmarker.generate_report()
            
            # Add benchmark metadata
            report["benchmark_info"] = {
                "config": self.config.get("benchmark", {}),
                "tools_tested": enabled_tools,
                "quick_mode": quick,
                "total_duration": time.time() - start_time,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.results["report"] = report
            
        except KeyboardInterrupt:
            print("\n⏹️  Benchmarking interrupted by user")
            return {"error": "Interrupted by user"}
        except Exception as e:
            print(f"\n❌ Benchmarking failed: {e}")
            return {"error": str(e)}
        
        return self.results
    
    def _get_enabled_tools(self, tools: Optional[List[str]]) -> List[str]:
        """Get list of enabled tools for benchmarking."""
        if tools:
            return [tool for tool in tools if self.config.get("tools", {}).get(tool, {}).get("enabled", False)]
        
        enabled_tools = []
        for tool_name, tool_config in self.config.get("tools", {}).items():
            if tool_config.get("enabled", False):
                enabled_tools.append(tool_name)
        
        return enabled_tools
    
    def save_results(self, output_dir: str, formats: List[str]) -> None:
        """Save benchmark results in specified formats."""
        if "report" not in self.results:
            print("❌ No results to save")
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        for format_type in formats:
            if format_type == "json":
                self._save_json_report(output_path, timestamp)
            elif format_type == "html":
                self._save_html_report(output_path, timestamp)
            elif format_type == "csv":
                self._save_csv_report(output_path, timestamp)
            else:
                print(f"⚠️  Unknown format: {format_type}")
    
    def _save_json_report(self, output_path: Path, timestamp: str) -> None:
        """Save results as JSON report."""
        report_file = output_path / f"benchmark_report_{timestamp}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.results["report"], f, indent=2)
        print(f"📄 JSON report saved: {report_file}")
    
    def _save_html_report(self, output_path: Path, timestamp: str) -> None:
        """Save results as HTML report."""
        report_file = output_path / f"benchmark_report_{timestamp}.html"
        
        html_content = self._generate_html_report()
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"📄 HTML report saved: {report_file}")
    
    def _save_csv_report(self, output_path: Path, timestamp: str) -> None:
        """Save results as CSV report."""
        import csv
        
        report_file = output_path / f"benchmark_results_{timestamp}.csv"
        
        with open(report_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                "Tool", "Test", "Execution Time (s)", "Memory Usage (MB)", 
                "Success", "Accuracy Score", "Error Message"
            ])
            
            # Write data
            for tool_name, results in self.results.items():
                if tool_name == "report":
                    continue
                    
                for result in results:
                    writer.writerow([
                        result.tool_name,
                        result.test_name,
                        f"{result.execution_time:.3f}",
                        f"{result.memory_usage:.1f}",
                        result.success,
                        f"{result.accuracy_score:.3f}" if result.accuracy_score else "",
                        result.error_message or ""
                    ])
        
        print(f"📄 CSV report saved: {report_file}")
    
    def _generate_html_report(self) -> str:
        """Generate HTML report."""
        report = self.results["report"]
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AgentHub Tool Benchmark Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .tool-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #e8f4f8; border-radius: 3px; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 AgentHub Tool Benchmark Report</h1>
        <p><strong>Generated:</strong> {report.get('timestamp', 'Unknown')}</p>
        <p><strong>Total Tests:</strong> {report.get('total_tests', 0)}</p>
    </div>
"""
        
        # Add tool sections
        for tool_name, tool_data in report.get("tools", {}).items():
            html += f"""
    <div class="tool-section">
        <h2>🔧 {tool_name.replace('_', ' ').title()}</h2>
        <div class="metric">Total Tests: {tool_data.get('total_tests', 0)}</div>
        <div class="metric">Success Rate: {tool_data.get('success_rate', 0):.1%}</div>
        <div class="metric">Avg Execution Time: {tool_data.get('average_execution_time', 0):.3f}s</div>
        <div class="metric">Avg Memory Usage: {tool_data.get('average_memory_usage', 0):.1f}MB</div>
        <div class="metric">Avg Accuracy: {tool_data.get('average_accuracy', 0):.2f}</div>
        
        <h3>Test Details</h3>
        <table>
            <tr>
                <th>Test Name</th>
                <th>Execution Time (s)</th>
                <th>Memory (MB)</th>
                <th>Success</th>
                <th>Accuracy</th>
                <th>Error</th>
            </tr>
"""
            
            for test in tool_data.get("test_details", []):
                success_class = "success" if test.get("success", False) else "error"
                html += f"""
            <tr>
                <td>{test.get('test_name', 'Unknown')}</td>
                <td>{test.get('execution_time', 0):.3f}</td>
                <td>{test.get('memory_usage', 0):.1f}</td>
                <td class="{success_class}">{'✓' if test.get('success', False) else '✗'}</td>
                <td>{f"{test.get('accuracy_score', 0):.3f}" if test.get('accuracy_score') is not None else 'N/A'}</td>
                <td>{test.get('error_message', '')}</td>
            </tr>
"""
            
            html += "        </table>\n    </div>\n"
        
        html += """
</body>
</html>
"""
        return html
    
    def print_summary(self) -> None:
        """Print benchmark summary."""
        if "report" not in self.results:
            print("❌ No results to summarize")
            return
        
        self.benchmarker.print_summary()


def main():
    """Main entry point for benchmark runner."""
    parser = argparse.ArgumentParser(description="AgentHub Tool Benchmarking Runner")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--tools", help="Comma-separated list of tools to benchmark")
    parser.add_argument("--output", default="benchmark_results", help="Output directory")
    parser.add_argument("--format", default="json,html", help="Output formats (comma-separated)")
    parser.add_argument("--quick", action="store_true", help="Run quick benchmark")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Parse tools list
    tools = None
    if args.tools:
        tools = [tool.strip() for tool in args.tools.split(",")]
    
    # Parse formats list
    formats = [fmt.strip() for fmt in args.format.split(",")]
    
    # Create and run benchmarker
    runner = BenchmarkRunner(args.config)
    
    try:
        # Run benchmarks
        results = runner.run_benchmarks(tools=tools, quick=args.quick)
        
        if "error" in results:
            print(f"❌ Benchmarking failed: {results['error']}")
            sys.exit(1)
        
        # Print summary
        runner.print_summary()
        
        # Save results
        runner.save_results(args.output, formats)
        
        print(f"\n✅ Benchmarking completed successfully!")
        print(f"📁 Results saved to: {args.output}")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
