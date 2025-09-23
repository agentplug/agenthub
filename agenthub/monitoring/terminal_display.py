"""
Terminal display for real-time agent monitoring

Provides real-time visualization of agent execution progress, logs, and analysis
results directly in the terminal with clean, user-friendly formatting.
"""

import sys
import threading
import time

from agenthub.core.llm.llm_service import LogAnalysis


class TerminalDisplay:
    """
    Real-time terminal display for agent monitoring

    Shows agent execution progress, logs, and analysis results in a clean,
    user-friendly format directly in the terminal.
    """

    def __init__(self, refresh_rate: float = 1.0) -> None:
        """
        Initialize Terminal Display

        Args:
            refresh_rate: How often to refresh display (seconds)
        """
        self.refresh_rate = refresh_rate
        self.is_displaying = False
        self.display_thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self.current_analysis: LogAnalysis | None = None
        self.log_count = 0
        self.start_time: float | None = None

    def start_display(self) -> None:
        """Start real-time display updates"""
        if self.is_displaying:
            return

        self.is_displaying = True
        self.start_time = time.time()
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        if self.display_thread:
            self.display_thread.start()

    def stop_display(self) -> None:
        """Stop real-time display updates"""
        self.is_displaying = False
        if self.display_thread and self.display_thread.is_alive():
            self.display_thread.join(timeout=1)

    def update_analysis(self, analysis: LogAnalysis, log_count: int) -> None:
        """
        Update display with new analysis and log count

        Args:
            analysis: Latest log analysis result
            log_count: Total number of logs captured
        """
        with self._lock:
            self.current_analysis = analysis
            self.log_count = log_count

    def _display_loop(self) -> None:
        """Main display update loop"""
        while self.is_displaying:
            self._render_display()
            time.sleep(self.refresh_rate)

    def _render_display(self) -> None:
        """Render the current display state"""
        with self._lock:
            if not self.current_analysis:
                return

        # Clear screen and move cursor to top
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

        # Render header
        self._render_header()

        # Render progress section
        self._render_progress()

        # Render status section
        self._render_status()

        # Render errors if any
        if self.current_analysis and self.current_analysis.errors:
            self._render_errors()

        # Render suggestions if any
        if self.current_analysis and self.current_analysis.suggestions:
            self._render_suggestions()

        # Render footer
        self._render_footer()

        sys.stdout.flush()

    def _render_header(self) -> None:
        """Render display header"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        elapsed_str = f"{elapsed:.1f}s"

        print("=" * 80)
        print(f"🤖 AgentHub Real-time Monitoring - Running for {elapsed_str}")
        print("=" * 80)
        print()

    def _render_progress(self) -> None:
        """Render status section without misleading progress bar"""
        if self.current_analysis:
            status_emoji = self._get_status_emoji(self.current_analysis.status)
            status = self.current_analysis.status
        else:
            status_emoji = "🔄"
            status = "unknown"

        print(f"🔄 Status: {status_emoji} {status.upper()}")
        print()

    def _render_status(self) -> None:
        """Render status section"""
        summary = (
            self.current_analysis.summary
            if self.current_analysis
            else "No analysis available"
        )

        print(f"📝 Activity: {summary}")
        print(f"📋 Logs: {self.log_count} lines captured")
        print()

    def _render_errors(self) -> None:
        """Render errors section"""
        print("❌ Errors Detected:")
        if self.current_analysis:
            for i, error in enumerate(self.current_analysis.errors, 1):
                print(f"   {i}. {error}")
        print()

    def _render_suggestions(self) -> None:
        """Render suggestions section"""
        print("💡 Suggestions:")
        if self.current_analysis:
            for i, suggestion in enumerate(self.current_analysis.suggestions, 1):
                print(f"   {i}. {suggestion}")
        print()

    def _render_footer(self) -> None:
        """Render display footer"""
        print("-" * 80)
        print("Press Ctrl+C to stop monitoring")
        print("-" * 80)

    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for status"""
        status_emojis = {
            "starting": "🚀",
            "working": "⚙️",
            "processing": "📊",
            "complete": "✅",
            "error": "❌",
            "warning": "⚠️",
        }
        return status_emojis.get(status, "🔄")

    def show_final_summary(
        self,
        analysis: LogAnalysis,
        total_logs: int,
        execution_time: float,
        return_code: int,
    ) -> None:
        """
        Show final execution summary

        Args:
            analysis: Final log analysis
            total_logs: Total number of logs captured
            execution_time: Total execution time in seconds
            return_code: Process return code
        """
        self.stop_display()

        # Clear screen
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

        print("=" * 80)
        print("🏁 AgentHub Execution Complete")
        print("=" * 80)
        print()

        # Execution summary
        status_emoji = "✅" if return_code == 0 else "❌"
        print(f"📊 Final Status: {status_emoji} {analysis.summary}")
        print(f"⏱️  Execution Time: {execution_time:.2f} seconds")
        print(f"📋 Total Logs: {total_logs} lines")
        print(f"🔢 Return Code: {return_code}")
        print()

        # Final analysis
        if analysis.errors:
            print("❌ Errors Found:")
            for i, error in enumerate(analysis.errors, 1):
                print(f"   {i}. {error}")
            print()

        if analysis.suggestions:
            print("💡 Recommendations:")
            for i, suggestion in enumerate(analysis.suggestions, 1):
                print(f"   {i}. {suggestion}")
            print()

        print("=" * 80)
        print("Monitoring session ended")
        print("=" * 80)
