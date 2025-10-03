"""Process manager for executing agents in isolated subprocesses with monitoring."""

import json
import logging
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

from agenthub.core.agents.dynamic_executor import DynamicAgentExecutor
from agenthub.runtime.environment_manager import EnvironmentManager

logger = logging.getLogger(__name__)


class ProcessManager:
    """Manages agent subprocess execution with isolation and real-time monitoring."""

    def __init__(
        self,
        timeout: int = 300,
        use_dynamic_execution: bool = True,
        monitoring: bool = False,
        realtime_communication: bool = True,
    ) -> None:
        """
        Initialize the process manager.

        Args:
            timeout: Maximum execution time in seconds
            use_dynamic_execution: Whether to use dynamic execution (default: True)
            monitoring: Whether to enable real-time monitoring (default: False)
            realtime_communication: Whether to enable WebSocket communication
                (default: True)
        """
        self.timeout = timeout
        self.environment_manager = EnvironmentManager()
        self.use_dynamic_execution = use_dynamic_execution
        self.dynamic_executor = (
            DynamicAgentExecutor() if use_dynamic_execution else None
        )
        self.monitoring = monitoring
        # Initialize monitoring components as None initially
        self.core_llm: Any = None
        self.llm_analyzer: Any = None
        self.log_streamer: Any = None
        self.terminal_display: Any = None

        # Real-time communication
        self.realtime_communication = realtime_communication
        self.communication_server: Any = None
        self._server_started = False

        # Initialize monitoring components if enabled
        if self.monitoring:
            try:
                from agenthub.core.llm.llm_service import get_shared_llm_service
                from agenthub.monitoring.llm_analyzer import LLMAnalyzer
                from agenthub.monitoring.log_streamer import LogStreamer
                from agenthub.monitoring.terminal_display import TerminalDisplay

                self.core_llm = get_shared_llm_service()
                self.llm_analyzer = LLMAnalyzer(self.core_llm)
                self.log_streamer = LogStreamer()
                self.terminal_display = TerminalDisplay()
                logger.info("Real-time monitoring components initialized")
            except ImportError as e:
                logger.warning(f"Monitoring components not available: {e}")
                self.monitoring = False

        # Try to initialize communication server if enabled
        if self.realtime_communication:
            logger.info("🔄 Initializing real-time communication server...")
            self._try_start_communication_server()
        else:
            logger.info(
                "📝 Real-time communication disabled - will use stdin/stdout fallback"
            )

    def set_monitoring(self, enabled: bool) -> None:
        """Enable or disable monitoring dynamically."""
        if enabled and not self.monitoring:
            try:
                from agenthub.core.llm.llm_service import get_shared_llm_service
                from agenthub.monitoring.llm_analyzer import LLMAnalyzer
                from agenthub.monitoring.log_streamer import LogStreamer
                from agenthub.monitoring.terminal_display import TerminalDisplay

                self.core_llm = get_shared_llm_service()
                self.llm_analyzer = LLMAnalyzer(self.core_llm)
                self.log_streamer = LogStreamer()
                self.terminal_display = TerminalDisplay()
                self.monitoring = True
                logger.info("Real-time monitoring enabled")
            except ImportError as e:
                logger.warning(f"Monitoring components not available: {e}")
                self.monitoring = False
        elif not enabled and self.monitoring:
            self.monitoring = False
            # Reset monitoring components to None
            self.core_llm = None
            self.llm_analyzer = None
            self.log_streamer = None
            self.terminal_display = None
            logger.info("Real-time monitoring disabled")

    def _try_start_communication_server(self) -> None:
        """Try to start communication server with graceful fallback."""
        try:
            # Check if WebSocket dependencies are available
            import websockets  # noqa: F401

            logger.debug("✅ WebSocket library available")

            # Import communication server
            from agenthub.core.communication import get_communication_server

            # Create server instance
            self.communication_server = get_communication_server()

            # Server will be started on first use (lazy initialization)
            logger.info("✅ Communication server initialized (lazy start)")
            logger.info(f"   📡 WebSocket port: {self.communication_server.port}")

        except ImportError as e:
            logger.warning(f"❌ WebSocket library not available: {e}")
            logger.info("📝 Falling back to stdin/stdout communication")
            self.realtime_communication = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize communication server: {e}")
            logger.info("📝 Falling back to stdin/stdout communication")
            self.realtime_communication = False

    async def _ensure_communication_server(self) -> bool:
        """
        Ensure communication server is running.

        Returns:
            bool: True if server available, False if fallback needed
        """
        if not self.realtime_communication:
            logger.debug("📝 Real-time communication disabled - using fallback")
            return False

        if self.communication_server is None:
            logger.debug("📝 Communication server not initialized - using fallback")
            return False

        # Try to start server if not running
        if not self.communication_server.is_running:
            logger.info("🚀 Starting WebSocket communication server...")
            success = await self.communication_server.start()
            if not success:
                logger.warning(
                    "❌ Communication server failed to start - using fallback"
                )
                return False
            logger.info(
                f"✅ WebSocket server started on port {self.communication_server.port}"
            )
        else:
            logger.debug(
                f"✅ WebSocket server running on port {self.communication_server.port}"
            )

        return True

    def _stream_agent_logs(
        self, process: subprocess.Popen, agent_path: str, method: str
    ) -> None:
        """
        Stream agent subprocess logs in real-time via WebSocket.

        Args:
            process: The subprocess running the agent
            agent_path: Path to the agent
            method: Method being executed
        """
        if not self.communication_server or not self.communication_server.is_running:
            return

        def stream_stdout() -> None:
            """Stream stdout logs."""
            try:
                for line in iter(process.stdout.readline, ""):
                    if line:
                        # Send log message via WebSocket
                        log_message = {
                            "type": "agent_log",
                            "agent_path": agent_path,
                            "method": method,
                            "stream": "stdout",
                            "message": line.strip(),
                            "timestamp": time.time(),
                        }

                        # Send log message only to this agent's session (not broadcast)
                        if hasattr(self.communication_server, "send_to_agent_sync"):
                            self.communication_server.send_to_agent_sync(
                                agent_path, log_message
                            )

                        logger.info(
                            f"📝 Agent stdout [{agent_path}.{method}]: {line.strip()}"
                        )
            except Exception as e:
                logger.warning(f"Error streaming stdout: {e}")

        def stream_stderr() -> None:
            """Stream stderr logs."""
            try:
                for line in iter(process.stderr.readline, ""):
                    if line:
                        # Send log message via WebSocket
                        log_message = {
                            "type": "agent_log",
                            "agent_path": agent_path,
                            "method": method,
                            "stream": "stderr",
                            "message": line.strip(),
                            "timestamp": time.time(),
                        }

                        # Send log message only to this agent's session (not broadcast)
                        if hasattr(self.communication_server, "send_to_agent_sync"):
                            self.communication_server.send_to_agent_sync(
                                agent_path, log_message
                            )

                        logger.warning(
                            f"⚠️ Agent stderr [{agent_path}.{method}]: {line.strip()}"
                        )
            except Exception as e:
                logger.warning(f"Error streaming stderr: {e}")

        # Start log streaming threads
        stdout_thread = threading.Thread(target=stream_stdout, daemon=True)
        stderr_thread = threading.Thread(target=stream_stderr, daemon=True)

        stdout_thread.start()
        stderr_thread.start()

        logger.info(f"📡 Started real-time log streaming for {agent_path}.{method}")

    def set_realtime_communication(self, enabled: bool) -> None:
        """Enable or disable real-time communication dynamically."""
        if enabled and not self.realtime_communication:
            logger.info("🔄 Enabling real-time communication...")
            self._try_start_communication_server()
            if self.communication_server is not None:
                self.realtime_communication = True
                logger.info("✅ Real-time communication enabled")
            else:
                logger.warning("❌ Failed to enable real-time communication")
        elif not enabled and self.realtime_communication:
            logger.info("🔄 Disabling real-time communication...")
            self.realtime_communication = False
            # Stop server if running
            if self.communication_server and self.communication_server.is_running:
                import asyncio

                try:
                    asyncio.create_task(self.communication_server.stop())
                    logger.info("🛑 WebSocket server stopped")
                except Exception as e:
                    logger.warning(f"❌ Error stopping communication server: {e}")
            logger.info(
                "📝 Real-time communication disabled - using stdin/stdout fallback"
            )

    def get_communication_status(self) -> dict[str, Any]:
        """Get communication server status."""
        if not self.realtime_communication:
            return {"enabled": False, "reason": "disabled"}

        if self.communication_server is None:
            return {"enabled": False, "reason": "not_initialized"}

        return {
            "enabled": True,
            "server_running": self.communication_server.is_running,
            "port": self.communication_server.port,
            "host": self.communication_server.host,
            "active_sessions": len(self.communication_server.agent_sessions),
        }

    def log_communication_status(self) -> None:
        """Log the current communication status for debugging."""
        status = self.get_communication_status()

        if status["enabled"]:
            logger.info("📡 COMMUNICATION STATUS: WebSocket Real-time Communication")
            logger.info(f"   ✅ Server running: {status['server_running']}")
            logger.info(f"   🌐 Host: {status['host']}")
            logger.info(f"   🔌 Port: {status['port']}")
            logger.info(f"   👥 Active sessions: {status['active_sessions']}")
        else:
            logger.info("📝 COMMUNICATION STATUS: stdin/stdout Fallback")
            logger.info(f"   ❌ Reason: {status['reason']}")

    def execute_agent(
        self,
        agent_path: str,
        method: str,
        parameters: dict[str, Any],
        manifest: dict[str, Any] | None = None,
        tool_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute an agent method in an isolated subprocess.

        Args:
            agent_path: Path to the agent directory
            method: Name of the method to execute
            parameters: Dictionary of method parameters
            manifest: Optional manifest data for dynamic execution

        Returns:
            dict: Execution result with 'result' or 'error' key

        Raises:
            ValueError: If agent_path or method is invalid
            RuntimeError: If subprocess creation fails
        """
        if not agent_path or not method:
            raise ValueError("agent_path and method are required")

        agent_dir = Path(agent_path)
        if not agent_dir.exists():
            raise ValueError(f"Agent directory does not exist: {agent_path}")

        # Determine agent script based on configuration
        agent_script = self._get_agent_script(agent_path)
        if not agent_script.exists():
            raise ValueError(f"Agent script not found: {agent_script}")

        # Register agent session if communication server is available
        session_registered = False
        if self.communication_server:
            # Try to ensure server is running
            import asyncio

            try:
                # Check if there's an event loop running
                try:
                    loop = asyncio.get_running_loop()
                    # If we get here, there's a running loop
                    logger.debug("📡 Event loop is running, scheduling server start")
                    asyncio.create_task(self._ensure_communication_server())
                except RuntimeError:
                    # No running loop, try to get or create one
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            logger.debug(
                                "📡 Event loop is running, scheduling server start"
                            )
                            asyncio.create_task(self._ensure_communication_server())
                        else:
                            logger.debug(
                                "📡 Event loop exists but not running, starting server"
                            )
                            loop.run_until_complete(self._ensure_communication_server())
                    except RuntimeError:
                        # No event loop at all, create a new one
                        logger.debug("📡 No event loop found, creating new one")
                        asyncio.run(self._ensure_communication_server())
            except Exception as e:
                logger.warning(f"Failed to start communication server: {e}")

            if self.communication_server.is_running:
                logger.info(f"📡 Registering WebSocket session: {agent_path}.{method}")
                self.communication_server.register_agent_session(
                    agent_path,
                    {
                        "method": method,
                        "parameters": parameters,
                        "start_time": time.time(),
                    },
                )
                session_registered = True
            else:
                logger.info(
                    f"📝 WebSocket not running - using fallback: {agent_path}.{method}"
                )
        else:
            logger.info(
                f"📝 No communication server - using fallback: {agent_path}.{method}"
            )

        try:
            # Try dynamic execution first if enabled
            if self.use_dynamic_execution and self.dynamic_executor:
                try:
                    start_time = time.time()
                    result = self.dynamic_executor.execute_agent_method(
                        agent_path, method, parameters, manifest
                    )
                    execution_time = time.time() - start_time
                    result["execution_time"] = execution_time

                    # Update session status
                    if session_registered:
                        logger.info(
                            f"✅ Agent completed - unregistering session: {agent_path}"
                        )
                        self.communication_server.unregister_agent_session(agent_path)

                    return result
                except Exception as e:
                    logger.warning(
                        f"Dynamic execution failed, falling back to subprocess: {e}"
                    )

            # Choose execution method based on monitoring setting
            if self.monitoring:
                result = self._execute_with_monitoring(
                    agent_path,
                    method,
                    parameters,
                    tool_context,
                    agent_script,
                    agent_dir,
                )
            else:
                result = self._execute_without_monitoring(
                    agent_path,
                    method,
                    parameters,
                    tool_context,
                    agent_script,
                    agent_dir,
                )

            # Update session status
            if session_registered:
                logger.info(f"✅ Agent completed - unregistering session: {agent_path}")
                self.communication_server.unregister_agent_session(agent_path)

            return result

        except Exception:
            # Update session status on error
            if session_registered:
                logger.warning(f"❌ Agent failed - unregistering session: {agent_path}")
                self.communication_server.unregister_agent_session(agent_path)
            raise

    def _execute_without_monitoring(
        self,
        agent_path: str,
        method: str,
        parameters: dict[str, Any],
        tool_context: dict[str, Any] | None,
        agent_script: Path,
        agent_dir: Path,
    ) -> dict[str, Any]:
        """Execute agent without monitoring (original subprocess execution)."""
        # Prepare execution data with tool context if available
        execution_data = {"method": method, "parameters": parameters}
        if tool_context:
            execution_data["tool_context"] = tool_context

        try:
            # Get Python executable for this agent's virtual environment
            python_executable = self.environment_manager.get_python_executable(
                agent_path
            )

            # Check if this is a Dana script being executed with Python
            if agent_script.suffix == ".na" and "python" in python_executable.lower():
                return {
                    "error": "Dana agent execution not supported",
                    "message": (
                        "Dana script cannot be executed with Python. "
                        "Dana runtime is required but not available in venv."
                    ),
                    "suggestion": (
                        "Install Dana runtime or use a Python-based agent instead."
                    ),
                }

            # Execute agent in subprocess with real-time log streaming
            start_time = time.time()
            logger.info(
                f"Executing agent in subprocess: {python_executable} "
                f"{str(agent_script)} '{json.dumps(execution_data)}'"
            )

            # Use Popen for real-time log streaming if WebSocket is available
            if self.communication_server and self.communication_server.is_running:
                logger.info(
                    f"📡 Starting agent with real-time streaming: {agent_path}.{method}"
                )
                process = subprocess.Popen(
                    [python_executable, str(agent_script), json.dumps(execution_data)],
                    cwd=str(agent_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,  # Line buffered
                    universal_newlines=True,
                )

                # Start log streaming
                self._stream_agent_logs(process, agent_path, method)

                # Wait for process to complete
                try:
                    process.wait(timeout=self.timeout)
                    execution_time = time.time() - start_time

                    # Get final output for result parsing
                    stdout, stderr = process.communicate()
                    result = subprocess.CompletedProcess(
                        process.args, process.returncode, stdout, stderr
                    )
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                    execution_time = time.time() - start_time
                    result = subprocess.CompletedProcess(
                        process.args,
                        -1,
                        "",
                        f"Process timed out after {self.timeout} seconds",
                    )
            else:
                # Fallback to original method without log streaming
                logger.info(
                    f"📝 Executing agent without log streaming: {agent_path}.{method}"
                )
                result = subprocess.run(
                    [python_executable, str(agent_script), json.dumps(execution_data)],
                    cwd=str(agent_dir),
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )
                execution_time = time.time() - start_time

            # Parse the result
            if result.returncode == 0:
                try:
                    parsed_result = json.loads(result.stdout)
                    if isinstance(parsed_result, dict):
                        parsed_result["execution_time"] = execution_time
                        return parsed_result
                    else:
                        return {
                            "error": "Agent returned non-dictionary result",
                            "raw_output": result.stdout,
                            "execution_time": execution_time,
                        }
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse agent output: {result.stdout}")
                    return {
                        "error": f"Invalid JSON response from agent: {e}",
                        "raw_output": result.stdout,
                        "execution_time": execution_time,
                    }
            else:
                # Agent execution failed
                error_msg = result.stderr or result.stdout or "Unknown error"
                return {
                    "error": f"Agent execution failed: {error_msg}",
                    "return_code": result.returncode,
                    "execution_time": execution_time,
                }

        except subprocess.TimeoutExpired:
            return {
                "error": f"Agent execution timed out after {self.timeout} seconds",
                "timeout": self.timeout,
            }
        except FileNotFoundError as e:
            raise RuntimeError(f"Failed to execute agent: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error executing agent: {e}")
            return {"error": f"Unexpected execution error: {e}"}

    def _execute_with_monitoring(
        self,
        agent_path: str,
        method: str,
        parameters: dict[str, Any],
        tool_context: dict[str, Any] | None,
        agent_script: Path,
        agent_dir: Path,
    ) -> dict[str, Any]:
        """Execute agent with real-time monitoring."""
        execution_data = self._prepare_execution_data(method, parameters, tool_context)

        try:
            command = self._prepare_monitoring_command(
                agent_path, agent_script, execution_data
            )
            start_time = self._start_monitoring_session(command, agent_dir)
            return_code, execution_time = self._monitor_execution(start_time)
            final_logs, final_analysis = self._finalize_monitoring(
                execution_time, return_code
            )

            return self._parse_monitoring_result(
                return_code, execution_time, final_logs, final_analysis
            )

        except Exception as e:
            logger.error(f"Unexpected error in monitored execution: {e}")
            return self._create_error_result(f"Unexpected execution error: {e}")

    def _prepare_execution_data(
        self,
        method: str,
        parameters: dict[str, Any],
        tool_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Prepare execution data with tool context."""
        execution_data = {"method": method, "parameters": parameters}
        if tool_context:
            execution_data["tool_context"] = tool_context
        return execution_data

    def _prepare_monitoring_command(
        self, agent_path: str, agent_script: Path, execution_data: dict[str, Any]
    ) -> list[str]:
        """Prepare command for monitored execution."""
        try:
            python_executable = self.environment_manager.get_python_executable(
                agent_path
            )
        except Exception:
            # Fallback to system Python if no virtual environment
            import sys

            python_executable = sys.executable

        command = [python_executable, str(agent_script), json.dumps(execution_data)]
        logger.info(f"Starting monitored execution: {' '.join(command)}")
        return command

    def _start_monitoring_session(self, command: list[str], agent_dir: Path) -> float:
        """Start the monitoring session with log streaming and terminal display."""
        # Clear logs from previous executions to prevent accumulation
        self.log_streamer.clear_logs()
        self.log_streamer.start_streaming(command, cwd=str(agent_dir))
        self.terminal_display.start_display()
        return time.time()

    def _monitor_execution(self, start_time: float) -> tuple[int, float]:
        """Monitor the execution with periodic log analysis."""
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
        return_code = self.log_streamer.wait_for_completion(timeout=self.timeout)
        execution_time = time.time() - start_time
        return return_code, execution_time

    def _finalize_monitoring(
        self, execution_time: float, return_code: int
    ) -> tuple[list[str], Any]:
        """Finalize monitoring session and get final analysis."""
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
        """Parse the monitoring result and return appropriate response."""
        if return_code == 0:
            return self._parse_successful_result(final_logs, execution_time)
        else:
            return self._parse_failed_result(final_analysis, execution_time)

    def _parse_successful_result(
        self, final_logs: list[str], execution_time: float
    ) -> dict[str, Any]:
        """Parse result from successful execution."""
        try:
            stdout_lines = [line for line in final_logs if "[STDOUT]" in line]
            if stdout_lines:
                result_text = self._extract_result_text(stdout_lines)
                parsed_result = json.loads(result_text)
                logger.debug("Successfully parsed JSON result")

                # The agent already returns the correct structure, add execution_time
                # to match non-monitoring format
                if isinstance(parsed_result, dict):
                    parsed_result["execution_time"] = execution_time
                    return parsed_result
                else:
                    return self._create_parse_error_result(
                        ValueError("Agent returned non-dictionary result"),
                        execution_time,
                    )
            else:
                return self._create_success_result(execution_time)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse agent output: {e}")
            return self._create_parse_error_result(e, execution_time)

    def _extract_result_text(self, stdout_lines: list[str]) -> str:
        """Extract and combine result text from stdout lines."""
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
        """Parse result from failed execution."""
        error_msg = "Agent execution failed"
        if final_analysis.errors:
            error_msg += f": {', '.join(final_analysis.errors)}"

        return {
            "status": "error",
            "summary": error_msg,
            "tools_used": [],
            "execution_time": execution_time,
        }

    def _create_success_result(self, execution_time: float) -> dict[str, Any]:
        """Create a simple success result structure."""
        return {
            "status": "completed",
            "summary": "Execution completed successfully",
            "tools_used": [],
            "execution_time": execution_time,
        }

    def _create_parse_error_result(
        self, error: Exception, execution_time: float
    ) -> dict[str, Any]:
        """Create an error result for JSON parsing failures."""
        return {
            "status": "error",
            "summary": f"Invalid JSON response from agent: {error}",
            "tools_used": [],
            "execution_time": execution_time,
        }

    def _create_error_result(self, error_msg: str) -> dict[str, Any]:
        """Create a generic error result."""
        return {
            "status": "error",
            "summary": error_msg,
            "tools_used": [],
            "execution_time": 0,
        }

    def validate_agent_structure(
        self, agent_path: str, require_venv: bool = True
    ) -> bool:
        """
        Validate that an agent has the required structure.

        Args:
            agent_path: Path to the agent directory
            require_venv: Whether to require virtual environment (default: True)

        Returns:
            True if agent structure is valid
        """
        agent_dir = Path(agent_path)

        # Check agent configuration to determine required files
        agent_config = self.environment_manager._get_agent_config(agent_path)

        # Always require agent.yaml or agent.yml
        agent_yaml_exists = (agent_dir / "agent.yaml").exists()
        agent_yml_exists = (agent_dir / "agent.yml").exists()

        if not agent_yaml_exists and not agent_yml_exists:
            logger.debug("Missing required file: agent.yaml (or agent.yml)")
            return False

        # Check for agent script file (either agent.py or agent.na)
        agent_py_exists = (agent_dir / "agent.py").exists()
        agent_na_exists = (agent_dir / "agent.na").exists()

        if agent_config and "dana_version" in agent_config:
            # For Dana agents, require agent.na
            if not agent_na_exists:
                logger.debug("Missing required file: agent.na (Dana agent)")
                return False
        else:
            # For Python agents or default, require agent.py
            if not agent_py_exists:
                logger.debug("Missing required file: agent.py (Python agent)")
                return False

        # Ensure only one agent script file exists
        if agent_py_exists and agent_na_exists:
            logger.debug("Both agent.py and agent.na found - only one should exist")
            return False

        # Check virtual environment only if required
        if require_venv:
            venv_path = self.environment_manager.get_agent_venv_path(agent_path)
            if not venv_path.exists():
                logger.debug(f"Missing virtual environment: {venv_path}")
                return False

            try:
                self.environment_manager.get_python_executable(agent_path)
                return True
            except RuntimeError:
                logger.debug("Python executable not found in virtual environment")
                return False

        return True

    def _get_agent_script(self, agent_path: str) -> Path:
        """
        Get the agent script path based on agent configuration.
        Supports both agent.py (Python) and agent.na (Dana).

        Args:
            agent_path: Path to the agent directory

        Returns:
            Path to the agent script file
        """
        agent_dir = Path(agent_path)

        # Check agent configuration to determine script type
        agent_config = self.environment_manager._get_agent_config(agent_path)

        if agent_config and "dana_version" in agent_config:
            # Use Dana script
            agent_script = agent_dir / "agent.na"
            logger.info(f"Using Dana script for agent: {agent_path}")
        else:
            # Default to Python script
            agent_script = agent_dir / "agent.py"
            logger.info(f"Using Python script for agent: {agent_path}")

        return agent_script
