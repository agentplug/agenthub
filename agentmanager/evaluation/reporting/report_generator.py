"""
Report generator for evaluation results.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from ..core.data_models import EvaluationResults


class ReportGenerator:
    """Main report generator for evaluation results."""
    
    def __init__(self):
        """Initialize report generator."""
        self._html_reporter = HTMLReporter()
        self._json_reporter = JSONReporter()
    
    def generate_report(
        self, 
        results: EvaluationResults, 
        format_type: str = "html"
    ) -> str:
        """
        Generate a report from evaluation results.
        
        Args:
            results: Evaluation results to report on
            format_type: Report format ("html", "json", "text")
            
        Returns:
            Generated report as string
        """
        if format_type.lower() == "html":
            return self._html_reporter.generate(results)
        elif format_type.lower() == "json":
            return self._json_reporter.generate(results)
        elif format_type.lower() == "text":
            return self._generate_text_report(results)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
    
    def _generate_text_report(self, results: EvaluationResults) -> str:
        """Generate a simple text report."""
        report = []
        report.append("=" * 60)
        report.append(f"EVALUATION REPORT - {results.agent_name}")
        report.append("=" * 60)
        report.append(f"Evaluation Mode: {results.evaluation_mode.value}")
        report.append(f"Timestamp: {results.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Duration: {results.duration:.2f} seconds")
        report.append(f"Total Evaluations: {results.total_evaluations}")
        report.append(f"Success Rate: {results.success_rate:.2%}")
        report.append("")
        
        if results.benchmark_name:
            report.append(f"Benchmark: {results.benchmark_name}")
            report.append("")
        
        # Summary metrics
        if results.summary_metrics:
            report.append("SUMMARY METRICS:")
            report.append("-" * 20)
            for metric, value in results.summary_metrics.items():
                if isinstance(value, float):
                    report.append(f"{metric}: {value:.3f}")
                else:
                    report.append(f"{metric}: {value}")
            report.append("")
        
        # Individual results
        report.append("INDIVIDUAL RESULTS:")
        report.append("-" * 20)
        for i, result in enumerate(results.results, 1):
            report.append(f"\nResult {i}:")
            report.append(f"  Input: {result.agent_output.input_text[:100]}...")
            report.append(f"  Output: {result.agent_output.output_text[:100]}...")
            
            if result.metrics:
                report.append("  Metrics:")
                for metric_name, metric_result in result.metrics.items():
                    report.append(f"    {metric_name}: {metric_result.value:.3f}")
        
        return "\n".join(report)
    
    def get_available_formats(self) -> list:
        """Get list of available report formats."""
        return ["html", "json", "text"]


class HTMLReporter:
    """HTML report generator."""
    
    def generate(self, results: EvaluationResults) -> str:
        """Generate HTML report."""
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html>")
        html.append("<head>")
        html.append("<title>Evaluation Report</title>")
        html.append("<style>")
        html.append(self._get_css_styles())
        html.append("</style>")
        html.append("</head>")
        html.append("<body>")
        
        # Header
        html.append("<div class='header'>")
        html.append(f"<h1>Evaluation Report - {results.agent_name}</h1>")
        html.append(f"<p>Generated: {results.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>")
        html.append("</div>")
        
        # Summary
        html.append("<div class='summary'>")
        html.append("<h2>Summary</h2>")
        html.append(f"<p><strong>Mode:</strong> {results.evaluation_mode.value}</p>")
        html.append(f"<p><strong>Duration:</strong> {results.duration:.2f} seconds</p>")
        html.append(f"<p><strong>Total Evaluations:</strong> {results.total_evaluations}</p>")
        html.append(f"<p><strong>Success Rate:</strong> {results.success_rate:.2%}</p>")
        if results.benchmark_name:
            html.append(f"<p><strong>Benchmark:</strong> {results.benchmark_name}</p>")
        html.append("</div>")
        
        # Metrics
        if results.summary_metrics:
            html.append("<div class='metrics'>")
            html.append("<h2>Summary Metrics</h2>")
            html.append("<table>")
            html.append("<tr><th>Metric</th><th>Value</th></tr>")
            for metric, value in results.summary_metrics.items():
                if isinstance(value, float):
                    html.append(f"<tr><td>{metric}</td><td>{value:.3f}</td></tr>")
                else:
                    html.append(f"<tr><td>{metric}</td><td>{value}</td></tr>")
            html.append("</table>")
            html.append("</div>")
        
        # Individual results
        html.append("<div class='results'>")
        html.append("<h2>Individual Results</h2>")
        for i, result in enumerate(results.results, 1):
            html.append(f"<div class='result-item'>")
            html.append(f"<h3>Result {i}</h3>")
            html.append(f"<p><strong>Input:</strong> {result.agent_output.input_text}</p>")
            html.append(f"<p><strong>Output:</strong> {result.agent_output.output_text}</p>")
            
            if result.metrics:
                html.append("<table class='metrics-table'>")
                html.append("<tr><th>Metric</th><th>Value</th><th>Type</th></tr>")
                for metric_name, metric_result in result.metrics.items():
                    html.append(f"<tr><td>{metric_name}</td><td>{metric_result.value:.3f}</td><td>{metric_result.metric_type}</td></tr>")
                html.append("</table>")
            
            html.append("</div>")
        html.append("</div>")
        
        html.append("</body>")
        html.append("</html>")
        
        return "\n".join(html)
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for HTML report."""
        return """
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }
        .header {
            background-color: #f4f4f4;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .summary, .metrics, .results {
            margin-bottom: 30px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .result-item {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }
        .metrics-table {
            margin-top: 10px;
        }
        """


class JSONReporter:
    """JSON report generator."""
    
    def generate(self, results: EvaluationResults) -> str:
        """Generate JSON report."""
        # Convert results to dictionary
        data = {
            "agent_name": results.agent_name,
            "evaluation_mode": results.evaluation_mode.value,
            "timestamp": results.timestamp.isoformat(),
            "duration": results.duration,
            "total_evaluations": results.total_evaluations,
            "success_rate": results.success_rate,
            "error_count": results.error_count,
            "benchmark_name": results.benchmark_name,
            "summary_metrics": results.summary_metrics,
            "results": []
        }
        
        # Add individual results
        for result in results.results:
            result_data = {
                "input_text": result.agent_output.input_text,
                "output_text": result.agent_output.output_text,
                "timestamp": result.agent_output.timestamp.isoformat(),
                "metadata": result.agent_output.metadata,
                "metrics": {}
            }
            
            # Add metrics
            for metric_name, metric_result in result.metrics.items():
                result_data["metrics"][metric_name] = {
                    "value": metric_result.value,
                    "metric_type": metric_result.metric_type,
                    "confidence": metric_result.confidence,
                    "metadata": metric_result.metadata,
                    "timestamp": metric_result.timestamp.isoformat()
                }
            
            data["results"].append(result_data)
        
        return json.dumps(data, indent=2, ensure_ascii=False)
