"""
LLM-based log analyzer for real-time agent monitoring

Uses the Core LLM Component to analyze agent execution logs and provide
structured insights about progress, errors, and suggestions.
"""

import json
from dataclasses import dataclass
from typing import Any

from agenthub.core.llm.llm_service import CoreLLMService


@dataclass
class LogAnalysis:
    """Data class for log analysis results in monitoring."""

    summary: str
    progress: int
    status: str
    errors: list[str]
    suggestions: list[str]


class LLMAnalyzer:
    """
    LLM-based log analyzer for agent execution monitoring

    Analyzes agent logs using the Core LLM Component to provide structured
    insights about what the agent is doing, progress estimation, error
    detection, and actionable suggestions.
    """

    def __init__(self, core_llm_service: CoreLLMService):
        """
        Initialize LLM Analyzer

        Args:
            core_llm_service: Core LLM service instance for log analysis
        """
        self.core_llm = core_llm_service
        self.cache: dict[str, Any] = {}
        self.log_analysis_prompt = self._get_log_analysis_prompt()

    def analyze(self, logs: list[str]) -> LogAnalysis:
        """
        Analyze agent execution logs using Core LLM Component

        Args:
            logs: List of log lines from agent execution

        Returns:
            Structured log analysis result
        """
        if not logs:
            return self._fallback_analysis([])

        log_text = "\n".join(logs)
        system_prompt = (
            "You are an expert at analyzing agent execution logs. "
            "Focus on identifying what the agent is doing, detecting "
            "errors, and providing actionable insights."
        )

        response = self.core_llm.generate(
            self.log_analysis_prompt.format(text=log_text),
            system_prompt=system_prompt,
            return_json=True,
        )
        return self._parse_log_analysis_response(response)

    def _get_log_analysis_prompt(self) -> str:
        """
        Get log analysis prompt template

        Returns:
            Prompt template for log analysis
        """
        return """
            Analyze these agent execution logs and provide a concise summary:

            {text}

            Please provide:
            1. What the agent is currently doing (max 20 words).
               You must answer the main thing agent is doing in a specific way,
               and say I'm instead of the agent is doing something.
            2. Any errors or issues detected
            3. Progress estimation (0-100%)
            4. Actionable suggestions if errors found

            Format as JSON:
            {{
                "summary": "...",
                "progress": 75,
                "status": "working",
                "errors": ["..."],
                "suggestions": ["..."]
            }}
        """

    def _parse_log_analysis_response(self, response: str) -> LogAnalysis:
        """
        Parse log analysis response from LLM

        Args:
            response: JSON response string from LLM

        Returns:
            Parsed LogAnalysis object
        """
        try:
            data = json.loads(response)
            return LogAnalysis(
                summary=data.get("summary", "Working..."),
                progress=data.get("progress", 0),
                status=data.get("status", "working"),
                errors=data.get("errors", []),
                suggestions=data.get("suggestions", []),
            )
        except (json.JSONDecodeError, TypeError):
            return self._fallback_analysis([])

    def _fallback_analysis(self, logs: list[str]) -> LogAnalysis:
        """
        Fallback analysis when LLM is not available

        Args:
            logs: List of log lines

        Returns:
            Basic log analysis using pattern matching
        """
        if not logs:
            return LogAnalysis("🔄 Starting...", 0, "starting", [], [])

        log_text = " ".join(logs).lower()

        error_words = ["error", "failed", "exception", "traceback"]
        if any(word in log_text for word in error_words):
            return LogAnalysis(
                "❌ Error detected", 0, "error", ["Error found"], ["Check logs"]
            )

        working_words = ["processing", "analyzing", "working", "executing"]
        if any(word in log_text for word in working_words):
            return LogAnalysis("📊 Processing...", 50, "working", [], [])

        complete_words = ["complete", "finished", "done", "success"]
        if any(word in log_text for word in complete_words):
            return LogAnalysis("✅ Complete", 100, "complete", [], [])

        starting_words = ["starting", "initializing", "loading"]
        if any(word in log_text for word in starting_words):
            return LogAnalysis("🚀 Starting...", 10, "starting", [], [])

        return LogAnalysis("🔄 Working...", 25, "working", [], [])
