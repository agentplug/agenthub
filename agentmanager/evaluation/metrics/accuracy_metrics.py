"""
Accuracy metrics for evaluation.
"""

import difflib
from typing import Optional
from .base_metric import BaseMetric
from ..core.data_models import AgentOutput, EvaluationContext, MetricResult


class AccuracyMetrics:
    """Accuracy-related metric calculations."""
    
    @staticmethod
    def exact_match(
        predicted: str, 
        expected: str, 
        case_sensitive: bool = True
    ) -> float:
        """Calculate exact match score."""
        if not expected:
            return 0.0
        
        if case_sensitive:
            return 1.0 if predicted == expected else 0.0
        else:
            return 1.0 if predicted.lower() == expected.lower() else 0.0
    
    @staticmethod
    def partial_match(
        predicted: str, 
        expected: str, 
        threshold: float = 0.8
    ) -> float:
        """Calculate partial match score using sequence matching."""
        if not expected:
            return 0.0
        
        # Use difflib for sequence matching
        matcher = difflib.SequenceMatcher(None, predicted.lower(), expected.lower())
        ratio = matcher.ratio()
        
        return 1.0 if ratio >= threshold else ratio
    
    @staticmethod
    def keyword_overlap(
        predicted: str, 
        expected: str
    ) -> float:
        """Calculate keyword overlap score."""
        if not expected:
            return 0.0
        
        pred_words = set(predicted.lower().split())
        exp_words = set(expected.lower().split())
        
        if not exp_words:
            return 0.0
        
        overlap = len(pred_words.intersection(exp_words))
        return overlap / len(exp_words)
    
    @staticmethod
    def semantic_similarity(
        predicted: str, 
        expected: str
    ) -> float:
        """Calculate semantic similarity (simplified version)."""
        if not expected:
            return 0.0
        
        # Simple word-based similarity for now
        # In a full implementation, this would use embeddings
        pred_words = set(predicted.lower().split())
        exp_words = set(expected.lower().split())
        
        if not exp_words:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(pred_words.intersection(exp_words))
        union = len(pred_words.union(exp_words))
        
        return intersection / union if union > 0 else 0.0


class ExactMatchMetric(BaseMetric):
    """Exact match metric implementation."""
    
    def __init__(self, config=None, case_sensitive: bool = True):
        """Initialize exact match metric."""
        super().__init__(config)
        self.case_sensitive = case_sensitive
    
    def calculate(
        self, 
        agent_output: AgentOutput, 
        context: Optional[EvaluationContext] = None
    ) -> MetricResult:
        """Calculate exact match score."""
        if not self.validate_input(agent_output):
            raise ValueError("Invalid agent output for exact match")
        
        predicted = agent_output.output_text
        expected = context.expected_outputs[0] if context and context.expected_outputs else ""
        
        score = AccuracyMetrics.exact_match(predicted, expected, self.case_sensitive)
        
        return MetricResult(
            metric_type="accuracy",
            value=score,
            metadata={
                "case_sensitive": self.case_sensitive,
                "predicted_length": len(predicted),
                "expected_length": len(expected)
            }
        )
    
    def validate_input(self, agent_output: AgentOutput) -> bool:
        """Validate input for exact match calculation."""
        return (
            hasattr(agent_output, 'output_text') and 
            agent_output.output_text is not None
        )


class PartialMatchMetric(BaseMetric):
    """Partial match metric implementation."""
    
    def __init__(self, config=None, threshold: float = 0.8):
        """Initialize partial match metric."""
        super().__init__(config)
        self.threshold = threshold
    
    def calculate(
        self, 
        agent_output: AgentOutput, 
        context: Optional[EvaluationContext] = None
    ) -> MetricResult:
        """Calculate partial match score."""
        if not self.validate_input(agent_output):
            raise ValueError("Invalid agent output for partial match")
        
        predicted = agent_output.output_text
        expected = context.expected_outputs[0] if context and context.expected_outputs else ""
        
        score = AccuracyMetrics.partial_match(predicted, expected, self.threshold)
        
        return MetricResult(
            metric_type="accuracy",
            value=score,
            metadata={
                "threshold": self.threshold,
                "predicted_length": len(predicted),
                "expected_length": len(expected)
            }
        )
    
    def validate_input(self, agent_output: AgentOutput) -> bool:
        """Validate input for partial match calculation."""
        return (
            hasattr(agent_output, 'output_text') and 
            agent_output.output_text is not None
        )
