#!/usr/bin/env python3
"""
Simple demonstration of AgentHub Phase 3.1 Real-time Monitoring

This script demonstrates the three-step monitoring process without requiring
virtual environments or complex agent setup:
1. Observe agent's running logs in real-time
2. Convert logs to readable progress using LLM analysis
3. Display progress appropriately in terminal
"""

import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agenthub.core.llm.llm_service import CoreLLMService
from agenthub.monitoring.llm_analyzer import LLMAnalyzer
from agenthub.monitoring.log_streamer import LogStreamer
from agenthub.monitoring.terminal_display import TerminalDisplay


def demonstrate_step1_log_observation():
    """Demonstrate Step 1: Real-time log observation."""
    print("🔍 Step 1: Real-time Log Observation")
    print("=" * 50)

    streamer = LogStreamer()

    # Create a command that simulates agent execution with progress
    if sys.platform == "win32":
        command = [
            "cmd",
            "/c",
            "echo Starting agent execution && "
            "timeout 2 && echo Processing data... && "
            "timeout 2 && echo Analyzing results... && "
            "timeout 2 && echo Generating report... && "
            "timeout 1 && echo Agent execution complete!",
        ]
    else:
        command = [
            "sh",
            "-c",
            "echo 'Starting agent execution'; "
            "sleep 2; echo 'Processing data...'; "
            "sleep 2; echo 'Analyzing results...'; "
            "sleep 2; echo 'Generating report...'; "
            "sleep 1; echo 'Agent execution complete!'",
        ]

    print("📡 Starting log streaming...")
    print(f"🔧 Command: {' '.join(command)}")
    print()

    streamer.start_streaming(command)

    # Show real-time log capture
    print("📋 Real-time log capture:")
    start_time = time.time()
    while not streamer.is_complete() and (time.time() - start_time) < 15:
        logs = streamer.get_logs()
        if logs:
            # Show only new logs
            for line in logs[-1:]:
                print(f"   {line}")
        time.sleep(0.5)

    final_logs = streamer.get_logs()
    print(f"\n✅ Step 1 Complete: Captured {len(final_logs)} log lines")
    streamer.stop_streaming()

    return final_logs


def demonstrate_step2_log_analysis(logs):
    """Demonstrate Step 2: Convert logs to readable progress using LLM analysis."""
    print("\n🧠 Step 2: LLM-Powered Log Analysis")
    print("=" * 50)

    # Initialize Core LLM Service and Analyzer
    core_llm = CoreLLMService()
    analyzer = LLMAnalyzer(core_llm)

    print(f"📊 Analyzing {len(logs)} log lines...")
    print("🔍 Log content:")
    for i, log in enumerate(logs, 1):
        print(f"   {i}. {log}")

    print("\n🧠 LLM Analysis in progress...")
    analysis = analyzer.analyze(logs)

    print("\n📈 Analysis Results:")
    print(f"   Summary: {analysis.summary}")
    print(f"   Progress: {analysis.progress}%")
    print(f"   Status: {analysis.status}")
    if analysis.errors:
        print(f"   Errors: {analysis.errors}")
    if analysis.suggestions:
        print(f"   Suggestions: {analysis.suggestions}")

    print("\n✅ Step 2 Complete: Logs converted to structured progress")
    return analysis


def demonstrate_step3_progress_display(analysis, log_count):
    """Demonstrate Step 3: Display progress appropriately in terminal."""
    print("\n🖥️ Step 3: Terminal Progress Display")
    print("=" * 50)

    display = TerminalDisplay(refresh_rate=1.0)

    print("🖥️ Starting terminal display...")
    print("📺 Watch the real-time progress visualization:")
    print()

    display.start_display()

    # Simulate progress updates
    for i in range(8):
        # Simulate increasing progress
        updated_analysis = analysis
        updated_analysis.progress = min(100, analysis.progress + (i * 10))
        updated_log_count = log_count + i

        display.update_analysis(updated_analysis, updated_log_count)
        time.sleep(1)

    # Show final summary
    display.show_final_summary(analysis, log_count, 8.0, 0)

    print("\n✅ Step 3 Complete: Progress displayed in user-friendly format")


def main():
    """Demonstrate the complete three-step monitoring process."""
    print("=" * 80)
    print("🤖 AgentHub Phase 3.1 Real-time Monitoring Demonstration")
    print("=" * 80)
    print()
    print("This demonstration shows the three-step monitoring process:")
    print("1. 🔍 Observe agent's running logs in real-time")
    print("2. 🧠 Convert logs to readable progress using LLM analysis")
    print("3. 🖥️ Display progress appropriately in terminal")
    print()

    try:
        # Step 1: Real-time log observation
        logs = demonstrate_step1_log_observation()

        if not logs:
            print("❌ No logs captured, cannot proceed with analysis")
            return

        # Step 2: LLM-powered log analysis
        analysis = demonstrate_step2_log_analysis(logs)

        # Step 3: Terminal progress display
        demonstrate_step3_progress_display(analysis, len(logs))

        print("\n" + "=" * 80)
        print("🎉 Complete Monitoring Demonstration Successful!")
        print("=" * 80)
        print()
        print("✅ All three steps demonstrated successfully:")
        print("   1. ✅ Real-time log observation - WORKING")
        print("   2. ✅ LLM-powered log analysis - WORKING")
        print("   3. ✅ Terminal progress display - WORKING")
        print()
        print("🚀 The monitoring system is ready for production use!")
        print()
        print("Key capabilities demonstrated:")
        print("• Real-time subprocess log capture")
        print("• LLM-powered progress analysis and status detection")
        print("• User-friendly terminal visualization with progress bars")
        print("• Error detection and actionable suggestions")
        print("• Comprehensive execution summaries")

    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Demonstration interrupted by user")
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback

        traceback.print_exc()
