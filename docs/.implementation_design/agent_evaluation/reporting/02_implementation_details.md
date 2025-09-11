# Reporting System - Implementation Details

**Document Type**: Implementation Details  
**Author**: Assistant  
**Date Created**: 2025-06-28  
**Last Updated**: 2025-06-28  
**Status**: Draft  
**Stakeholders**: Developers, Technical Architects, QA Team  
**Component**: Reporting System  
**Iteration Count**: 1  

## Overview

This document provides detailed implementation specifications for the Reporting System, including class hierarchies, algorithms, data structures, and performance optimizations.

## Class Hierarchy

### 1. Base Classes

#### ReportGenerator
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class ReportConfig:
    """Configuration for report generation."""
    default_format: str = "html"
    template_directory: str = "templates"
    output_directory: str = "output"
    cache_enabled: bool = True
    cache_ttl: int = 3600
    max_file_size: int = 100 * 1024 * 1024  # 100MB

class ReportGenerator:
    """Core report generation engine."""
    
    def __init__(self, config: Optional[ReportConfig] = None):
        self.config = config or ReportConfig()
        self._template_engine = TemplateEngine(self.config.template_directory)
        self._export_manager = ExportManager()
        self._cache = {} if self.config.cache_enabled else None
    
    def generate_report(
        self, 
        evaluation_results: 'EvaluationResults', 
        report_type: str = "html",
        template: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> 'Report':
        """Generate a report from evaluation results."""
        # Generate cache key
        cache_key = self._generate_cache_key(evaluation_results, report_type, template, options)
        
        # Check cache
        if self._cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        # Process data
        processed_data = self._process_evaluation_data(evaluation_results)
        
        # Select template
        template_name = template or self._get_default_template(report_type)
        
        # Render template
        content = self._template_engine.render_template(
            template_name, 
            processed_data, 
            report_type
        )
        
        # Create report
        report = Report(
            report_id=str(uuid.uuid4()),
            report_type=report_type,
            title=processed_data.get('title', 'Evaluation Report'),
            content=content,
            metadata=processed_data.get('metadata', {}),
            created_at=datetime.now(),
            format=report_type,
            template_used=template_name
        )
        
        # Cache result
        if self._cache:
            self._cache[cache_key] = report
        
        return report
    
    def _process_evaluation_data(self, evaluation_results: 'EvaluationResults') -> Dict[str, Any]:
        """Process evaluation results for template rendering."""
        return {
            'title': f"Evaluation Report - {evaluation_results.agent_name}",
            'agent_name': evaluation_results.agent_name,
            'evaluation_date': evaluation_results.timestamp,
            'metrics': evaluation_results.metrics,
            'summary': evaluation_results.summary,
            'metadata': {
                'total_evaluations': len(evaluation_results.results),
                'evaluation_duration': evaluation_results.duration,
                'benchmark_used': evaluation_results.benchmark_name
            }
        }
    
    def _get_default_template(self, report_type: str) -> str:
        """Get default template for report type."""
        templates = {
            'html': 'standard_report.html',
            'pdf': 'pdf_report.html',
            'json': 'json_report.json',
            'csv': 'csv_report.csv',
            'markdown': 'markdown_report.md'
        }
        return templates.get(report_type, 'standard_report.html')
    
    def _generate_cache_key(
        self, 
        evaluation_results: 'EvaluationResults', 
        report_type: str, 
        template: Optional[str], 
        options: Optional[Dict[str, Any]]
    ) -> str:
        """Generate cache key for report."""
        import hashlib
        import json
        
        data = {
            'agent_name': evaluation_results.agent_name,
            'timestamp': evaluation_results.timestamp.isoformat(),
            'report_type': report_type,
            'template': template,
            'options': options or {}
        }
        
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
```

#### VisualizationEngine
```python
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple, Any

class VisualizationEngine:
    """Data visualization and chart generation engine."""
    
    def __init__(self, config: Optional[VizConfig] = None):
        self.config = config or VizConfig()
        self._chart_generator = ChartGenerator(self.config.default_backend)
        self._setup_matplotlib()
    
    def _setup_matplotlib(self):
        """Setup matplotlib configuration."""
        plt.style.use(self.config.chart_theme)
        if self.config.color_palette:
            plt.rcParams['axes.prop_cycle'] = plt.cycler(color=self.config.color_palette)
    
    def create_chart(
        self, 
        data: 'MetricData', 
        chart_type: str,
        options: Optional[Dict[str, Any]] = None
    ) -> 'Chart':
        """Create a chart from metric data."""
        options = options or {}
        
        if chart_type == "bar":
            return self._create_bar_chart(data, options)
        elif chart_type == "line":
            return self._create_line_chart(data, options)
        elif chart_type == "pie":
            return self._create_pie_chart(data, options)
        elif chart_type == "scatter":
            return self._create_scatter_plot(data, options)
        elif chart_type == "heatmap":
            return self._create_heatmap(data, options)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
    
    def _create_bar_chart(self, data: 'MetricData', options: Dict[str, Any]) -> 'Chart':
        """Create a bar chart."""
        fig, ax = plt.subplots(figsize=self.config.default_size)
        
        # Extract data
        labels = list(data.keys())
        values = list(data.values())
        
        # Create bar chart
        bars = ax.bar(labels, values, color=self.config.color_palette)
        
        # Customize chart
        ax.set_title(options.get('title', 'Metrics Comparison'))
        ax.set_xlabel(options.get('xlabel', 'Metrics'))
        ax.set_ylabel(options.get('ylabel', 'Values'))
        
        # Add value labels on bars
        if options.get('show_values', True):
            for bar, value in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{value:.2f}', ha='center', va='bottom')
        
        # Rotate x-axis labels if needed
        if options.get('rotate_labels', False):
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        return Chart(
            chart_id=str(uuid.uuid4()),
            chart_type="bar",
            title=options.get('title', 'Bar Chart'),
            data=data,
            options=options,
            created_at=datetime.now()
        )
    
    def _create_line_chart(self, data: 'MetricData', options: Dict[str, Any]) -> 'Chart':
        """Create a line chart."""
        fig, ax = plt.subplots(figsize=self.config.default_size)
        
        # Extract data
        x_data = data.get('x', list(range(len(data.get('y', [])))))
        y_data = data.get('y', [])
        
        # Create line chart
        ax.plot(x_data, y_data, marker='o', linewidth=2, markersize=6)
        
        # Customize chart
        ax.set_title(options.get('title', 'Trend Analysis'))
        ax.set_xlabel(options.get('xlabel', 'Time'))
        ax.set_ylabel(options.get('ylabel', 'Value'))
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        return Chart(
            chart_id=str(uuid.uuid4()),
            chart_type="line",
            title=options.get('title', 'Line Chart'),
            data=data,
            options=options,
            created_at=datetime.now()
        )
    
    def build_dashboard(
        self, 
        evaluation_results: 'EvaluationResults',
        layout: Optional[str] = None
    ) -> 'Dashboard':
        """Build an interactive dashboard."""
        layout = layout or "grid"
        
        # Create dashboard
        dashboard = Dashboard(
            dashboard_id=str(uuid.uuid4()),
            title=f"Dashboard - {evaluation_results.agent_name}",
            layout=layout,
            widgets=[],
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        # Add metrics display widget
        metrics_widget = self.create_metrics_display(
            evaluation_results.summary_metrics,
            display_type="cards"
        )
        dashboard.widgets.append(metrics_widget)
        
        # Add performance chart
        if evaluation_results.performance_data:
            performance_chart = self.create_chart(
                evaluation_results.performance_data,
                chart_type="line",
                options={"title": "Performance Over Time"}
            )
            chart_widget = Widget(
                widget_id=str(uuid.uuid4()),
                widget_type="chart",
                title="Performance Chart",
                data=performance_chart.data,
                position=(0, 1),
                size=(400, 300),
                options={}
            )
            dashboard.widgets.append(chart_widget)
        
        return dashboard
```

#### ExportManager
```python
import os
import json
import csv
from pathlib import Path
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

class ExportManager:
    """Multi-format export functionality."""
    
    def __init__(self):
        self._exporters = {
            'html': self._export_to_html,
            'pdf': self._export_to_pdf,
            'json': self._export_to_json,
            'csv': self._export_to_csv,
            'markdown': self._export_to_markdown
        }
    
    def export_to_html(
        self, 
        report: 'Report', 
        output_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Export report to HTML format."""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write HTML content
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report.content)
            
            return True
        except Exception as e:
            print(f"Error exporting to HTML: {e}")
            return False
    
    def export_to_pdf(
        self, 
        report: 'Report', 
        output_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Export report to PDF format."""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Configure font
            font_config = FontConfiguration()
            
            # Create HTML document
            html_doc = HTML(string=report.content)
            
            # Generate PDF
            html_doc.write_pdf(
                output_path,
                font_config=font_config,
                stylesheets=[CSS(string=self._get_pdf_styles())]
            )
            
            return True
        except Exception as e:
            print(f"Error exporting to PDF: {e}")
            return False
    
    def export_to_json(
        self, 
        report: 'Report', 
        output_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Export report to JSON format."""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Create JSON data
            json_data = {
                'report_id': report.report_id,
                'report_type': report.report_type,
                'title': report.title,
                'content': report.content,
                'metadata': report.metadata,
                'created_at': report.created_at.isoformat(),
                'format': report.format
            }
            
            # Write JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    def export_to_csv(
        self, 
        report: 'Report', 
        output_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Export report to CSV format."""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Extract metrics data from report metadata
            metrics_data = report.metadata.get('metrics', {})
            
            # Write CSV file
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow(['Metric', 'Value'])
                
                # Write data
                for metric, value in metrics_data.items():
                    writer.writerow([metric, value])
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def export_to_markdown(
        self, 
        report: 'Report', 
        output_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Export report to Markdown format."""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Generate Markdown content
            markdown_content = self._generate_markdown_content(report)
            
            # Write Markdown file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            return True
        except Exception as e:
            print(f"Error exporting to Markdown: {e}")
            return False
    
    def _get_pdf_styles(self) -> str:
        """Get CSS styles for PDF export."""
        return """
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }
        h1, h2, h3 {
            color: #333;
        }
        .metrics-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .metrics-table th, .metrics-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .metrics-table th {
            background-color: #f2f2f2;
        }
        """
    
    def _generate_markdown_content(self, report: 'Report') -> str:
        """Generate Markdown content from report."""
        content = f"# {report.title}\n\n"
        content += f"**Generated:** {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Add metrics table
        metrics = report.metadata.get('metrics', {})
        if metrics:
            content += "## Metrics\n\n"
            content += "| Metric | Value |\n"
            content += "|--------|-------|\n"
            for metric, value in metrics.items():
                content += f"| {metric} | {value} |\n"
            content += "\n"
        
        # Add summary
        summary = report.metadata.get('summary', '')
        if summary:
            content += "## Summary\n\n"
            content += f"{summary}\n\n"
        
        return content
```

### 2. Template Engine Implementation

#### TemplateEngine
```python
from jinja2 import Environment, FileSystemLoader, Template
from typing import Dict, Any, Optional
import os

class TemplateEngine:
    """Template processing and management."""
    
    def __init__(self, template_dir: Optional[str] = None):
        self.template_dir = template_dir or "templates"
        self._setup_jinja2()
        self._custom_templates = {}
    
    def _setup_jinja2(self):
        """Setup Jinja2 environment."""
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=True
        )
        
        # Add custom filters
        self.jinja_env.filters['format_number'] = self._format_number
        self.jinja_env.filters['format_percentage'] = self._format_percentage
        self.jinja_env.filters['format_date'] = self._format_date
    
    def render_template(
        self, 
        template_name: str, 
        data: Dict[str, Any],
        format_type: str = "html"
    ) -> str:
        """Render a template with data."""
        try:
            # Get template
            if template_name in self._custom_templates:
                template = Template(self._custom_templates[template_name])
            else:
                template = self.jinja_env.get_template(template_name)
            
            # Render template
            return template.render(**data)
        except Exception as e:
            raise TemplateError(f"Error rendering template {template_name}: {e}")
    
    def register_template(
        self, 
        name: str, 
        template_content: str,
        template_type: str = "html"
    ) -> bool:
        """Register a custom template."""
        try:
            # Validate template
            validation_result = self.validate_template(template_content, template_type)
            if not validation_result.is_valid:
                return False
            
            # Store template
            self._custom_templates[name] = template_content
            return True
        except Exception as e:
            print(f"Error registering template: {e}")
            return False
    
    def validate_template(
        self, 
        template_content: str, 
        template_type: str = "html"
    ) -> 'ValidationResult':
        """Validate template syntax."""
        try:
            # Create template object
            template = Template(template_content)
            
            # Test render with dummy data
            dummy_data = {
                'title': 'Test Title',
                'metrics': {'test': 0.5},
                'summary': 'Test summary'
            }
            template.render(**dummy_data)
            
            return ValidationResult(is_valid=True, errors=[])
        except Exception as e:
            return ValidationResult(is_valid=False, errors=[str(e)])
    
    def _format_number(self, value: float, precision: int = 2) -> str:
        """Format number with specified precision."""
        return f"{value:.{precision}f}"
    
    def _format_percentage(self, value: float, precision: int = 1) -> str:
        """Format percentage with specified precision."""
        return f"{value * 100:.{precision}f}%"
    
    def _format_date(self, date: datetime, format_str: str = "%Y-%m-%d") -> str:
        """Format date with specified format."""
        return date.strftime(format_str)
```

### 3. Analytics Engine Implementation

#### AnalyticsEngine
```python
import statistics
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta

class AnalyticsEngine:
    """Advanced analytics and insights generation."""
    
    def __init__(self):
        self._trend_analyzer = TrendAnalyzer()
        self._recommendation_engine = RecommendationEngine()
        self._anomaly_detector = AnomalyDetector()
    
    def generate_summary(
        self, 
        evaluation_results: 'EvaluationResults',
        summary_level: str = "detailed"
    ) -> 'SummaryAnalytics':
        """Generate summary analytics."""
        # Calculate basic metrics
        total_evaluations = len(evaluation_results.results)
        metrics = evaluation_results.summary_metrics
        
        # Calculate averages
        avg_scores = {}
        for metric_name, values in metrics.items():
            if isinstance(values, list):
                avg_scores[metric_name] = statistics.mean(values)
            else:
                avg_scores[metric_name] = values
        
        # Find best and worst performing agents
        best_agent = self._find_best_agent(evaluation_results)
        worst_agent = self._find_worst_agent(evaluation_results)
        
        # Generate trends
        trends = self._generate_trends(evaluation_results)
        
        # Generate recommendations
        recommendations = self._recommendation_engine.generate_recommendations(
            evaluation_results, summary_level
        )
        
        return SummaryAnalytics(
            total_evaluations=total_evaluations,
            average_score=statistics.mean(avg_scores.values()) if avg_scores else 0.0,
            best_performing_agent=best_agent,
            worst_performing_agent=worst_agent,
            key_metrics=avg_scores,
            trends=trends,
            recommendations=recommendations,
            generated_at=datetime.now()
        )
    
    def analyze_trends(
        self, 
        historical_results: List['EvaluationResults'],
        trend_period: str = "monthly"
    ) -> 'TrendAnalysis':
        """Analyze performance trends over time."""
        return self._trend_analyzer.analyze_trends(historical_results, trend_period)
    
    def generate_recommendations(
        self, 
        evaluation_results: 'EvaluationResults',
        recommendation_type: str = "improvement"
    ) -> List['Recommendation']:
        """Generate actionable recommendations."""
        return self._recommendation_engine.generate_recommendations(
            evaluation_results, recommendation_type
        )
    
    def detect_anomalies(
        self, 
        evaluation_results: 'EvaluationResults',
        sensitivity: float = 0.1
    ) -> List['Anomaly']:
        """Detect anomalies in evaluation results."""
        return self._anomaly_detector.detect_anomalies(
            evaluation_results, sensitivity
        )
    
    def _find_best_agent(self, evaluation_results: 'EvaluationResults') -> str:
        """Find best performing agent."""
        # This would be implemented based on specific criteria
        return evaluation_results.agent_name
    
    def _find_worst_agent(self, evaluation_results: 'EvaluationResults') -> str:
        """Find worst performing agent."""
        # This would be implemented based on specific criteria
        return evaluation_results.agent_name
    
    def _generate_trends(self, evaluation_results: 'EvaluationResults') -> List['Trend']:
        """Generate trend data."""
        # This would analyze trends in the evaluation results
        return []
```

## Performance Optimizations

### 1. Caching Implementation

```python
import time
from typing import Any, Optional
from collections import OrderedDict

class ReportCache:
    """Caching system for generated reports."""
    
    def __init__(self, max_size: int = 100, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self._cache = OrderedDict()
        self._timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._cache:
            return None
        
        # Check TTL
        if self._is_expired(key):
            self._remove(key)
            return None
        
        # Move to end (LRU)
        value = self._cache.pop(key)
        self._cache[key] = value
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        # Remove oldest if cache is full
        if len(self._cache) >= self.max_size:
            self._evict_oldest()
        
        self._cache[key] = value
        self._timestamps[key] = time.time()
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired."""
        if key not in self._timestamps:
            return True
        
        age = time.time() - self._timestamps[key]
        return age > self.ttl
    
    def _evict_oldest(self) -> None:
        """Evict oldest cache entry."""
        if self._cache:
            oldest_key = next(iter(self._cache))
            self._remove(oldest_key)
    
    def _remove(self, key: str) -> None:
        """Remove entry from cache."""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
```

### 2. Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable, Any

class ParallelProcessor:
    """Parallel processing utilities for report generation."""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
    
    def process_reports_parallel(
        self, 
        report_tasks: List[Callable], 
        timeout: int = 300
    ) -> List[Any]:
        """Process multiple report generation tasks in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(task): i for i, task in enumerate(report_tasks)
            }
            
            # Collect results
            for future in as_completed(future_to_task, timeout=timeout):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Task failed: {e}")
                    results.append(None)
        
        return results
```

## Error Handling Implementation

### 1. Exception Classes

```python
class ReportingError(Exception):
    """Base exception for reporting system errors."""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "REPORTING_ERROR"
        self.details = details or {}
        self.timestamp = datetime.now()

class ReportGenerationError(ReportingError):
    """Error during report generation."""
    def __init__(self, message: str, report_type: str = None, details: dict = None):
        super().__init__(message, "REPORT_GENERATION_ERROR", details)
        self.report_type = report_type

class TemplateError(ReportingError):
    """Error in template processing."""
    def __init__(self, message: str, template_name: str = None, details: dict = None):
        super().__init__(message, "TEMPLATE_ERROR", details)
        self.template_name = template_name

class ExportError(ReportingError):
    """Error during export operation."""
    def __init__(self, message: str, export_format: str = None, details: dict = None):
        super().__init__(message, "EXPORT_ERROR", details)
        self.export_format = export_format
```

### 2. Error Recovery

```python
class ErrorRecovery:
    """Error recovery mechanisms for report generation."""
    
    def __init__(self):
        self.retry_attempts = 3
        self.retry_delay = 1.0
    
    def generate_report_with_retry(
        self, 
        generator: ReportGenerator,
        evaluation_results: 'EvaluationResults',
        report_type: str = "html"
    ) -> 'Report':
        """Generate report with retry on failure."""
        last_exception = None
        
        for attempt in range(self.retry_attempts):
            try:
                return generator.generate_report(evaluation_results, report_type)
            except Exception as e:
                last_exception = e
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                else:
                    break
        
        # All retries failed
        raise ReportGenerationError(
            f"Report generation failed after {self.retry_attempts} attempts",
            report_type=report_type,
            details={"last_exception": str(last_exception)}
        )
```

---

**Note**: This implementation provides a comprehensive foundation for the reporting system while maintaining simplicity and performance. The design follows KISS and YAGNI principles to ensure maintainability and avoid over-engineering.
