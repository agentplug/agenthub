"""
Monitoring adapter module for optional real-time agent monitoring.

This module provides an adapter layer for optional monitoring components,
including LLM-based log analysis and terminal display.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MonitoringAdapter:
    """
    Adapter for optional monitoring components.

    Provides integration with LLM-based log analysis and real-time
    terminal display during agent execution. Gracefully handles
    missing dependencies.
    """

    def __init__(self, enabled: bool = False):
        """
        Initialize monitoring adapter.

        Args:
            enabled: Whether to enable monitoring (default: False)
        """
        self.enabled = enabled
        self.core_llm: Any = None
        self.llm_analyzer: Any = None
        self.log_streamer: Any = None
        self.terminal_display: Any = None

        if self.enabled:
            self._try_initialize_components()

    def _try_initialize_components(self) -> None:
        """Try to initialize monitoring components with graceful fallback."""
        try:
            from agenthub.core.llm.llm_service import get_shared_llm_service
            from agenthub.monitoring.llm_analyzer import LLMAnalyzer
            from agenthub.monitoring.log_streamer import LogStreamer
            from agenthub.monitoring.terminal_display import TerminalDisplay

            self.core_llm = get_shared_llm_service()
            self.llm_analyzer = LLMAnalyzer(self.core_llm)
            self.log_streamer = LogStreamer()
            self.terminal_display = TerminalDisplay()
            logger.info("✅ Real-time monitoring components initialized")
        except ImportError as e:
            logger.warning(f"❌ Monitoring components not available: {e}")
            logger.info("📝 Monitoring disabled - dependencies not installed")
            self.enabled = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize monitoring: {e}")
            self.enabled = False

    def enable(self) -> bool:
        """
        Enable monitoring.

        Returns:
            bool: True if enabled successfully
        """
        if self.enabled:
            logger.info("✅ Monitoring already enabled")
            return True

        logger.info("🔄 Enabling monitoring...")
        self._try_initialize_components()

        if self.core_llm is not None:
            self.enabled = True
            logger.info("✅ Monitoring enabled")
            return True
        else:
            logger.warning("❌ Failed to enable monitoring")
            return False

    def disable(self) -> None:
        """Disable monitoring."""
        if not self.enabled:
            logger.info("📝 Monitoring already disabled")
            return

        logger.info("🔄 Disabling monitoring...")
        self.enabled = False

        # Reset monitoring components
        self.core_llm = None
        self.llm_analyzer = None
        self.log_streamer = None
        self.terminal_display = None

        logger.info("📝 Monitoring disabled")

    def is_available(self) -> bool:
        """
        Check if monitoring is available.

        Returns:
            bool: True if monitoring components are available
        """
        return (
            self.enabled
            and self.core_llm is not None
            and self.llm_analyzer is not None
            and self.log_streamer is not None
            and self.terminal_display is not None
        )

    def execute_with_monitoring(
        self,
        command: list[str],
        agent_dir: Path,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """
        Execute agent with real-time monitoring.

        Args:
            command: Command to execute
            agent_dir: Agent directory for execution
            timeout: Maximum execution time in seconds

        Returns:
            dict: Execution result with monitoring data
        """
        if not self.is_available():
            return {
                "error": "Monitoring not available",
                "message": "Monitoring components not initialized",
            }

        try:
            start_time = self._start_monitoring_session(command, agent_dir)
            return_code, execution_time = self._monitor_execution(start_time, timeout)
            final_logs, final_analysis = self._finalize_monitoring(
                execution_time, return_code
            )

            return self._parse_monitoring_result(
                return_code, execution_time, final_logs, final_analysis
            )

        except Exception as e:
            logger.error(f"Unexpected error in monitored execution: {e}")
            return {
                "error": f"Unexpected execution error: {e}",
                "execution_time": 0,
            }

    def _start_monitoring_session(self, command: list[str], agent_dir: Path) -> float:
        """
        Start the monitoring session with log streaming and terminal display.

        Args:
            command: Command to execute
            agent_dir: Agent directory

        Returns:
            float: Start timestamp
        """
        # Clear logs from previous executions to prevent accumulation
        self.log_streamer.clear_logs()
        self.log_streamer.start_streaming(command, cwd=str(agent_dir))
        self.terminal_display.start_display()
        logger.info(f"📊 Started monitoring session: {' '.join(command)}")
        return time.time()

    def _monitor_execution(self, start_time: float, timeout: int) -> tuple[int, float]:
        """
        Monitor the execution with periodic log analysis.

        Args:
            start_time: Execution start time
            timeout: Maximum execution time

        Returns:
            tuple: (return_code, execution_time)
        """
        last_analysis_time = 0.0
        analysis_interval = 2.0  # Analyze logs every 2 seconds

        while not self.log_streamer.is_complete():
            current_time = time.time()
            new_logs = self.log_streamer.get_new_logs(0)

            # Analyze logs periodically
            if current_time - last_analysis_time >= analysis_interval and new_logs:
                try:
                    analysis = self.llm_analyzer.analyze(new_logs)
                    self.terminal_display.update_analysis(
                        analysis, len(self.log_streamer.get_logs())
                    )
                    last_analysis_time = current_time
                except Exception as e:
                    logger.warning(f"Log analysis failed: {e}")

            time.sleep(0.1)  # Small delay to prevent excessive CPU usage

        # Wait for process completion
        return_code = self.log_streamer.wait_for_completion(timeout=timeout)
        execution_time = time.time() - start_time
        return return_code, execution_time

    def _finalize_monitoring(
        self, execution_time: float, return_code: int
    ) -> tuple[list[str], Any]:
        """
        Finalize monitoring session and get final analysis.

        Args:
            execution_time: Total execution time
            return_code: Process return code

        Returns:
            tuple: (final_logs, final_analysis)
        """
        final_logs = self.log_streamer.get_logs()
        final_analysis = self.llm_analyzer.analyze(final_logs)

        # Stop monitoring components
        self.terminal_display.stop_display()
        self.log_streamer.stop_streaming()

        # Show final summary
        self.terminal_display.show_final_summary(
            final_analysis, len(final_logs), execution_time, return_code
        )

        return final_logs, final_analysis

    def _parse_monitoring_result(
        self,
        return_code: int,
        execution_time: float,
        final_logs: list[str],
        final_analysis: Any,
    ) -> dict[str, Any]:
        """
        Parse the monitoring result and return appropriate response.

        Args:
            return_code: Process return code
            execution_time: Total execution time
            final_logs: All collected logs
            final_analysis: LLM analysis result

        Returns:
            dict: Parsed result
        """
        if return_code == 0:
            return self._parse_successful_result(final_logs, execution_time)
        else:
            return self._parse_failed_result(final_analysis, execution_time)

    def _parse_successful_result(
        self, final_logs: list[str], execution_time: float
    ) -> dict[str, Any]:
        """
        Parse result from successful execution.

        Args:
            final_logs: All collected logs
            execution_time: Total execution time

        Returns:
            dict: Success result
        """
        try:
            stdout_lines = [line for line in final_logs if "[STDOUT]" in line]
            if stdout_lines:
                result_text = self._extract_result_text(stdout_lines)
                parsed_result = json.loads(result_text)
                logger.debug("Successfully parsed JSON result")

                if isinstance(parsed_result, dict):
                    parsed_result["execution_time"] = execution_time
                    return parsed_result
                else:
                    return {
                        "error": "Agent returned non-dictionary result",
                        "execution_time": execution_time,
                    }
            else:
                return {
                    "status": "completed",
                    "summary": "Execution completed successfully",
                    "execution_time": execution_time,
                }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse agent output: {e}")
            return {
                "error": f"Invalid JSON response from agent: {e}",
                "execution_time": execution_time,
            }

    def _extract_result_text(self, stdout_lines: list[str]) -> str:
        """
        Extract and combine result text from stdout lines.

        Args:
            stdout_lines: Lines containing [STDOUT] marker

        Returns:
            str: Extracted result text
        """
        result_text = ""
        for line in stdout_lines:
            if "[STDOUT]" in line:
                result_text += line.split("[STDOUT]")[-1].strip()
            else:
                result_text += line.strip()

        logger.debug(f"Attempting to parse JSON: {result_text[:200]}...")
        return result_text

    def _parse_failed_result(
        self, final_analysis: Any, execution_time: float
    ) -> dict[str, Any]:
        """
        Parse result from failed execution.

        Args:
            final_analysis: LLM analysis result
            execution_time: Total execution time

        Returns:
            dict: Error result
        """
        error_msg = "Agent execution failed"
        if hasattr(final_analysis, "errors") and final_analysis.errors:
            error_msg += f": {', '.join(final_analysis.errors)}"

        return {
            "error": error_msg,
            "execution_time": execution_time,
        }
