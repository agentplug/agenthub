"""
LLM-based log analyzer for real-time agent monitoring

Uses the Core LLM Component to analyze agent execution logs and provide
structured insights about progress, errors, and suggestions.
"""

import json

from agenthub.core.llm.llm_service import CoreLLMService, LogAnalysis


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
        self.cache = {}
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

        # Filter out known non-error messages before analysis
        filtered_logs = []
        for log in logs:
            filtered_log = self._filter_non_error_messages(log.lower())
            if filtered_log.strip():  # Only keep non-empty logs after filtering
                filtered_logs.append(log)  # Keep original case for LLM analysis

        # Use filtered logs for analysis, but fallback to original if empty
        analysis_logs = filtered_logs if filtered_logs else logs
        log_text = "\n".join(analysis_logs)
        
        system_prompt = (
            "You are an expert at analyzing agent execution logs. "
            "Focus on identifying what the agent is doing, detecting "
            "real errors (not warnings or expected messages), and providing actionable insights. "
            "Ignore MCP discovery failures and tool warnings as these are expected behavior."
        )

        response = self.core_llm.analyze_text(
            log_text, self.log_analysis_prompt, system_prompt, return_json=True
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

            IMPORTANT: Only report REAL errors, not warnings or expected messages:
            - Ignore "MCP discovery failed" - this is expected for local tools
            - Ignore "warning:" messages from web tools - these are expected behavior
            - Ignore "unhandled errors in a TaskGroup" - this is expected for local tools
            - Only report actual execution failures, exceptions, or critical errors

            Please provide:
            1. What the agent is currently doing (max 50 characters)
            2. Any REAL errors or critical issues detected (not warnings)
            3. Progress estimation (0-100%)
            4. Actionable suggestions if real errors found

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

        # Filter out known non-error messages that should not trigger error detection
        filtered_log_text = self._filter_non_error_messages(log_text)

        error_words = ["error", "failed", "exception", "traceback"]
        if any(word in filtered_log_text for word in error_words):
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

    def _filter_non_error_messages(self, log_text: str) -> str:
        """
        Filter out known non-error messages that should not trigger error detection.
        
        Args:
            log_text: Raw log text to filter
            
        Returns:
            Filtered log text with non-error messages removed
        """
        # Remove MCP discovery failure warnings (these are expected for local tools)
        log_text = log_text.replace("mcp discovery failed", "")
        
        # Remove web tool warning messages (these are expected when no URL is provided)
        log_text = log_text.replace("warning:", "")
        log_text = log_text.replace("no url or content provided", "")
        log_text = log_text.replace("empty or invalid url provided", "")
        log_text = log_text.replace("both url and content provided", "")
        
        # Remove other common non-error messages
        log_text = log_text.replace("unhandled errors in a taskgroup", "")
        log_text = log_text.replace("mcp execution failed", "")
        
        return log_text
