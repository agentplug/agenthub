# Reporting System - Testing Strategy

**Document Type**: Testing Strategy  
**Author**: Assistant  
**Date Created**: 2025-06-28  
**Last Updated**: 2025-06-28  
**Status**: Draft  
**Stakeholders**: Developers, QA Team, Test Engineers  
**Component**: Reporting System  
**Iteration Count**: 1  

## Overview

This document outlines the comprehensive testing strategy for the Reporting System, covering unit testing, integration testing, visual testing, and performance testing to ensure reliability, accuracy, and performance.

## Testing Objectives

### 1. Primary Objectives
- **Report Accuracy**: Ensure generated reports are accurate and complete
- **Visual Quality**: Verify charts and visualizations are correct and appealing
- **Performance**: Meet response time and throughput requirements
- **Export Functionality**: Ensure all export formats work correctly
- **User Experience**: Verify intuitive and responsive interface

### 2. Success Criteria
- **Test Coverage**: >90% code coverage
- **Performance**: <5s average report generation time
- **Visual Accuracy**: 100% chart accuracy for test cases
- **Export Success**: 99.9% successful export rate
- **User Satisfaction**: >4.0/5.0 usability score

## Testing Levels

### 1. Unit Testing

#### Scope
- Individual report generation functions
- Chart creation and rendering
- Template processing
- Export functionality
- Data validation and processing

#### Test Categories

##### Report Generation Tests
```python
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from reporting.core import ReportGenerator, ReportConfig

class TestReportGenerator:
    """Test report generation functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.config = ReportConfig()
        self.generator = ReportGenerator(self.config)
        self.evaluation_results = Mock()
        self.evaluation_results.agent_name = "Test Agent"
        self.evaluation_results.timestamp = datetime.now()
        self.evaluation_results.metrics = {"accuracy": 0.95, "speed": 0.87}
        self.evaluation_results.summary = "Test summary"
        self.evaluation_results.results = [Mock(), Mock()]
        self.evaluation_results.duration = 120.5
        self.evaluation_results.benchmark_name = "Test Benchmark"
    
    def test_generate_html_report(self):
        """Test HTML report generation."""
        report = self.generator.generate_report(
            self.evaluation_results, 
            report_type="html"
        )
        
        assert report.report_type == "html"
        assert report.title == "Evaluation Report - Test Agent"
        assert "Test Agent" in report.content
        assert "accuracy" in report.content
        assert report.template_used is not None
    
    def test_generate_pdf_report(self):
        """Test PDF report generation."""
        report = self.generator.generate_report(
            self.evaluation_results, 
            report_type="pdf"
        )
        
        assert report.report_type == "pdf"
        assert report.format == "pdf"
        assert report.content is not None
    
    def test_generate_json_report(self):
        """Test JSON report generation."""
        report = self.generator.generate_report(
            self.evaluation_results, 
            report_type="json"
        )
        
        assert report.report_type == "json"
        assert report.format == "json"
        assert "Test Agent" in report.content
    
    def test_custom_template(self):
        """Test custom template usage."""
        custom_template = "Custom Report: {{ title }}"
        
        report = self.generator.generate_report(
            self.evaluation_results,
            report_type="html",
            template=custom_template
        )
        
        assert "Custom Report" in report.content
        assert report.template_used == custom_template
    
    def test_report_caching(self):
        """Test report caching functionality."""
        # Generate report first time
        report1 = self.generator.generate_report(
            self.evaluation_results, 
            report_type="html"
        )
        
        # Generate same report second time (should use cache)
        report2 = self.generator.generate_report(
            self.evaluation_results, 
            report_type="html"
        )
        
        # Should be same report (cached)
        assert report1.report_id == report2.report_id
        assert report1.content == report2.content
    
    def test_invalid_report_type(self):
        """Test handling of invalid report type."""
        with pytest.raises(ValueError):
            self.generator.generate_report(
                self.evaluation_results, 
                report_type="invalid_type"
            )
    
    def test_empty_evaluation_results(self):
        """Test handling of empty evaluation results."""
        empty_results = Mock()
        empty_results.agent_name = ""
        empty_results.timestamp = datetime.now()
        empty_results.metrics = {}
        empty_results.summary = ""
        empty_results.results = []
        empty_results.duration = 0
        empty_results.benchmark_name = ""
        
        report = self.generator.generate_report(empty_results, "html")
        
        assert report.title == "Evaluation Report - "
        assert report.content is not None
```

##### Chart Generation Tests
```python
class TestVisualizationEngine:
    """Test visualization engine functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.viz_engine = VisualizationEngine()
        self.metric_data = {
            "accuracy": 0.95,
            "speed": 0.87,
            "reliability": 0.92
        }
    
    def test_create_bar_chart(self):
        """Test bar chart creation."""
        chart = self.viz_engine.create_chart(
            self.metric_data, 
            chart_type="bar",
            options={"title": "Test Bar Chart"}
        )
        
        assert chart.chart_type == "bar"
        assert chart.title == "Test Bar Chart"
        assert chart.data == self.metric_data
        assert chart.width == 800
        assert chart.height == 600
    
    def test_create_line_chart(self):
        """Test line chart creation."""
        line_data = {
            "x": [1, 2, 3, 4, 5],
            "y": [0.8, 0.85, 0.9, 0.88, 0.92]
        }
        
        chart = self.viz_engine.create_chart(
            line_data, 
            chart_type="line",
            options={"title": "Test Line Chart"}
        )
        
        assert chart.chart_type == "line"
        assert chart.title == "Test Line Chart"
        assert chart.data == line_data
    
    def test_create_pie_chart(self):
        """Test pie chart creation."""
        chart = self.viz_engine.create_chart(
            self.metric_data, 
            chart_type="pie",
            options={"title": "Test Pie Chart"}
        )
        
        assert chart.chart_type == "pie"
        assert chart.title == "Test Pie Chart"
        assert chart.data == self.metric_data
    
    def test_create_heatmap(self):
        """Test heatmap creation."""
        heatmap_data = [
            [0.8, 0.9, 0.7],
            [0.85, 0.95, 0.8],
            [0.9, 0.88, 0.92]
        ]
        labels = ["Agent A", "Agent B", "Agent C"]
        
        chart = self.viz_engine.create_chart(
            {"data": heatmap_data, "labels": labels}, 
            chart_type="heatmap",
            options={"title": "Test Heatmap"}
        )
        
        assert chart.chart_type == "heatmap"
        assert chart.title == "Test Heatmap"
    
    def test_invalid_chart_type(self):
        """Test handling of invalid chart type."""
        with pytest.raises(ValueError):
            self.viz_engine.create_chart(
                self.metric_data, 
                chart_type="invalid_type"
            )
    
    def test_dashboard_creation(self):
        """Test dashboard creation."""
        evaluation_results = Mock()
        evaluation_results.agent_name = "Test Agent"
        evaluation_results.summary_metrics = self.metric_data
        evaluation_results.performance_data = {
            "x": [1, 2, 3],
            "y": [0.8, 0.85, 0.9]
        }
        
        dashboard = self.viz_engine.build_dashboard(
            evaluation_results, 
            layout="grid"
        )
        
        assert dashboard.title == "Dashboard - Test Agent"
        assert dashboard.layout == "grid"
        assert len(dashboard.widgets) > 0
        assert dashboard.is_interactive == True
```

##### Export Functionality Tests
```python
class TestExportManager:
    """Test export functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.export_manager = ExportManager()
        self.report = Mock()
        self.report.content = "<html><body>Test Report</body></html>"
        self.report.metadata = {
            "metrics": {"accuracy": 0.95, "speed": 0.87}
        }
        self.report.title = "Test Report"
        self.report.created_at = datetime.now()
        self.report.format = "html"
    
    def test_export_to_html(self):
        """Test HTML export."""
        output_path = "test_output.html"
        
        result = self.export_manager.export_to_html(
            self.report, 
            output_path
        )
        
        assert result == True
        assert os.path.exists(output_path)
        
        # Cleanup
        os.remove(output_path)
    
    def test_export_to_pdf(self):
        """Test PDF export."""
        output_path = "test_output.pdf"
        
        result = self.export_manager.export_to_pdf(
            self.report, 
            output_path
        )
        
        assert result == True
        assert os.path.exists(output_path)
        
        # Cleanup
        os.remove(output_path)
    
    def test_export_to_json(self):
        """Test JSON export."""
        output_path = "test_output.json"
        
        result = self.export_manager.export_to_json(
            self.report, 
            output_path
        )
        
        assert result == True
        assert os.path.exists(output_path)
        
        # Verify JSON content
        with open(output_path, 'r') as f:
            data = json.load(f)
            assert data['title'] == "Test Report"
            assert data['format'] == "html"
        
        # Cleanup
        os.remove(output_path)
    
    def test_export_to_csv(self):
        """Test CSV export."""
        output_path = "test_output.csv"
        
        result = self.export_manager.export_to_csv(
            self.report, 
            output_path
        )
        
        assert result == True
        assert os.path.exists(output_path)
        
        # Verify CSV content
        with open(output_path, 'r') as f:
            content = f.read()
            assert "Metric,Value" in content
            assert "accuracy,0.95" in content
        
        # Cleanup
        os.remove(output_path)
    
    def test_export_to_markdown(self):
        """Test Markdown export."""
        output_path = "test_output.md"
        
        result = self.export_manager.export_to_markdown(
            self.report, 
            output_path
        )
        
        assert result == True
        assert os.path.exists(output_path)
        
        # Verify Markdown content
        with open(output_path, 'r') as f:
            content = f.read()
            assert "# Test Report" in content
            assert "## Metrics" in content
        
        # Cleanup
        os.remove(output_path)
    
    def test_export_error_handling(self):
        """Test export error handling."""
        # Test with invalid output path
        result = self.export_manager.export_to_html(
            self.report, 
            "/invalid/path/report.html"
        )
        
        assert result == False
```

### 2. Integration Testing

#### Scope
- End-to-end report generation workflows
- Integration with evaluation engine
- Integration with metrics engine
- Multi-format export workflows
- Dashboard functionality

#### Test Categories

##### End-to-End Report Generation
```python
class TestReportGenerationIntegration:
    """Test end-to-end report generation."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.generator = ReportGenerator()
        self.export_manager = ExportManager()
        self.evaluation_results = create_sample_evaluation_results()
    
    def test_complete_html_report_workflow(self):
        """Test complete HTML report workflow."""
        # Generate report
        report = self.generator.generate_report(
            self.evaluation_results, 
            report_type="html"
        )
        
        # Export to file
        output_path = "integration_test.html"
        success = self.export_manager.export_to_html(report, output_path)
        
        assert success == True
        assert os.path.exists(output_path)
        
        # Verify content
        with open(output_path, 'r') as f:
            content = f.read()
            assert self.evaluation_results.agent_name in content
            assert "accuracy" in content.lower()
        
        # Cleanup
        os.remove(output_path)
    
    def test_multi_format_export_workflow(self):
        """Test multi-format export workflow."""
        formats = ["html", "pdf", "json", "csv", "markdown"]
        output_files = []
        
        for format_type in formats:
            # Generate report
            report = self.generator.generate_report(
                self.evaluation_results, 
                report_type=format_type
            )
            
            # Export to file
            output_path = f"integration_test.{format_type}"
            success = getattr(self.export_manager, f"export_to_{format_type}")(
                report, output_path
            )
            
            assert success == True
            assert os.path.exists(output_path)
            output_files.append(output_path)
        
        # Cleanup
        for file_path in output_files:
            os.remove(file_path)
    
    def test_dashboard_integration(self):
        """Test dashboard integration."""
        viz_engine = VisualizationEngine()
        
        # Create dashboard
        dashboard = viz_engine.build_dashboard(
            self.evaluation_results,
            layout="grid"
        )
        
        # Verify dashboard structure
        assert dashboard.title is not None
        assert len(dashboard.widgets) > 0
        assert dashboard.is_interactive == True
        
        # Test widget functionality
        for widget in dashboard.widgets:
            assert widget.widget_id is not None
            assert widget.title is not None
            assert widget.data is not None
```

### 3. Visual Testing

#### Scope
- Chart accuracy and appearance
- Layout and formatting correctness
- Responsive design validation
- Cross-browser compatibility
- Print layout verification

#### Test Categories

##### Chart Visual Testing
```python
class TestVisualAccuracy:
    """Test visual accuracy of charts and reports."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.viz_engine = VisualizationEngine()
        self.test_data = {
            "accuracy": 0.95,
            "speed": 0.87,
            "reliability": 0.92
        }
    
    def test_bar_chart_visual_accuracy(self):
        """Test bar chart visual accuracy."""
        chart = self.viz_engine.create_chart(
            self.test_data, 
            chart_type="bar",
            options={"title": "Test Bar Chart"}
        )
        
        # Verify chart properties
        assert chart.width == 800
        assert chart.height == 600
        assert chart.title == "Test Bar Chart"
        
        # Test chart rendering
        base64_image = self.viz_engine.get_chart_as_base64(chart, "png")
        assert base64_image is not None
        assert len(base64_image) > 0
    
    def test_line_chart_visual_accuracy(self):
        """Test line chart visual accuracy."""
        line_data = {
            "x": [1, 2, 3, 4, 5],
            "y": [0.8, 0.85, 0.9, 0.88, 0.92]
        }
        
        chart = self.viz_engine.create_chart(
            line_data, 
            chart_type="line",
            options={"title": "Performance Trend"}
        )
        
        # Verify chart properties
        assert chart.chart_type == "line"
        assert chart.data == line_data
        
        # Test chart rendering
        base64_image = self.viz_engine.get_chart_as_base64(chart, "png")
        assert base64_image is not None
    
    def test_pie_chart_visual_accuracy(self):
        """Test pie chart visual accuracy."""
        chart = self.viz_engine.create_chart(
            self.test_data, 
            chart_type="pie",
            options={"title": "Metrics Distribution"}
        )
        
        # Verify chart properties
        assert chart.chart_type == "pie"
        assert chart.data == self.test_data
        
        # Test chart rendering
        base64_image = self.viz_engine.get_chart_as_base64(chart, "png")
        assert base64_image is not None
    
    def test_heatmap_visual_accuracy(self):
        """Test heatmap visual accuracy."""
        heatmap_data = [
            [0.8, 0.9, 0.7],
            [0.85, 0.95, 0.8],
            [0.9, 0.88, 0.92]
        ]
        labels = ["Agent A", "Agent B", "Agent C"]
        
        chart = self.viz_engine.create_chart(
            {"data": heatmap_data, "labels": labels}, 
            chart_type="heatmap",
            options={"title": "Agent Performance Heatmap"}
        )
        
        # Verify chart properties
        assert chart.chart_type == "heatmap"
        assert chart.data["data"] == heatmap_data
        assert chart.data["labels"] == labels
        
        # Test chart rendering
        base64_image = self.viz_engine.get_chart_as_base64(chart, "png")
        assert base64_image is not None
```

##### Report Layout Testing
```python
class TestReportLayout:
    """Test report layout and formatting."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.generator = ReportGenerator()
        self.evaluation_results = create_sample_evaluation_results()
    
    def test_html_report_layout(self):
        """Test HTML report layout."""
        report = self.generator.generate_report(
            self.evaluation_results, 
            report_type="html"
        )
        
        # Verify HTML structure
        assert "<html>" in report.content
        assert "<head>" in report.content
        assert "<body>" in report.content
        assert "<title>" in report.content
        
        # Verify content structure
        assert "Evaluation Report" in report.content
        assert "Metrics" in report.content
        assert "Summary" in report.content
    
    def test_pdf_report_layout(self):
        """Test PDF report layout."""
        report = self.generator.generate_report(
            self.evaluation_results, 
            report_type="pdf"
        )
        
        # Verify PDF-specific content
        assert report.format == "pdf"
        assert report.content is not None
        
        # Test PDF export
        output_path = "layout_test.pdf"
        success = ExportManager().export_to_pdf(report, output_path)
        
        assert success == True
        assert os.path.exists(output_path)
        
        # Cleanup
        os.remove(output_path)
    
    def test_responsive_design(self):
        """Test responsive design elements."""
        report = self.generator.generate_report(
            self.evaluation_results, 
            report_type="html"
        )
        
        # Check for responsive design elements
        assert "viewport" in report.content
        assert "responsive" in report.content.lower() or "mobile" in report.content.lower()
```

### 4. Performance Testing

#### Scope
- Report generation performance
- Chart rendering performance
- Export operation performance
- Memory usage optimization
- Concurrent request handling

#### Test Categories

##### Load Testing
```python
import time
import threading
from concurrent.futures import ThreadPoolExecutor

class TestPerformanceLoad:
    """Test performance under load."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.generator = ReportGenerator()
        self.export_manager = ExportManager()
        self.evaluation_results = create_sample_evaluation_results()
    
    def test_report_generation_performance(self):
        """Test report generation performance."""
        start_time = time.time()
        
        # Generate multiple reports
        reports = []
        for i in range(10):
            report = self.generator.generate_report(
                self.evaluation_results, 
                report_type="html"
            )
            reports.append(report)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_report = total_time / len(reports)
        
        # Should be under 5 seconds per report
        assert avg_time_per_report < 5.0
        assert len(reports) == 10
    
    def test_concurrent_report_generation(self):
        """Test concurrent report generation."""
        def generate_report():
            return self.generator.generate_report(
                self.evaluation_results, 
                report_type="html"
            )
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(generate_report) for _ in range(20)]
            reports = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete within reasonable time
        assert total_time < 30.0  # 30 seconds for 20 reports
        assert len(reports) == 20
        assert all(report is not None for report in reports)
    
    def test_export_performance(self):
        """Test export performance."""
        report = self.generator.generate_report(
            self.evaluation_results, 
            report_type="html"
        )
        
        formats = ["html", "pdf", "json", "csv", "markdown"]
        export_times = {}
        
        for format_type in formats:
            start_time = time.time()
            
            output_path = f"perf_test.{format_type}"
            success = getattr(self.export_manager, f"export_to_{format_type}")(
                report, output_path
            )
            
            end_time = time.time()
            export_time = end_time - start_time
            
            assert success == True
            export_times[format_type] = export_time
            
            # Cleanup
            if os.path.exists(output_path):
                os.remove(output_path)
        
        # PDF export should be the slowest, but under 10 seconds
        assert export_times["pdf"] < 10.0
        # Other formats should be faster
        assert export_times["html"] < 1.0
        assert export_times["json"] < 1.0
        assert export_times["csv"] < 1.0
        assert export_times["markdown"] < 1.0
    
    def test_memory_usage(self):
        """Test memory usage during report generation."""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate multiple reports
        reports = []
        for i in range(50):
            report = self.generator.generate_report(
                self.evaluation_results, 
                report_type="html"
            )
            reports.append(report)
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Cleanup
        del reports
        gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        # Should not use more than 500MB additional memory
        assert memory_increase < 500
        assert peak_memory < 2000  # Less than 2GB peak
```

##### Stress Testing
```python
class TestPerformanceStress:
    """Test performance under stress conditions."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.generator = ReportGenerator()
        self.evaluation_results = create_large_evaluation_results()
    
    def test_large_dataset_processing(self):
        """Test processing of large datasets."""
        # Create large evaluation results
        large_results = create_large_evaluation_results(1000)  # 1000 evaluations
        
        start_time = time.time()
        report = self.generator.generate_report(
            large_results, 
            report_type="html"
        )
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # Should handle large datasets efficiently
        assert total_time < 30.0  # Under 30 seconds
        assert report is not None
        assert len(report.content) > 0
    
    def test_memory_cleanup_under_stress(self):
        """Test memory cleanup under stress conditions."""
        import gc
        import psutil
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        # Process multiple large reports
        for i in range(10):
            large_results = create_large_evaluation_results(100)
            report = self.generator.generate_report(
                large_results, 
                report_type="html"
            )
            
            # Force cleanup
            del report
            del large_results
            gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        # Memory should not grow significantly
        assert memory_increase < 100  # Less than 100MB increase
```

## Test Data Management

### 1. Test Data Generation

```python
class TestDataGenerator:
    """Generate test data for reporting tests."""
    
    @staticmethod
    def create_sample_evaluation_results() -> 'EvaluationResults':
        """Create sample evaluation results for testing."""
        return Mock(
            agent_name="Test Agent",
            timestamp=datetime.now(),
            metrics={"accuracy": 0.95, "speed": 0.87, "reliability": 0.92},
            summary="Test agent performed well across all metrics.",
            results=[Mock() for _ in range(10)],
            duration=120.5,
            benchmark_name="Test Benchmark",
            summary_metrics={"accuracy": 0.95, "speed": 0.87, "reliability": 0.92},
            performance_data={"x": [1, 2, 3, 4, 5], "y": [0.8, 0.85, 0.9, 0.88, 0.92]}
        )
    
    @staticmethod
    def create_large_evaluation_results(size: int = 100) -> 'EvaluationResults':
        """Create large evaluation results for stress testing."""
        return Mock(
            agent_name="Large Test Agent",
            timestamp=datetime.now(),
            metrics={"accuracy": 0.95, "speed": 0.87, "reliability": 0.92},
            summary="Large test agent performance data.",
            results=[Mock() for _ in range(size)],
            duration=600.0,
            benchmark_name="Large Test Benchmark",
            summary_metrics={"accuracy": 0.95, "speed": 0.87, "reliability": 0.92},
            performance_data={"x": list(range(size)), "y": [0.8 + i * 0.001 for i in range(size)]}
        )
    
    @staticmethod
    def create_chart_test_data() -> Dict[str, Any]:
        """Create test data for chart generation."""
        return {
            "accuracy": 0.95,
            "speed": 0.87,
            "reliability": 0.92,
            "efficiency": 0.89,
            "usability": 0.91
        }
```

### 2. Test Fixtures

```python
@pytest.fixture
def sample_evaluation_results():
    """Fixture for sample evaluation results."""
    return TestDataGenerator.create_sample_evaluation_results()

@pytest.fixture
def report_generator():
    """Fixture for report generator."""
    return ReportGenerator()

@pytest.fixture
def visualization_engine():
    """Fixture for visualization engine."""
    return VisualizationEngine()

@pytest.fixture
def export_manager():
    """Fixture for export manager."""
    return ExportManager()

@pytest.fixture
def chart_test_data():
    """Fixture for chart test data."""
    return TestDataGenerator.create_chart_test_data()
```

## Test Execution Strategy

### 1. Test Phases

#### Phase 1: Unit Tests
- **Duration**: 3-4 days
- **Scope**: Individual report generation functions
- **Coverage**: >90% code coverage
- **Tools**: pytest, coverage.py

#### Phase 2: Integration Tests
- **Duration**: 2-3 days
- **Scope**: End-to-end workflows
- **Coverage**: All integration points
- **Tools**: pytest, testcontainers

#### Phase 3: Visual Tests
- **Duration**: 2-3 days
- **Scope**: Chart and layout accuracy
- **Coverage**: All visualization types
- **Tools**: Custom visual testing tools

#### Phase 4: Performance Tests
- **Duration**: 2-3 days
- **Scope**: Load and stress testing
- **Coverage**: Performance requirements
- **Tools**: locust, pytest-benchmark

### 2. Continuous Integration

```yaml
# .github/workflows/reporting-testing.yml
name: Reporting System Testing

on:
  push:
    branches: [main, develop]
    paths: ['agentmanager/evaluation/reporting/**']
  pull_request:
    branches: [main]
    paths: ['agentmanager/evaluation/reporting/**']

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov matplotlib plotly weasyprint
      - name: Run unit tests
        run: |
          pytest tests/reporting/unit/ -v --cov=agentmanager.evaluation.reporting --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  visual-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest matplotlib plotly
      - name: Run visual tests
        run: |
          pytest tests/reporting/visual/ -v
      - name: Upload test artifacts
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: visual-test-results
          path: test_outputs/

  performance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest-benchmark locust
      - name: Run performance tests
        run: |
          pytest tests/reporting/performance/ -v --benchmark-only
```

## Quality Gates

### 1. Coverage Requirements
- **Unit Tests**: >90% code coverage
- **Integration Tests**: >80% integration coverage
- **Visual Tests**: 100% chart type coverage
- **Performance Tests**: All performance requirements met

### 2. Performance Requirements
- **Report Generation**: <5s average per report
- **Chart Creation**: <2s average per chart
- **Export Operations**: <10s average for PDF
- **Memory Usage**: <2GB peak usage

### 3. Quality Requirements
- **Code Quality**: All linting rules passed
- **Documentation**: All public APIs documented
- **Error Handling**: All error conditions handled
- **Visual Quality**: All charts render correctly

---

**Note**: This testing strategy provides comprehensive coverage for the reporting system while maintaining efficiency and reliability. The strategy follows industry best practices and ensures high-quality, performant code that meets all requirements.
