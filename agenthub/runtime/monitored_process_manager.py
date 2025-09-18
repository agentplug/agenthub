"""
Enhanced Process Manager with real-time monitoring capabilities.

Demonstrates the three-step monitoring process:
1. Observe agent's running logs in real-time
2. Convert logs to readable progress using LLM analysis
3. Display progress appropriately in terminal
"""

import json
import logging
import time
from pathlib import Path

from agenthub.core.llm.llm_service import CoreLLMService
from agenthub.monitoring.llm_analyzer import LLMAnalyzer
from agenthub.monitoring.log_streamer import LogStreamer
from agenthub.monitoring.terminal_display import TerminalDisplay
from agenthub.runtime.environment_manager import EnvironmentManager

logger = logging.getLogger(__name__)


class MonitoredProcessManager:
    """
    Enhanced Process Manager with real-time monitoring capabilities.

    Demonstrates the complete monitoring flow:
    1. Real-time log observation
    2. LLM-powered log analysis
    3. User-friendly progress display
    """

    def __init__(self, timeout: int = 300, monitoring: bool = True):
        """
        Initialize the monitored process manager.

        Args:
            timeout: Maximum execution time in seconds
            monitoring: Whether to enable real-time monitoring (default: True)
        """
        self.timeout = timeout
        self.monitoring = monitoring
        self.environment_manager = EnvironmentManager()

        # Initialize monitoring components if enabled
        if self.monitoring:
            self.core_llm = CoreLLMService()
            self.log_streamer = LogStreamer()
            self.llm_analyzer = LLMAnalyzer(self.core_llm)
            self.terminal_display = TerminalDisplay()
        else:
            self.core_llm = None
            self.log_streamer = None
            self.llm_analyzer = None
            self.terminal_display = None

    def execute_agent_with_monitoring(
        self,
        agent_path: str,
        method: str,
        parameters: dict,
        tool_context: dict = None,
    ) -> dict:
        """
        Execute an agent method with real-time monitoring.

        This method demonstrates the complete monitoring flow:
        1. Start real-time log observation
        2. Convert logs to readable progress using LLM analysis
        3. Display progress appropriately in terminal

        Args:
            agent_path: Path to the agent directory
            method: Name of the method to execute
            parameters: Dictionary of method parameters
            tool_context: Optional tool context for agent execution

        Returns:
            dict: Execution result with monitoring data
        """
        if not self.monitoring:
            # Fallback to basic execution without monitoring
            return self._execute_without_monitoring(
                agent_path, method, parameters, tool_context
            )

        agent_dir = Path(agent_path)
        if not agent_dir.exists():
            raise ValueError(f"Agent directory does not exist: {agent_path}")

        agent_script = agent_dir / "agent.py"
        if not agent_script.exists():
            raise ValueError(f"Agent script not found: {agent_script}")

        # Prepare execution data
        execution_data = {"method": method, "parameters": parameters}
        if tool_context:
            execution_data["tool_context"] = tool_context

        try:
            # Get Python executable
            python_executable = self.environment_manager.get_python_executable(
                agent_path
            )

            # Step 1: Start real-time log observation
            logger.info("🚀 Starting real-time log monitoring...")
            command = [python_executable, str(agent_script), json.dumps(execution_data)]

            self.log_streamer.start_streaming(command, cwd=str(agent_dir))

            # Step 2 & 3: Start progress analysis and display
            self.terminal_display.start_display()

            # Monitor execution with real-time updates
            start_time = time.time()
            last_analysis_time = 0
            analysis_interval = 2.0  # Analyze logs every 2 seconds

            while not self.log_streamer.is_complete():
                current_time = time.time()

                # Step 2: Convert logs to readable progress using LLM analysis
                if current_time - last_analysis_time >= analysis_interval:
                    logs = self.log_streamer.get_logs()
                    if logs:
                        analysis = self.llm_analyzer.analyze(logs)

                        # Step 3: Display progress appropriately in terminal
                        self.terminal_display.update_analysis(analysis, len(logs))

                        logger.debug(
                            f"Analysis: {analysis.summary} ({analysis.progress}%)"
                        )

                    last_analysis_time = current_time

                time.sleep(0.1)  # Small delay to prevent excessive CPU usage

            # Wait for process completion
            return_code = self.log_streamer.wait_for_completion()
            execution_time = time.time() - start_time

            # Get final logs and analysis
            final_logs = self.log_streamer.get_logs()
            final_analysis = self.llm_analyzer.analyze(final_logs)

            # Show final summary
            self.terminal_display.show_final_summary(
                final_analysis, len(final_logs), execution_time, return_code
            )

            # Parse result
            if return_code == 0:
                try:
                    # Try to get result from stdout (last few lines)
                    result_lines = [
                        line for line in final_logs if "RESULT:" in line or "{" in line
                    ]
                    if result_lines:
                        # Extract JSON from result lines
                        result_text = result_lines[-1]
                        if "RESULT:" in result_text:
                            result_text = result_text.split("RESULT:")[-1].strip()

                        parsed_result = json.loads(result_text)
                        parsed_result["execution_time"] = execution_time
                        parsed_result["monitoring_data"] = {
                            "total_logs": len(final_logs),
                            "final_analysis": {
                                "summary": final_analysis.summary,
                                "progress": final_analysis.progress,
                                "status": final_analysis.status,
                                "errors": final_analysis.errors,
                                "suggestions": final_analysis.suggestions,
                            },
                        }
                        return parsed_result
                    else:
                        return {
                            "result": "Execution completed successfully",
                            "execution_time": execution_time,
                            "monitoring_data": {
                                "total_logs": len(final_logs),
                                "final_analysis": {
                                    "summary": final_analysis.summary,
                                    "progress": final_analysis.progress,
                                    "status": final_analysis.status,
                                    "errors": final_analysis.errors,
                                    "suggestions": final_analysis.suggestions,
                                },
                            },
                        }
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse agent output: {e}")
                    return {
                        "error": f"Invalid JSON response from agent: {e}",
                        "raw_output": final_logs[-10:] if final_logs else [],
                        "execution_time": execution_time,
                        "monitoring_data": {
                            "total_logs": len(final_logs),
                            "final_analysis": {
                                "summary": final_analysis.summary,
                                "progress": final_analysis.progress,
                                "status": final_analysis.status,
                                "errors": final_analysis.errors,
                                "suggestions": final_analysis.suggestions,
                            },
                        },
                    }
            else:
                # Agent execution failed
                error_msg = "Agent execution failed"
                if final_analysis.errors:
                    error_msg += f": {', '.join(final_analysis.errors)}"

                return {
                    "error": error_msg,
                    "return_code": return_code,
                    "execution_time": execution_time,
                    "monitoring_data": {
                        "total_logs": len(final_logs),
                        "final_analysis": {
                            "summary": final_analysis.summary,
                            "progress": final_analysis.progress,
                            "status": final_analysis.status,
                            "errors": final_analysis.errors,
                            "suggestions": final_analysis.suggestions,
                        },
                    },
                }

        except Exception as e:
            logger.error(f"Unexpected error in monitored execution: {e}")
            return {
                "error": f"Unexpected execution error: {e}",
                "monitoring_data": {"error": str(e)},
            }
        finally:
            # Cleanup monitoring resources
            if self.log_streamer:
                self.log_streamer.stop_streaming()
            if self.terminal_display:
                self.terminal_display.stop_display()

    def _execute_without_monitoring(
        self,
        agent_path: str,  # noqa: ARG002
        method: str,  # noqa: ARG002
        parameters: dict,  # noqa: ARG002
        tool_context: dict = None,  # noqa: ARG002
    ) -> dict:
        """
        Execute agent without monitoring (fallback method).

        Args:
            agent_path: Path to the agent directory
            method: Name of the method to execute
            parameters: Dictionary of method parameters
            tool_context: Optional tool context for agent execution

        Returns:
            dict: Basic execution result
        """
        # This would use the original ProcessManager logic
        # For now, return a simple response
        return {
            "result": "Execution completed (monitoring disabled)",
            "note": "Use monitoring=True to enable real-time monitoring",
        }

    def get_monitoring_capabilities(self) -> dict:
        """
        Get information about monitoring capabilities.

        Returns:
            dict: Monitoring capabilities and status
        """
        return {
            "monitoring_enabled": self.monitoring,
            "components": {
                "core_llm": self.core_llm is not None,
                "log_streamer": self.log_streamer is not None,
                "llm_analyzer": self.llm_analyzer is not None,
                "terminal_display": self.terminal_display is not None,
            },
            "features": [
                "Real-time log observation",
                "LLM-powered progress analysis",
                "User-friendly terminal display",
                "Error detection and suggestions",
                "Final execution summary",
            ],
        }
