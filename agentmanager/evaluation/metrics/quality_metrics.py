"""
Quality metrics for evaluation.
"""

import re
from typing import List, Dict
from collections import Counter
from .base_metric import BaseMetric
from ..core.data_models import AgentOutput, EvaluationContext, MetricResult


class QualityMetrics:
    """Quality-related metric calculations."""
    
    @staticmethod
    def relevance_score(
        output: str, 
        input_text: str, 
        context: Optional[str] = None
    ) -> float:
        """Calculate relevance score of output to input."""
        if not input_text:
            return 0.0
        
        # Extract keywords from input
        input_keywords = set(QualityMetrics._extract_keywords(input_text))
        output_keywords = set(QualityMetrics._extract_keywords(output))
        
        if not input_keywords:
            return 0.0
        
        # Calculate keyword overlap
        overlap = len(input_keywords.intersection(output_keywords))
        return overlap / len(input_keywords)
    
    @staticmethod
    def completeness_score(
        output: str, 
        expected_elements: List[str]
    ) -> float:
        """Calculate completeness score based on expected elements."""
        if not expected_elements:
            return 1.0
        
        output_lower = output.lower()
        found_elements = sum(1 for element in expected_elements if element.lower() in output_lower)
        
        return found_elements / len(expected_elements)
    
    @staticmethod
    def coherence_score(output: str) -> float:
        """Calculate coherence score for text output."""
        if not output:
            return 0.0
        
        # Simple coherence heuristics
        sentences = re.split(r'[.!?]+', output)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 0.5  # Single sentence is somewhat coherent
        
        # Check for transition words
        transition_words = ['however', 'therefore', 'moreover', 'furthermore', 'additionally', 'also', 'but', 'and', 'so']
        has_transitions = any(word in output.lower() for word in transition_words)
        
        # Check for consistent tense (simplified)
        past_tense_words = ['was', 'were', 'had', 'did', 'went', 'came']
        present_tense_words = ['is', 'are', 'has', 'does', 'goes', 'comes']
        
        past_count = sum(1 for word in past_tense_words if word in output.lower())
        present_count = sum(1 for word in present_tense_words if word in output.lower())
        
        tense_consistency = 1.0 if (past_count == 0 or present_count == 0) else 0.5
        
        # Combine factors
        coherence = 0.3 + (0.3 if has_transitions else 0) + (0.4 * tense_consistency)
        return min(1.0, coherence)
    
    @staticmethod
    def clarity_score(output: str) -> float:
        """Calculate clarity and readability score."""
        if not output:
            return 0.0
        
        # Simple readability heuristics
        sentences = re.split(r'[.!?]+', output)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        # Average sentence length
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Word length distribution
        words = output.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Calculate clarity score (lower is better for readability)
        sentence_score = max(0, 1 - (avg_sentence_length - 10) / 20)  # Optimal around 10 words
        word_score = max(0, 1 - (avg_word_length - 4) / 6)  # Optimal around 4 characters
        
        return (sentence_score + word_score) / 2
    
    @staticmethod
    def factual_accuracy(
        output: str, 
        reference_facts: List[str]
    ) -> float:
        """Calculate factual accuracy against reference facts."""
        if not reference_facts:
            return 1.0  # No reference to check against
        
        output_lower = output.lower()
        correct_facts = 0
        
        for fact in reference_facts:
            if fact.lower() in output_lower:
                correct_facts += 1
        
        return correct_facts / len(reference_facts)
    
    @staticmethod
    def safety_score(output: str) -> float:
        """Calculate safety score for harmful content detection."""
        if not output:
            return 1.0
        
        # Simple harmful content detection
        harmful_indicators = [
            'hate', 'violence', 'harmful', 'dangerous', 'illegal',
            'threat', 'abuse', 'harassment', 'discrimination'
        ]
        
        output_lower = output.lower()
        harmful_count = sum(1 for indicator in harmful_indicators if indicator in output_lower)
        
        # Return safety score (1.0 = safe, 0.0 = harmful)
        return max(0.0, 1.0 - (harmful_count * 0.2))
    
    @staticmethod
    def _extract_keywords(text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could", "should"
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords


class RelevanceScoreMetric(BaseMetric):
    """Relevance score metric implementation."""
    
    def calculate(
        self, 
        agent_output: AgentOutput, 
        context: Optional[EvaluationContext] = None
    ) -> MetricResult:
        """Calculate relevance score."""
        if not self.validate_input(agent_output):
            raise ValueError("Invalid agent output for relevance score")
        
        output_text = agent_output.output_text
        input_text = agent_output.input_text
        
        score = QualityMetrics.relevance_score(output_text, input_text)
        
        return MetricResult(
            metric_type="quality",
            value=score,
            metadata={
                "input_length": len(input_text),
                "output_length": len(output_text)
            }
        )
    
    def validate_input(self, agent_output: AgentOutput) -> bool:
        """Validate input for relevance score calculation."""
        return (
            hasattr(agent_output, 'output_text') and 
            hasattr(agent_output, 'input_text') and
            agent_output.output_text is not None and
            agent_output.input_text is not None
        )


class CoherenceScoreMetric(BaseMetric):
    """Coherence score metric implementation."""
    
    def calculate(
        self, 
        agent_output: AgentOutput, 
        context: Optional[EvaluationContext] = None
    ) -> MetricResult:
        """Calculate coherence score."""
        if not self.validate_input(agent_output):
            raise ValueError("Invalid agent output for coherence score")
        
        output_text = agent_output.output_text
        score = QualityMetrics.coherence_score(output_text)
        
        return MetricResult(
            metric_type="quality",
            value=score,
            metadata={
                "output_length": len(output_text)
            }
        )
    
    def validate_input(self, agent_output: AgentOutput) -> bool:
        """Validate input for coherence score calculation."""
        return (
            hasattr(agent_output, 'output_text') and 
            agent_output.output_text is not None
        )
