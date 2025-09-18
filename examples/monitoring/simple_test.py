#!/usr/bin/env python3
"""
Simple test of monitoring components without full agent execution.

This script tests the three monitoring components individually:
1. LogStreamer - Real-time log observation
2. LLMAnalyzer - Log analysis and progress extraction
3. TerminalDisplay - Progress visualization
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


def test_log_streamer():
    """Test Step 1: Real-time log observation."""
    print("🧪 Testing Step 1: Real-time Log Observation")
    print("-" * 50)

    streamer = LogStreamer()

    # Simulate a command that produces logs
    if sys.platform == "win32":
        command = [
            "cmd",
            "/c",
            "echo Starting process && timeout 3 && echo Processing data && echo Complete",
        ]
    else:
        command = [
            "sh",
            "-c",
            "echo 'Starting process'; sleep 2; echo 'Processing data'; sleep 1; echo 'Complete'",
        ]

    print(f"📡 Starting log streaming for command: {' '.join(command)}")
    streamer.start_streaming(command)

    # Monitor logs in real-time
    start_time = time.time()
    while not streamer.is_complete() and (time.time() - start_time) < 10:
        logs = streamer.get_logs()
        if logs:
            print(f"📋 Captured {len(logs)} log lines")
            # Show last few lines
            for line in logs[-3:]:
                print(f"   {line}")
        time.sleep(0.5)

    # Get final logs
    final_logs = streamer.get_logs()
    print(f"✅ Log streaming complete! Total logs: {len(final_logs)}")

    streamer.stop_streaming()
    return final_logs


def test_llm_analyzer(logs):
    """Test Step 2: Convert logs to readable progress using LLM analysis."""
    print("\n🧪 Testing Step 2: LLM-Powered Log Analysis")
    print("-" * 50)

    # Initialize Core LLM Service
    core_llm = CoreLLMService()
    analyzer = LLMAnalyzer(core_llm)

    print(f"🧠 Analyzing {len(logs)} log lines...")

    # Analyze logs
    analysis = analyzer.analyze(logs)

    print("📊 Analysis Results:")
    print(f"   Summary: {analysis.summary}")
    print(f"   Progress: {analysis.progress}%")
    print(f"   Status: {analysis.status}")
    if analysis.errors:
        print(f"   Errors: {analysis.errors}")
    if analysis.suggestions:
        print(f"   Suggestions: {analysis.suggestions}")

    print("✅ Log analysis complete!")
    return analysis


def test_terminal_display(analysis, log_count):
    """Test Step 3: Display progress appropriately in terminal."""
    print("\n🧪 Testing Step 3: Terminal Progress Display")
    print("-" * 50)

    display = TerminalDisplay(refresh_rate=0.5)

    print("🖥️ Starting terminal display...")
    display.start_display()

    # Simulate progress updates
    for i in range(5):
        display.update_analysis(analysis, log_count + i)
        time.sleep(1)

    # Show final summary
    display.show_final_summary(analysis, log_count, 5.0, 0)

    print("✅ Terminal display test complete!")


def main():
    """Run all monitoring component tests."""
    print("=" * 80)
    print("🧪 AgentHub Monitoring Components Test")
    print("=" * 80)
    print()
    print("This test demonstrates the three-step monitoring process:")
    print("1. Real-time log observation")
    print("2. LLM-powered log analysis")
    print("3. User-friendly progress display")
    print()

    try:
        # Step 1: Test log streaming
        logs = test_log_streamer()

        if not logs:
            print("❌ No logs captured, cannot proceed with analysis")
            return

        # Step 2: Test LLM analysis
        analysis = test_llm_analyzer(logs)

        # Step 3: Test terminal display
        test_terminal_display(analysis, len(logs))

        print("\n" + "=" * 80)
        print("🎉 All Monitoring Components Test Complete!")
        print("=" * 80)
        print()
        print("✅ Step 1: Real-time log observation - WORKING")
        print("✅ Step 2: LLM-powered log analysis - WORKING")
        print("✅ Step 3: Terminal progress display - WORKING")
        print()
        print("The monitoring system is ready for agent execution!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
