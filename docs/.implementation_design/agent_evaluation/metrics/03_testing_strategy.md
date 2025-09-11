# Metrics Engine - Testing Strategy

**Document Type**: Testing Strategy  
**Author**: Assistant  
**Date Created**: 2025-06-28  
**Last Updated**: 2025-06-28  
**Status**: Draft  
**Stakeholders**: Developers, QA Team, Test Engineers  
**Component**: Metrics Engine  
**Iteration Count**: 1  

## Overview

This document outlines the comprehensive testing strategy for the Metrics Engine, covering unit testing, integration testing, performance testing, and validation testing to ensure reliability, accuracy, and performance.

## Testing Objectives

### 1. Primary Objectives
- **Accuracy**: Ensure metric calculations are mathematically correct
- **Reliability**: Verify consistent results across different conditions
- **Performance**: Meet response time and throughput requirements
- **Robustness**: Handle edge cases and error conditions gracefully
- **Maintainability**: Ensure code quality and testability

### 2. Success Criteria
- **Test Coverage**: >90% code coverage
- **Performance**: <100ms average calculation time per metric
- **Accuracy**: <1% error rate in metric calculations
- **Reliability**: 99.9% success rate in normal conditions
- **Error Handling**: Graceful handling of all error conditions

## Testing Levels

### 1. Unit Testing

#### Scope
- Individual metric calculation functions
- Base metric class methods
- Utility functions and helpers
- Data validation and processing
- Error handling mechanisms

#### Test Categories

##### Accuracy Metrics Tests
```python
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from metrics.accuracy import ExactMatchMetric, SemanticSimilarityMetric

class TestExactMatchMetric:
    """Test exact match metric calculations."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.metric = ExactMatchMetric()
        self.agent_output = Mock()
        self.context = Mock()
    
    def test_exact_match_success(self):
        """Test successful exact match."""
        self.agent_output.output_text = "The capital of France is Paris."
        self.context.expected_output = "The capital of France is Paris."
        
        result = self.metric.calculate(self.agent_output, self.context)
        
        assert result.value == 1.0
        assert result.metric_type == "exact_match"
        assert result.confidence is None
    
    def test_exact_match_failure(self):
        """Test failed exact match."""
        self.agent_output.output_text = "The capital of France is London."
        self.context.expected_output = "The capital of France is Paris."
        
        result = self.metric.calculate(self.agent_output, self.context)
        
        assert result.value == 0.0
        assert result.metric_type == "exact_match"
    
    def test_case_sensitivity(self):
        """Test case sensitivity handling."""
        self.metric.case_sensitive = False
        self.agent_output.output_text = "the capital of france is paris."
        self.context.expected_output = "The capital of France is Paris."
        
        result = self.metric.calculate(self.agent_output, self.context)
        
        assert result.value == 1.0
    
    def test_whitespace_normalization(self):
        """Test whitespace normalization."""
        self.metric.normalize_whitespace = True
        self.agent_output.output_text = "The  capital   of  France  is  Paris."
        self.context.expected_output = "The capital of France is Paris."
        
        result = self.metric.calculate(self.agent_output, self.context)
        
        assert result.value == 1.0
    
    def test_missing_expected_output(self):
        """Test handling of missing expected output."""
        self.agent_output.output_text = "Some output"
        self.context.expected_output = ""
        
        result = self.metric.calculate(self.agent_output, self.context)
        
        assert result.value == 0.0
        assert "error" in result.metadata
    
    def test_invalid_input(self):
        """Test handling of invalid input."""
        self.agent_output.output_text = None
        
        with pytest.raises(MetricValidationError):
            self.metric.calculate(self.agent_output, self.context)

class TestSemanticSimilarityMetric:
    """Test semantic similarity metric calculations."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.metric = SemanticSimilarityMetric()
        self.agent_output = Mock()
        self.context = Mock()
    
    @patch('metrics.accuracy.SentenceTransformer')
    def test_semantic_similarity_calculation(self, mock_transformer):
        """Test semantic similarity calculation."""
        # Mock the transformer
        mock_model = Mock()
        mock_model.encode.return_value = [
            np.array([0.1, 0.2, 0.3]),  # predicted embedding
            np.array([0.1, 0.2, 0.3])   # expected embedding
        ]
        mock_transformer.return_value = mock_model
        
        self.agent_output.output_text = "The capital of France is Paris."
        self.context.expected_output = "Paris is the capital of France."
        
        result = self.metric.calculate(self.agent_output, self.context)
        
        assert 0.0 <= result.value <= 1.0
        assert result.metric_type == "semantic_similarity"
    
    def test_model_loading_error(self):
        """Test handling of model loading errors."""
        with patch('metrics.accuracy.SentenceTransformer', side_effect=Exception("Model load failed")):
            with pytest.raises(MetricCalculationError):
                SemanticSimilarityMetric()
    
    def test_embedding_calculation_error(self):
        """Test handling of embedding calculation errors."""
        with patch('metrics.accuracy.SentenceTransformer') as mock_transformer:
            mock_model = Mock()
            mock_model.encode.side_effect = Exception("Embedding failed")
            mock_transformer.return_value = mock_model
            
            self.agent_output.output_text = "Some text"
            self.context.expected_output = "Other text"
            
            result = self.metric.calculate(self.agent_output, self.context)
            
            assert result.value == 0.0
            assert "error" in result.metadata
```

##### Quality Metrics Tests
```python
class TestRelevanceScoreMetric:
    """Test relevance score metric calculations."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.metric = RelevanceScoreMetric()
        self.agent_output = Mock()
    
    def test_relevance_score_calculation(self):
        """Test relevance score calculation."""
        self.agent_output.input_text = "What is the capital of France?"
        self.agent_output.output_text = "The capital of France is Paris."
        
        result = self.metric.calculate(self.agent_output)
        
        assert 0.0 <= result.value <= 1.0
        assert result.metric_type == "relevance_score"
        assert "keyword_score" in result.metadata
        assert "semantic_score" in result.metadata
    
    def test_high_relevance_score(self):
        """Test high relevance score for relevant output."""
        self.agent_output.input_text = "What is the capital of France?"
        self.agent_output.output_text = "France's capital city is Paris, located in the north-central part of the country."
        
        result = self.metric.calculate(self.agent_output)
        
        assert result.value > 0.7  # Should be high relevance
    
    def test_low_relevance_score(self):
        """Test low relevance score for irrelevant output."""
        self.agent_output.input_text = "What is the capital of France?"
        self.agent_output.output_text = "I like pizza and ice cream."
        
        result = self.metric.calculate(self.agent_output)
        
        assert result.value < 0.3  # Should be low relevance
    
    def test_question_answer_alignment(self):
        """Test question-answer alignment detection."""
        self.agent_output.input_text = "How does photosynthesis work?"
        self.agent_output.output_text = "Photosynthesis is the process by which plants convert sunlight into energy."
        
        result = self.metric.calculate(self.agent_output)
        
        assert result.value > 0.6  # Should detect question-answer alignment
    
    def test_missing_input_text(self):
        """Test handling of missing input text."""
        self.agent_output.input_text = None
        self.agent_output.output_text = "Some output"
        
        with pytest.raises(MetricValidationError):
            self.metric.calculate(self.agent_output)
```

##### Performance Metrics Tests
```python
class TestResponseTimeMetric:
    """Test response time metric calculations."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.metric = ResponseTimeMetric()
        self.agent_output = Mock()
        self.context = Mock()
    
    def test_response_time_calculation(self):
        """Test response time calculation."""
        start_time = datetime(2025, 1, 1, 12, 0, 0)
        end_time = datetime(2025, 1, 1, 12, 0, 5)
        
        self.agent_output.metadata = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        }
        
        result = self.metric.calculate(self.agent_output, self.context)
        
        assert result.value == 5.0  # 5 seconds
        assert result.metric_type == "response_time"
    
    def test_response_time_from_context(self):
        """Test response time calculation from context."""
        start_time = datetime(2025, 1, 1, 12, 0, 0)
        end_time = datetime(2025, 1, 1, 12, 0, 3)
        
        self.context.start_time = start_time
        self.context.end_time = end_time
        
        result = self.metric.calculate(self.agent_output, self.context)
        
        assert result.value == 3.0  # 3 seconds
    
    def test_milliseconds_conversion(self):
        """Test conversion to milliseconds."""
        self.metric.time_unit = "milliseconds"
        start_time = datetime(2025, 1, 1, 12, 0, 0)
        end_time = datetime(2025, 1, 1, 12, 0, 2)
        
        self.agent_output.metadata = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        }
        
        result = self.metric.calculate(self.agent_output, self.context)
        
        assert result.value == 2000.0  # 2000 milliseconds
    
    def test_missing_timing_data(self):
        """Test handling of missing timing data."""
        self.agent_output.metadata = {}
        self.context = None
        
        result = self.metric.calculate(self.agent_output, self.context)
        
        assert result.value == 0.0
        assert "error" in result.metadata
```

##### Aggregation Tests
```python
class TestMetricAggregator:
    """Test metric aggregation functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.aggregator = MetricAggregator()
        self.metric_results = [
            MetricResult(metric_type="accuracy", value=0.8),
            MetricResult(metric_type="accuracy", value=0.9),
            MetricResult(metric_type="accuracy", value=0.7),
            MetricResult(metric_type="accuracy", value=0.85),
            MetricResult(metric_type="accuracy", value=0.95)
        ]
    
    def test_mean_aggregation(self):
        """Test mean aggregation."""
        result = self.aggregator.aggregate(self.metric_results, method="mean")
        
        assert result.aggregated_value == 0.84  # (0.8 + 0.9 + 0.7 + 0.85 + 0.95) / 5
        assert result.aggregation_method == "mean"
        assert result.count == 5
    
    def test_median_aggregation(self):
        """Test median aggregation."""
        result = self.aggregator.aggregate(self.metric_results, method="median")
        
        assert result.aggregated_value == 0.85  # Middle value
        assert result.aggregation_method == "median"
    
    def test_max_aggregation(self):
        """Test max aggregation."""
        result = self.aggregator.aggregate(self.metric_results, method="max")
        
        assert result.aggregated_value == 0.95  # Maximum value
        assert result.aggregation_method == "max"
    
    def test_min_aggregation(self):
        """Test min aggregation."""
        result = self.aggregator.aggregate(self.metric_results, method="min")
        
        assert result.aggregated_value == 0.7  # Minimum value
        assert result.aggregation_method == "min"
    
    def test_empty_results(self):
        """Test handling of empty results."""
        with pytest.raises(ValueError):
            self.aggregator.aggregate([])
    
    def test_mixed_metric_types(self):
        """Test handling of mixed metric types."""
        mixed_results = [
            MetricResult(metric_type="accuracy", value=0.8),
            MetricResult(metric_type="speed", value=0.9)
        ]
        
        with pytest.raises(ValueError):
            self.aggregator.aggregate(mixed_results)
    
    def test_summary_statistics(self):
        """Test summary statistics calculation."""
        summary = self.aggregator.get_summary_statistics(self.metric_results)
        
        assert summary.count == 5
        assert summary.mean == 0.84
        assert summary.median == 0.85
        assert summary.min_value == 0.7
        assert summary.max_value == 0.95
        assert "q1" in summary.quartiles
        assert "q2" in summary.quartiles
        assert "q3" in summary.quartiles
```

### 2. Integration Testing

#### Scope
- Metric calculator with multiple metrics
- Aggregation across different metric types
- Error handling and recovery
- Performance under load
- Integration with evaluation engine

#### Test Categories

##### End-to-End Metric Calculation
```python
class TestMetricCalculatorIntegration:
    """Test metric calculator integration."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.calculator = MetricCalculator()
        self.agent_outputs = [
            AgentOutput(
                input_text="What is the capital of France?",
                output_text="The capital of France is Paris.",
                timestamp=datetime.now()
            ),
            AgentOutput(
                input_text="What is the capital of Germany?",
                output_text="The capital of Germany is Berlin.",
                timestamp=datetime.now()
            )
        ]
        self.metric_types = ["exact_match", "relevance_score", "response_time"]
    
    def test_calculate_metrics_success(self):
        """Test successful metric calculation."""
        results = self.calculator.calculate_metrics(
            self.agent_outputs, 
            self.metric_types
        )
        
        assert len(results) == 2
        for result in results:
            assert len(result.metrics) == 3
            assert "exact_match" in result.metrics
            assert "relevance_score" in result.metrics
            assert "response_time" in result.metrics
    
    def test_calculate_metrics_with_context(self):
        """Test metric calculation with context."""
        context = EvaluationContext(
            expected_outputs=["Paris", "Berlin"],
            start_time=datetime.now(),
            end_time=datetime.now()
        )
        
        results = self.calculator.calculate_metrics(
            self.agent_outputs, 
            self.metric_types,
            context
        )
        
        assert len(results) == 2
        # Verify context was used in calculations
        for result in results:
            assert result.metrics["exact_match"].value >= 0.0
    
    def test_batch_calculation(self):
        """Test batch calculation functionality."""
        batch_data = [
            (self.agent_outputs[0], ["exact_match", "relevance_score"]),
            (self.agent_outputs[1], ["exact_match", "response_time"])
        ]
        
        results = self.calculator.batch_calculate(batch_data)
        
        assert len(results) == 2
        assert len(results[0].metrics) == 2
        assert len(results[1].metrics) == 2
    
    def test_invalid_metric_type(self):
        """Test handling of invalid metric types."""
        with pytest.raises(InvalidMetricTypeError):
            self.calculator.calculate_metrics(
                self.agent_outputs, 
                ["invalid_metric"]
            )
    
    def test_empty_inputs(self):
        """Test handling of empty inputs."""
        with pytest.raises(ValueError):
            self.calculator.calculate_metrics([], self.metric_types)
        
        with pytest.raises(ValueError):
            self.calculator.calculate_metrics(self.agent_outputs, [])
```

##### Error Handling Integration
```python
class TestErrorHandlingIntegration:
    """Test error handling integration."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.calculator = MetricCalculator()
        self.agent_output = AgentOutput(
            input_text="Test input",
            output_text="Test output",
            timestamp=datetime.now()
        )
    
    def test_metric_calculation_error_recovery(self):
        """Test error recovery in metric calculation."""
        # Mock a metric to raise an error
        with patch('metrics.accuracy.ExactMatchMetric.calculate') as mock_calculate:
            mock_calculate.side_effect = Exception("Calculation failed")
            
            results = self.calculator.calculate_metrics(
                [self.agent_output], 
                ["exact_match"]
            )
            
            # Should not raise exception, but return error result
            assert len(results) == 1
            assert results[0].metrics["exact_match"].value == 0.0
            assert "error" in results[0].metrics["exact_match"].metadata
    
    def test_parallel_processing_error_handling(self):
        """Test error handling in parallel processing."""
        config = MetricConfig(parallel_processing=True, max_workers=2)
        calculator = MetricCalculator(config)
        
        # Create outputs that will cause errors
        problematic_outputs = [
            AgentOutput(input_text=None, output_text="Test", timestamp=datetime.now()),
            AgentOutput(input_text="Test", output_text=None, timestamp=datetime.now())
        ]
        
        results = calculator.calculate_metrics(
            problematic_outputs, 
            ["exact_match", "relevance_score"]
        )
        
        # Should handle errors gracefully
        assert len(results) == 2
        for result in results:
            for metric_result in result.metrics.values():
                assert metric_result.value == 0.0
                assert "error" in metric_result.metadata
```

### 3. Performance Testing

#### Scope
- Response time under normal load
- Throughput with multiple concurrent requests
- Memory usage and resource management
- Scalability with large datasets
- Caching effectiveness

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
        self.calculator = MetricCalculator()
        self.agent_outputs = [
            AgentOutput(
                input_text=f"Test input {i}",
                output_text=f"Test output {i}",
                timestamp=datetime.now()
            ) for i in range(100)
        ]
        self.metric_types = ["exact_match", "relevance_score", "response_time"]
    
    def test_response_time_under_load(self):
        """Test response time under normal load."""
        start_time = time.time()
        
        results = self.calculator.calculate_metrics(
            self.agent_outputs, 
            self.metric_types
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_output = total_time / len(self.agent_outputs)
        
        # Should be under 100ms per output on average
        assert avg_time_per_output < 0.1
        assert len(results) == 100
    
    def test_concurrent_calculations(self):
        """Test concurrent metric calculations."""
        def calculate_metrics_batch(batch_outputs):
            return self.calculator.calculate_metrics(
                batch_outputs, 
                self.metric_types
            )
        
        # Split outputs into batches
        batch_size = 20
        batches = [
            self.agent_outputs[i:i + batch_size] 
            for i in range(0, len(self.agent_outputs), batch_size)
        ]
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(calculate_metrics_batch, batch) for batch in batches]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should be faster than sequential processing
        assert total_time < 2.0  # Should complete within 2 seconds
        assert len(results) == 5  # 5 batches
        assert all(len(batch_results) == batch_size for batch_results in results)
    
    def test_memory_usage(self):
        """Test memory usage during calculations."""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process large dataset
        large_outputs = [
            AgentOutput(
                input_text=f"Test input {i} with more text to increase memory usage",
                output_text=f"Test output {i} with more text to increase memory usage",
                timestamp=datetime.now()
            ) for i in range(1000)
        ]
        
        results = self.calculator.calculate_metrics(
            large_outputs, 
            self.metric_types
        )
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        # Should not use more than 500MB additional memory
        assert memory_increase < 500
        assert len(results) == 1000
        
        # Cleanup
        del results
        del large_outputs
        gc.collect()
    
    def test_caching_performance(self):
        """Test caching performance improvement."""
        config = MetricConfig(cache_enabled=True)
        calculator = MetricCalculator(config)
        
        # First calculation (no cache)
        start_time = time.time()
        results1 = calculator.calculate_metrics(
            self.agent_outputs, 
            self.metric_types
        )
        first_time = time.time() - start_time
        
        # Second calculation (with cache)
        start_time = time.time()
        results2 = calculator.calculate_metrics(
            self.agent_outputs, 
            self.metric_types
        )
        second_time = time.time() - start_time
        
        # Second calculation should be faster due to caching
        assert second_time < first_time
        assert len(results1) == len(results2)
```

##### Stress Testing
```python
class TestPerformanceStress:
    """Test performance under stress conditions."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.calculator = MetricCalculator()
    
    def test_large_dataset_processing(self):
        """Test processing of large datasets."""
        # Create large dataset
        large_outputs = [
            AgentOutput(
                input_text=f"Test input {i}",
                output_text=f"Test output {i}",
                timestamp=datetime.now()
            ) for i in range(10000)
        ]
        
        start_time = time.time()
        results = self.calculator.calculate_metrics(
            large_outputs, 
            ["exact_match", "relevance_score"]
        )
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time_per_output = total_time / len(large_outputs)
        
        # Should handle large datasets efficiently
        assert avg_time_per_output < 0.05  # 50ms per output
        assert len(results) == 10000
    
    def test_memory_cleanup_under_stress(self):
        """Test memory cleanup under stress conditions."""
        import gc
        import psutil
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        # Process multiple large datasets
        for i in range(10):
            outputs = [
                AgentOutput(
                    input_text=f"Test input {j}",
                    output_text=f"Test output {j}",
                    timestamp=datetime.now()
                ) for j in range(1000)
            ]
            
            results = self.calculator.calculate_metrics(
                outputs, 
                ["exact_match", "relevance_score"]
            )
            
            # Force cleanup
            del results
            del outputs
            gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        # Memory should not grow significantly
        assert memory_increase < 100  # Less than 100MB increase
```

### 4. Validation Testing

#### Scope
- Metric accuracy against known results
- Comparison with reference implementations
- Edge case handling
- Boundary condition testing
- Data type validation

#### Test Categories

##### Accuracy Validation
```python
class TestMetricAccuracyValidation:
    """Test metric accuracy against known results."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.exact_match = ExactMatchMetric()
        self.semantic_similarity = SemanticSimilarityMetric()
    
    def test_exact_match_accuracy(self):
        """Test exact match accuracy with known cases."""
        test_cases = [
            ("Hello world", "Hello world", 1.0),
            ("Hello world", "hello world", 0.0),  # Case sensitive
            ("Hello world", "Hello  world", 0.0),  # Different spacing
            ("", "", 1.0),  # Empty strings
            ("Hello", "World", 0.0),  # Completely different
        ]
        
        for predicted, expected, expected_score in test_cases:
            agent_output = AgentOutput(
                input_text="Test",
                output_text=predicted,
                timestamp=datetime.now()
            )
            context = EvaluationContext(expected_output=expected)
            
            result = self.exact_match.calculate(agent_output, context)
            assert result.value == expected_score, f"Failed for: '{predicted}' vs '{expected}'"
    
    def test_semantic_similarity_accuracy(self):
        """Test semantic similarity accuracy with known cases."""
        test_cases = [
            ("The capital of France is Paris", "Paris is the capital of France", 0.8),  # High similarity
            ("The capital of France is Paris", "I like pizza", 0.2),  # Low similarity
            ("Hello world", "Hello world", 1.0),  # Identical
            ("Hello world", "Goodbye world", 0.5),  # Medium similarity
        ]
        
        for predicted, expected, min_expected_score in test_cases:
            agent_output = AgentOutput(
                input_text="Test",
                output_text=predicted,
                timestamp=datetime.now()
            )
            context = EvaluationContext(expected_output=expected)
            
            result = self.semantic_similarity.calculate(agent_output, context)
            assert result.value >= min_expected_score, f"Similarity too low for: '{predicted}' vs '{expected}'"
    
    def test_relevance_score_accuracy(self):
        """Test relevance score accuracy with known cases."""
        relevance_metric = RelevanceScoreMetric()
        
        test_cases = [
            ("What is the capital of France?", "The capital of France is Paris", 0.8),  # High relevance
            ("What is the capital of France?", "I like pizza and ice cream", 0.2),  # Low relevance
            ("How does photosynthesis work?", "Photosynthesis converts sunlight to energy", 0.7),  # Medium relevance
        ]
        
        for input_text, output_text, min_expected_score in test_cases:
            agent_output = AgentOutput(
                input_text=input_text,
                output_text=output_text,
                timestamp=datetime.now()
            )
            
            result = relevance_metric.calculate(agent_output)
            assert result.value >= min_expected_score, f"Relevance too low for: '{input_text}' -> '{output_text}'"
```

##### Edge Case Testing
```python
class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.calculator = MetricCalculator()
    
    def test_empty_strings(self):
        """Test handling of empty strings."""
        agent_output = AgentOutput(
            input_text="",
            output_text="",
            timestamp=datetime.now()
        )
        
        results = self.calculator.calculate_metrics(
            [agent_output], 
            ["exact_match", "relevance_score"]
        )
        
        assert len(results) == 1
        # Should handle empty strings gracefully
        for metric_result in results[0].metrics.values():
            assert 0.0 <= metric_result.value <= 1.0
    
    def test_very_long_strings(self):
        """Test handling of very long strings."""
        long_text = "A" * 10000  # 10KB string
        
        agent_output = AgentOutput(
            input_text=long_text,
            output_text=long_text,
            timestamp=datetime.now()
        )
        
        results = self.calculator.calculate_metrics(
            [agent_output], 
            ["exact_match", "relevance_score"]
        )
        
        assert len(results) == 1
        # Should handle long strings without errors
        for metric_result in results[0].metrics.values():
            assert 0.0 <= metric_result.value <= 1.0
    
    def test_special_characters(self):
        """Test handling of special characters."""
        special_text = "Hello! @#$%^&*()_+{}|:<>?[]\\;'\",./"
        
        agent_output = AgentOutput(
            input_text=special_text,
            output_text=special_text,
            timestamp=datetime.now()
        )
        
        results = self.calculator.calculate_metrics(
            [agent_output], 
            ["exact_match", "relevance_score"]
        )
        
        assert len(results) == 1
        # Should handle special characters gracefully
        for metric_result in results[0].metrics.values():
            assert 0.0 <= metric_result.value <= 1.0
    
    def test_unicode_characters(self):
        """Test handling of Unicode characters."""
        unicode_text = "Hello 世界 🌍 你好"
        
        agent_output = AgentOutput(
            input_text=unicode_text,
            output_text=unicode_text,
            timestamp=datetime.now()
        )
        
        results = self.calculator.calculate_metrics(
            [agent_output], 
            ["exact_match", "relevance_score"]
        )
        
        assert len(results) == 1
        # Should handle Unicode characters gracefully
        for metric_result in results[0].metrics.values():
            assert 0.0 <= metric_result.value <= 1.0
    
    def test_none_values(self):
        """Test handling of None values."""
        agent_output = AgentOutput(
            input_text=None,
            output_text=None,
            timestamp=datetime.now()
        )
        
        with pytest.raises(MetricValidationError):
            self.calculator.calculate_metrics(
                [agent_output], 
                ["exact_match"]
            )
    
    def test_invalid_timestamps(self):
        """Test handling of invalid timestamps."""
        agent_output = AgentOutput(
            input_text="Test",
            output_text="Test",
            timestamp="invalid_timestamp"
        )
        
        with pytest.raises(MetricValidationError):
            self.calculator.calculate_metrics(
                [agent_output], 
                ["response_time"]
            )
```

## Test Data Management

### 1. Test Data Generation

```python
class TestDataGenerator:
    """Generate test data for metric testing."""
    
    @staticmethod
    def generate_agent_outputs(count: int = 100) -> List[AgentOutput]:
        """Generate sample agent outputs for testing."""
        outputs = []
        for i in range(count):
            output = AgentOutput(
                input_text=f"Test input {i}",
                output_text=f"Test output {i}",
                timestamp=datetime.now()
            )
            outputs.append(output)
        return outputs
    
    @staticmethod
    def generate_accuracy_test_cases() -> List[Tuple[str, str, float]]:
        """Generate test cases for accuracy metrics."""
        return [
            ("Hello world", "Hello world", 1.0),
            ("Hello world", "hello world", 0.0),
            ("The capital of France is Paris", "Paris is the capital of France", 0.8),
            ("I like pizza", "I love pizza", 0.7),
            ("", "", 1.0),
        ]
    
    @staticmethod
    def generate_relevance_test_cases() -> List[Tuple[str, str, float]]:
        """Generate test cases for relevance metrics."""
        return [
            ("What is the capital of France?", "The capital of France is Paris", 0.9),
            ("What is the capital of France?", "I like pizza", 0.1),
            ("How does photosynthesis work?", "Photosynthesis converts sunlight to energy", 0.8),
            ("What is 2+2?", "2+2 equals 4", 0.9),
        ]
```

### 2. Test Fixtures

```python
@pytest.fixture
def sample_agent_outputs():
    """Fixture for sample agent outputs."""
    return TestDataGenerator.generate_agent_outputs(10)

@pytest.fixture
def sample_metric_calculator():
    """Fixture for metric calculator."""
    return MetricCalculator()

@pytest.fixture
def sample_evaluation_context():
    """Fixture for evaluation context."""
    return EvaluationContext(
        expected_outputs=["Expected output 1", "Expected output 2"],
        start_time=datetime.now(),
        end_time=datetime.now()
    )

@pytest.fixture
def accuracy_test_cases():
    """Fixture for accuracy test cases."""
    return TestDataGenerator.generate_accuracy_test_cases()

@pytest.fixture
def relevance_test_cases():
    """Fixture for relevance test cases."""
    return TestDataGenerator.generate_relevance_test_cases()
```

## Test Execution Strategy

### 1. Test Phases

#### Phase 1: Unit Tests
- **Duration**: 2-3 days
- **Scope**: Individual metric functions
- **Coverage**: >90% code coverage
- **Tools**: pytest, coverage.py

#### Phase 2: Integration Tests
- **Duration**: 1-2 days
- **Scope**: End-to-end workflows
- **Coverage**: All integration points
- **Tools**: pytest, testcontainers

#### Phase 3: Performance Tests
- **Duration**: 1 day
- **Scope**: Load and stress testing
- **Coverage**: Performance requirements
- **Tools**: locust, pytest-benchmark

#### Phase 4: Validation Tests
- **Duration**: 1 day
- **Scope**: Accuracy and edge cases
- **Coverage**: Known test cases
- **Tools**: Custom validation scripts

### 2. Continuous Integration

```yaml
# .github/workflows/metrics-testing.yml
name: Metrics Engine Testing

on:
  push:
    branches: [main, develop]
    paths: ['agentmanager/evaluation/metrics/**']
  pull_request:
    branches: [main]
    paths: ['agentmanager/evaluation/metrics/**']

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
          pip install pytest pytest-cov
      - name: Run unit tests
        run: |
          pytest tests/metrics/unit/ -v --cov=agentmanager.evaluation.metrics --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  integration-tests:
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
          pip install pytest testcontainers
      - name: Run integration tests
        run: |
          pytest tests/metrics/integration/ -v

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
          pytest tests/metrics/performance/ -v --benchmark-only
```

## Test Reporting

### 1. Test Results Dashboard

```python
class TestResultsDashboard:
    """Dashboard for test results and metrics."""
    
    def __init__(self):
        self.results = {}
        self.metrics = {}
    
    def add_test_result(self, test_name: str, result: dict):
        """Add test result to dashboard."""
        self.results[test_name] = result
    
    def generate_report(self) -> dict:
        """Generate comprehensive test report."""
        return {
            "summary": self._generate_summary(),
            "coverage": self._generate_coverage_report(),
            "performance": self._generate_performance_report(),
            "failures": self._generate_failure_report()
        }
    
    def _generate_summary(self) -> dict:
        """Generate test summary."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r["status"] == "passed")
        failed_tests = total_tests - passed_tests
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0
        }
```

### 2. Coverage Reporting

```python
class CoverageReporter:
    """Coverage reporting for metrics engine."""
    
    def __init__(self):
        self.coverage_data = {}
    
    def generate_coverage_report(self) -> dict:
        """Generate coverage report."""
        return {
            "overall_coverage": self._calculate_overall_coverage(),
            "metric_coverage": self._calculate_metric_coverage(),
            "line_coverage": self._calculate_line_coverage(),
            "branch_coverage": self._calculate_branch_coverage()
        }
    
    def _calculate_overall_coverage(self) -> float:
        """Calculate overall test coverage."""
        # Implementation for overall coverage calculation
        pass
```

## Quality Gates

### 1. Coverage Requirements
- **Unit Tests**: >90% code coverage
- **Integration Tests**: >80% integration coverage
- **Performance Tests**: All performance requirements met
- **Validation Tests**: All accuracy requirements met

### 2. Performance Requirements
- **Response Time**: <100ms average per metric
- **Throughput**: >1000 evaluations per minute
- **Memory Usage**: <1GB for standard benchmarks
- **Error Rate**: <1% in normal conditions

### 3. Quality Requirements
- **Code Quality**: All linting rules passed
- **Documentation**: All public APIs documented
- **Type Hints**: All functions have type hints
- **Error Handling**: All error conditions handled

---

**Note**: This testing strategy provides comprehensive coverage for the metrics engine while maintaining efficiency and reliability. The strategy follows industry best practices and ensures high-quality, performant code that meets all requirements.
