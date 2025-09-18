"""
Enhanced terminal display for real-time agent monitoring

Provides dual display modes (incremental and fullscreen), interactive controls,
and better integration with the monitoring system.
"""

import os
import sys
import threading
import time
import shutil
from typing import Optional, Dict, Any

from agenthub.core.llm.llm_service import LogAnalysis
from .config import MonitoringConfig


class EnhancedTerminalDisplay:
    """
    Enhanced real-time terminal display for agent monitoring
    
    Supports dual display modes:
    - Incremental: Preserves terminal history, smooth updates
    - Fullscreen: Clean focused view, clears screen each update
    
    Also supports interactive controls and customization options.
    """

    def __init__(self, config: MonitoringConfig):
        """
        Initialize Enhanced Terminal Display
        
        Args:
            config: Monitoring configuration object
        """
        self.config = config
        self.refresh_rate = config.refresh_rate
        self.display_mode = config.display_mode
        self.interactive = config.interactive
        self.show_metrics = config.show_metrics
        self.show_timeline = config.show_timeline
        self.compact_mode = config.compact_mode
        
        # Display state
        self.is_displaying = False
        self.is_paused = False
        self.display_thread = None
        self._lock = threading.Lock()
        
        # Current data
        self.current_analysis = None
        self.log_count = 0
        self.start_time = None
        
        # For incremental mode
        self.last_rendered_state = {}
        self.terminal_height = 24
        self.terminal_width = 80
        self.cursor_position = (0, 0)
        
        # Interactive mode
        self.keyboard_thread = None
        self.filter_mode = "all"  # all, errors, warnings, custom
        self.search_term = ""
        
        # Metrics integration
        self.metrics_data = {}
        
        # Display modes
        self.display_modes = {
            'full': self._render_full_display,
            'compact': self._render_compact_display,
            'minimal': self._render_minimal_display
        }
        self.current_display_mode = 'full'

    def start_display(self):
        """Start real-time display updates"""
        if self.is_displaying:
            return

        self.is_displaying = True
        self.start_time = time.time()
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        self.display_thread.start()
        
        # Start interactive mode if enabled
        if self.interactive:
            self._start_interactive_mode()

    def stop_display(self):
        """Stop real-time display updates"""
        self.is_displaying = False
        if self.display_thread and self.display_thread.is_alive():
            self.display_thread.join(timeout=1)
        
        if self.keyboard_thread and self.keyboard_thread.is_alive():
            self.keyboard_thread.join(timeout=1)

    def update_analysis(self, analysis: LogAnalysis, log_count: int):
        """
        Update display with new analysis and log count
        
        Args:
            analysis: Latest log analysis result
            log_count: Total number of logs captured
        """
        with self._lock:
            self.current_analysis = analysis
            self.log_count = log_count

    def update_metrics(self, metrics_data: Dict[str, Any]):
        """
        Update display with metrics data
        
        Args:
            metrics_data: Dictionary containing metrics information
        """
        with self._lock:
            self.metrics_data = metrics_data

    def set_display_mode(self, mode: str):
        """Change display mode during runtime"""
        if mode in ["incremental", "fullscreen"]:
            self.display_mode = mode
            # Clear state when switching modes
            self.last_rendered_state = {}

    def _display_loop(self):
        """Main display update loop"""
        while self.is_displaying:
            if not self.is_paused:
                self._render_display()
            time.sleep(self.refresh_rate)

    def _render_display(self):
        """Render display using selected mode"""
        if self.display_mode == "incremental":
            self._render_incremental()
        else:
            self._render_fullscreen()

    def _render_incremental(self):
        """Incremental rendering - adds new content below existing content"""
        with self._lock:
            if not self.current_analysis:
                return

        # For incremental mode, we simply add new content below existing content
        # without clearing the screen or moving the cursor to the top
        
        # Only render if this is a new analysis (not the same as last time)
        current_state = {
            'status': self.current_analysis.status,
            'summary': self.current_analysis.summary,
            'log_count': self.log_count,
        }
        
        if hasattr(self, 'last_incremental_state') and self.last_incremental_state == current_state:
            return  # Nothing changed, don't render again
        
        self.last_incremental_state = current_state.copy()
        
        # Add a separator and new monitoring info
        print("\n" + "=" * 80)
        print("🤖 AgentHub Real-time Monitoring [INCREMENTAL]")
        print("=" * 80)
        
        # Render current status
        self._render_status_simple()
        
        # Render progress info
        self._render_progress_simple()
        
        # Render errors if any
        if self.current_analysis.errors:
            self._render_errors_simple()
        
        # Render suggestions if any
        if self.current_analysis.suggestions:
            self._render_suggestions_simple()
        
        # Render metrics if enabled
        if self.show_metrics and self.metrics_data:
            self._render_metrics_simple()
        
        print("=" * 80)
        sys.stdout.flush()

    def _render_status_simple(self):
        """Simple status rendering for incremental mode"""
        if self.current_analysis:
            status_emoji = self._get_status_emoji(self.current_analysis.status)
            print(f"📊 Status: {status_emoji} {self.current_analysis.status.upper()}")
            print(f"📝 Summary: {self.current_analysis.summary}")

    def _render_progress_simple(self):
        """Simple progress rendering for incremental mode"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        print(f"⏱️  Execution Time: {elapsed:.2f} seconds")
        print(f"📋 Total Logs: {self.log_count} lines")

    def _render_errors_simple(self):
        """Simple errors rendering for incremental mode"""
        if self.current_analysis.errors:
            print("❌ Errors:")
            for error in self.current_analysis.errors:
                print(f"   • {error}")

    def _render_suggestions_simple(self):
        """Simple suggestions rendering for incremental mode"""
        if self.current_analysis.suggestions:
            print("💡 Suggestions:")
            for suggestion in self.current_analysis.suggestions:
                print(f"   • {suggestion}")

    def _render_metrics_simple(self):
        """Simple metrics rendering for incremental mode"""
        if self.metrics_data:
            print("📊 Metrics:")
            for key, value in self.metrics_data.items():
                print(f"   • {key}: {value}")

    def _render_fullscreen(self):
        """Full-screen rendering - clears screen and redraws everything"""
        with self._lock:
            if not self.current_analysis:
                return

        # Clear screen and move cursor to top
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()
        
        # Use selected display mode
        render_method = self.display_modes[self.current_display_mode]
        render_method()
        
        sys.stdout.flush()

    def _calculate_updates_needed(self):
        """Calculate which sections need updating in incremental mode"""
        current_state = {
            'status': self.current_analysis.status,
            'summary': self.current_analysis.summary,
            'log_count': self.log_count,
            'errors': self.current_analysis.errors,
            'suggestions': self.current_analysis.suggestions,
            'metrics': self.metrics_data
        }
        
        updates_needed = {}
        for key, value in current_state.items():
            if self.last_rendered_state.get(key) != value:
                updates_needed[key] = True
            else:
                updates_needed[key] = False
        
        self.last_rendered_state = current_state.copy()
        return updates_needed

    def _render_full_display(self):
        """Full display with all information"""
        # Render header
        self._render_header()
        
        # Render controls info if interactive
        if self.interactive:
            self._render_controls_info()
        
        # Render main content
        self._render_progress()
        self._render_status()
        
        if self.show_metrics and self.metrics_data:
            self._render_metrics_section()
        
        if self.show_timeline:
            self._render_timeline_section()
        
        # Render filtered content
        self._render_filtered_content()
        
        # Render footer
        self._render_footer()

    def _render_compact_display(self):
        """Compact display with essential information only"""
        # Compact header
        elapsed = time.time() - self.start_time if self.start_time else 0
        status_text = "PAUSED" if self.is_paused else "RUNNING"
        print(f"🤖 AgentHub [{elapsed:.1f}s] {status_text}")
        
        # Compact status
        if self.current_analysis:
            status_emoji = self._get_status_emoji(self.current_analysis.status)
            print(f"{status_emoji} {self.current_analysis.status.upper()}: {self.current_analysis.summary}")
        
        # Compact metrics
        if self.show_metrics and self.metrics_data:
            print(f"📊 Metrics: {self._format_compact_metrics()}")

    def _render_minimal_display(self):
        """Minimal display with just status"""
        if self.current_analysis:
            status_emoji = self._get_status_emoji(self.current_analysis.status)
            print(f"{status_emoji} {self.current_analysis.summary}")

    def _render_header(self):
        """Render display header"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        elapsed_str = f"{elapsed:.1f}s"
        status_text = "PAUSED" if self.is_paused else "RUNNING"
        mode_text = f"[{self.display_mode.upper()}]"

        print("=" * 80)
        print(f"🤖 AgentHub Real-time Monitoring {mode_text} - {status_text} for {elapsed_str}")
        print("=" * 80)
        print()

    def _render_header_incremental(self):
        """Render header in incremental mode"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        elapsed_str = f"{elapsed:.1f}s"
        status_text = "PAUSED" if self.is_paused else "RUNNING"
        mode_text = f"[{self.display_mode.upper()}]"

        # Move to top and clear header lines
        sys.stdout.write("\033[1;1H")
        sys.stdout.write("\033[K")  # Clear line
        sys.stdout.write("=" * 80)
        sys.stdout.write("\n\033[K")  # Clear next line
        sys.stdout.write(f"🤖 AgentHub Real-time Monitoring {mode_text} - {status_text} for {elapsed_str}")
        sys.stdout.write("\n\033[K")  # Clear next line
        sys.stdout.write("=" * 80)
        sys.stdout.write("\n\033[K")  # Clear next line

    def _render_progress(self):
        """Render progress section"""
        if not self.current_analysis:
            return
            
        status_emoji = self._get_status_emoji(self.current_analysis.status)
        status = self.current_analysis.status

        print(f"🔄 Status: {status_emoji} {status.upper()}")
        print()

    def _render_progress_incremental(self):
        """Render progress section in incremental mode"""
        if not self.current_analysis:
            return
            
        # Move to progress line (line 4)
        sys.stdout.write("\033[4;1H")
        sys.stdout.write("\033[K")  # Clear line
        
        status_emoji = self._get_status_emoji(self.current_analysis.status)
        status = self.current_analysis.status
        progress_line = f"🔄 Status: {status_emoji} {status.upper()}"
        sys.stdout.write(progress_line)
        
        # Clear next line
        sys.stdout.write("\n\033[K")

    def _render_status(self):
        """Render status section"""
        if not self.current_analysis:
            return
            
        summary = self.current_analysis.summary
        print(f"📝 Activity: {summary}")
        print(f"📋 Logs: {self.log_count} lines captured")
        print()

    def _render_status_incremental(self):
        """Render status section in incremental mode"""
        if not self.current_analysis:
            return
            
        # Move to status lines (lines 5-6)
        sys.stdout.write("\033[5;1H")
        sys.stdout.write("\033[K")  # Clear line
        sys.stdout.write(f"📝 Activity: {self.current_analysis.summary}")
        
        sys.stdout.write("\n\033[K")  # Clear next line
        sys.stdout.write(f"📋 Logs: {self.log_count} lines captured")
        
        # Clear next line
        sys.stdout.write("\n\033[K")

    def _render_metrics_section(self):
        """Render metrics section"""
        if not self.metrics_data:
            return
            
        print("📊 REAL-TIME METRICS")
        print("=" * 50)
        
        # System metrics
        if 'system' in self.metrics_data:
            system = self.metrics_data['system']
            print(f"🖥️  CPU: {system.get('cpu_usage', 0):.1f}% | Memory: {system.get('memory_usage', 0):.1f}%")
        
        # Tool usage
        if 'tools' in self.metrics_data:
            tools = self.metrics_data['tools']
            print("🔧 TOOL USAGE:")
            for tool, stats in list(tools.items())[:5]:  # Top 5 tools
                success_rate = stats.get('success_rate', 0) * 100
                calls = stats.get('total_executions', 0)
                print(f"  {tool}: {calls} calls, {success_rate:.1f}% success")
        
        print()

    def _render_metrics_incremental(self):
        """Render metrics section in incremental mode"""
        if not self.metrics_data:
            return
            
        # This would be more complex in practice
        # For now, just render the full section
        self._render_metrics_section()

    def _render_errors(self):
        """Render errors section"""
        if not self.current_analysis or not self.current_analysis.errors:
            return
            
        print("❌ Errors Detected:")
        for i, error in enumerate(self.current_analysis.errors, 1):
            print(f"   {i}. {error}")
        print()

    def _render_errors_incremental(self):
        """Render errors section in incremental mode"""
        if not self.current_analysis or not self.current_analysis.errors:
            return
            
        # Find the line to start rendering errors
        # This is simplified - in practice would need to track line positions
        print("❌ Errors Detected:")
        for i, error in enumerate(self.current_analysis.errors, 1):
            print(f"   {i}. {error}")
        print()

    def _render_suggestions(self):
        """Render suggestions section"""
        if not self.current_analysis or not self.current_analysis.suggestions:
            return
            
        print("💡 Suggestions:")
        for i, suggestion in enumerate(self.current_analysis.suggestions, 1):
            print(f"   {i}. {suggestion}")
        print()

    def _render_suggestions_incremental(self):
        """Render suggestions section in incremental mode"""
        if not self.current_analysis or not self.current_analysis.suggestions:
            return
            
        print("💡 Suggestions:")
        for i, suggestion in enumerate(self.current_analysis.suggestions, 1):
            print(f"   {i}. {suggestion}")
        print()

    def _render_controls_info(self):
        """Render interactive controls information"""
        print("🎛️  Controls: [p]ause [f]ilter [s]earch [m]etrics [c]ompact [e]xport [h]elp [q]uit")
        print()

    def _render_filtered_content(self):
        """Render content based on current filter"""
        # This would integrate with log streaming
        # For now, just show a placeholder
        if self.filter_mode != "all":
            print(f"📋 Filter: {self.filter_mode.upper()}")
            if self.search_term:
                print(f"🔍 Search: {self.search_term}")
            print()

    def _render_timeline_section(self):
        """Render execution timeline"""
        print("⏰ EXECUTION TIMELINE")
        print("=" * 50)
        print("Timeline feature coming soon...")
        print()

    def _render_footer(self):
        """Render display footer"""
        print("-" * 80)
        if self.interactive:
            print("Press Ctrl+C to stop monitoring")
        else:
            print("Monitoring in progress...")
        print("-" * 80)

    def _update_terminal_size(self):
        """Get current terminal dimensions"""
        try:
            self.terminal_height, self.terminal_width = shutil.get_terminal_size()
        except:
            pass  # Keep defaults if detection fails

    def _clear_remaining_lines(self):
        """Clear leftover content from previous renders"""
        current_line = self._get_current_line_count()
        lines_to_clear = max(0, self.terminal_height - current_line)
        
        for _ in range(lines_to_clear):
            sys.stdout.write("\n\033[K")

    def _get_current_line_count(self) -> int:
        """Estimate current line count (simplified)"""
        # This is a simplified implementation
        # In practice, would need to track actual line positions
        return 10

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

    def _format_compact_metrics(self) -> str:
        """Format metrics for compact display"""
        if not self.metrics_data:
            return "No data"
        
        metrics = []
        if 'system' in self.metrics_data:
            system = self.metrics_data['system']
            cpu = system.get('cpu_usage', 0)
            memory = system.get('memory_usage', 0)
            metrics.append(f"CPU:{cpu:.0f}% MEM:{memory:.0f}%")
        
        if 'tools' in self.metrics_data:
            tools = self.metrics_data['tools']
            total_calls = sum(stats.get('total_executions', 0) for stats in tools.values())
            metrics.append(f"Tools:{total_calls}")
        
        return " | ".join(metrics)

    # Interactive mode methods
    def _start_interactive_mode(self):
        """Start interactive mode with keyboard controls"""
        self.keyboard_thread = threading.Thread(target=self._keyboard_listener, daemon=True)
        self.keyboard_thread.start()

    def _keyboard_listener(self):
        """Listen for keyboard input in a separate thread"""
        # This is a simplified implementation
        # In practice, would need proper terminal input handling
        pass

    def toggle_pause(self):
        """Toggle pause/resume"""
        self.is_paused = not self.is_paused
        status = "PAUSED" if self.is_paused else "RUNNING"
        self._show_status_message(f"Monitoring {status}")

    def cycle_filter_mode(self):
        """Cycle through filter modes"""
        filter_modes = ["all", "errors", "warnings", "custom"]
        current_index = filter_modes.index(self.filter_mode)
        self.filter_mode = filter_modes[(current_index + 1) % len(filter_modes)]
        self._show_status_message(f"Filter: {self.filter_mode.upper()}")

    def _show_status_message(self, message: str):
        """Show a temporary status message"""
        # Save cursor position
        sys.stdout.write("\033[s")
        
        # Move to bottom of screen
        sys.stdout.write("\033[999;1H")
        
        # Clear line and show message
        sys.stdout.write("\033[K")
        sys.stdout.write(f"ℹ️  {message}")
        
        # Restore cursor position
        sys.stdout.write("\033[u")
        sys.stdout.flush()
        
        # Clear message after 2 seconds
        threading.Timer(2.0, self._clear_status_message).start()

    def _clear_status_message(self):
        """Clear the status message"""
        sys.stdout.write("\033[999;1H\033[K")
        sys.stdout.flush()

    def show_final_summary(
        self,
        analysis: LogAnalysis,
        total_logs: int,
        execution_time: float,
        return_code: int,
    ):
        """
        Show final execution summary
        
        Args:
            analysis: Final log analysis
            total_logs: Total number of logs captured
            execution_time: Total execution time in seconds
            return_code: Process return code
        """
        self.stop_display()

        # For incremental mode, don't clear the screen - just add the final summary
        if self.display_mode == "incremental":
            print("\n" + "=" * 80)
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
        else:
            # For fullscreen mode, clear the screen and show final summary
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
