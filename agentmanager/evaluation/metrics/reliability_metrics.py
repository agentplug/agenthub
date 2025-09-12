"""
Reliability metrics for evaluation.
"""

from typing import List, Dict, Optional
from .base_metric import BaseMetric
from ..core.data_models import AgentOutput, EvaluationContext, MetricResult


class ReliabilityMetrics:
    """Reliability-related metric calculations."""
    
    @staticmethod
    def consistency_score(
        outputs: List[str], 
        similarity_threshold: float = 0.8
    ) -> float:
        """Calculate consistency across multiple outputs."""
        if len(outputs) < 2:
            return 1.0  # Single output is consistent with itself
        
        # Calculate pairwise similarity
        similarities = []
        for i in range(len(outputs)):
            for j in range(i + 1, len(outputs)):
                similarity = ReliabilityMetrics._calculate_similarity(outputs[i], outputs[j])
                similarities.append(similarity)
        
        if not similarities:
            return 1.0
        
        # Return average similarity
        return sum(similarities) / len(similarities)
    
    @staticmethod
    def stability_score(
        metric_values: List[float], 
        time_window: float
    ) -> float:
        """Calculate stability over time."""
        if len(metric_values) < 2:
            return 1.0
        
        # Calculate coefficient of variation (lower is more stable)
        mean_value = sum(metric_values) / len(metric_values)
        if mean_value == 0:
            return 1.0
        
        variance = sum((x - mean_value) ** 2 for x in metric_values) / len(metric_values)
        std_dev = variance ** 0.5
        coefficient_of_variation = std_dev / mean_value
        
        # Convert to stability score (1.0 = most stable, 0.0 = least stable)
        return max(0.0, 1.0 - coefficient_of_variation)
    
    @staticmethod
    def robustness_score(
        normal_outputs: List[str], 
        edge_case_outputs: List[str]
    ) -> float:
        """Calculate robustness under edge cases."""
        if not normal_outputs or not edge_case_outputs:
            return 0.5  # Cannot determine robustness
        
        # Calculate quality scores for normal and edge cases
        normal_quality = sum(ReliabilityMetrics._calculate_quality(output) for output in normal_outputs) / len(normal_outputs)
        edge_quality = sum(ReliabilityMetrics._calculate_quality(output) for output in edge_case_outputs) / len(edge_case_outputs)
        
        # Robustness is how well edge cases perform relative to normal cases
        if normal_quality == 0:
            return 0.0
        
        return min(1.0, edge_quality / normal_quality)
    
    @staticmethod
    def reproducibility_score(
        run1_results: List[float], 
        run2_results: List[float]
    ) -> float:
        """Calculate reproducibility between runs."""
        if len(run1_results) != len(run2_results) or len(run1_results) == 0:
            return 0.0
        
        # Calculate correlation coefficient (simplified)
        mean1 = sum(run1_results) / len(run1_results)
        mean2 = sum(run2_results) / len(run2_results)
        
        numerator = sum((x - mean1) * (y - mean2) for x, y in zip(run1_results, run2_results))
        
        sum_sq1 = sum((x - mean1) ** 2 for x in run1_results)
        sum_sq2 = sum((y - mean2) ** 2 for y in run2_results)
        
        denominator = (sum_sq1 * sum_sq2) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        correlation = numerator / denominator
        return max(0.0, correlation)  # Return positive correlation only
    
    @staticmethod
    def _calculate_similarity(text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        if not text1 or not text2:
            return 0.0
        
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def _calculate_quality(text: str) -> float:
        """Calculate basic quality score for text."""
        if not text:
            return 0.0
        
        # Simple quality heuristics
        quality_score = 0.0
        
        # Length check
        if 10 <= len(text) <= 1000:
            quality_score += 0.3
        
        # Sentence structure
        if '.' in text or '!' in text or '?' in text:
            quality_score += 0.3
        
        # No error indicators
        error_words = ['error', 'exception', 'failed', 'unable']
        if not any(word in text.lower() for word in error_words):
            quality_score += 0.4
        
        return min(1.0, quality_score)


class ConsistencyScoreMetric(BaseMetric):
    """Consistency score metric implementation."""
    
    def __init__(self, config=None, similarity_threshold: float = 0.8):
        """Initialize consistency score metric."""
        super().__init__(config)
        self.similarity_threshold = similarity_threshold
    
    def calculate(
        self, 
        agent_output: AgentOutput, 
        context: Optional[EvaluationContext] = None
    ) -> MetricResult:
        """Calculate consistency score."""
        if not self.validate_input(agent_output):
            raise ValueError("Invalid agent output for consistency score")
        
        # For single output, consistency is 1.0
        # In practice, this would be calculated across multiple outputs
        score = 1.0
        
        return MetricResult(
            metric_type="reliability",
            value=score,
            metadata={
                "similarity_threshold": self.similarity_threshold,
                "note": "Single output consistency"
            }
        )
    
    def validate_input(self, agent_output: AgentOutput) -> bool:
        """Validate input for consistency score calculation."""
        return (
            hasattr(agent_output, 'output_text') and 
            agent_output.output_text is not None
        )


class ErrorDetectionMetric(BaseMetric):
    """Error detection metric implementation."""
    
    def calculate(
        self, 
        agent_output: AgentOutput, 
        context: Optional[EvaluationContext] = None
    ) -> MetricResult:
        """Calculate error detection score."""
        if not self.validate_input(agent_output):
            raise ValueError("Invalid agent output for error detection")
        
        output_text = agent_output.output_text.lower()
        
        # Check for error indicators
        error_indicators = [
            'error', 'exception', 'failed', 'unable', 'cannot', 'sorry',
            'unfortunately', 'problem', 'issue', 'wrong', 'incorrect'
        ]
        
        has_error = any(indicator in output_text for indicator in error_indicators)
        score = 1.0 if has_error else 0.0
        
        return MetricResult(
            metric_type="reliability",
            value=score,
            metadata={
                "error_detected": has_error,
                "error_indicators_checked": len(error_indicators)
            }
        )
    
    def validate_input(self, agent_output: AgentOutput) -> bool:
        """Validate input for error detection calculation."""
        return (
            hasattr(agent_output, 'output_text') and 
            agent_output.output_text is not None
        )
